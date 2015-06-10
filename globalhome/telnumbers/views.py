# coding: utf-8
from django.utils.translation import ugettext_lazy as _, ugettext
from django.http import Http404, HttpResponseRedirect
from telnumbers.models import TelNumbersGroupNumbers
from lib.decorators import render_to, login_required
import log
from telnumbers.forms import TelNumberForm, ChangeTelNumberForm
from models import TelNumber, TelNumbersZakazy, TelNumbersGroup
from django.core.urlresolvers import reverse
from findocs.models import Package_on_connection_of_service
from findocs.views import create_package
from findocs import decorator_for_sign_applications
# from findocs import check_for_sign_applications
from django.conf import settings
import datetime, os, sys
from fsmanage.models import sip_registrations
from django.db import connections, transaction
from externalnumbers.models import ExternalNumber

@login_required
# @check_for_sign_applications([])
@render_to("phones/list.html")
def phones_list(request):

    if request.user.get_profile().is_card:
        raise Http404
    "Отображает список внутренних телефонных номеров пользователя"
    user = request.user
    profile = user.get_profile()
    if request.POST:
        try:
            if request.POST.get("submit_block"):
                numb = TelNumber.objects.get(tel_number=request.POST.get("submit_block"), account=profile.billing_account_id)
                numb.is_blocked_call = 1
                numb.save()
            elif request.POST.get("submit_unblock"):
                numb = TelNumber.objects.get(tel_number=request.POST.get("submit_unblock"), account=profile.billing_account_id)
                numb.is_blocked_call = 0
                numb.save()
            elif request.POST.get("submit_unreg"):
                #### delete registration
                try:
                    sipreg = sip_registrations.objects.get(sip_user=request.POST.get("submit_unreg"))
                    sipreg.delete()
                except sip_registrations.DoesNotExist, e:
                    pass
                # sipreg.delete()
        except TelNumber.DoesNotExist, e:
            raise Http404
    context = {}
    context["is_juridical"] = True
#    if not profile.is_juridical:
#        context["is_juridical"] = False
#        raise Http404
    bac = profile.billing_account
    context["profile"] = profile
    phones = []
    for p in bac.phones:
        number_zakaz_obj = TelNumbersZakazy.objects.get(number__id=p.id, status_number__id=1)
        if number_zakaz_obj.date_deactivation:
            if number_zakaz_obj.date_deactivation < datetime.datetime.now():
                continue
        phones.append({'id':p.id, 'tel_number':p.tel_number, 'person_name':p.person_name, 'internal_phone':p.internal_phone, \
                       'password':p.password, 'date_deactivation':number_zakaz_obj.date_deactivation, 'is_blocked_call':p.is_blocked_call, \
                       'registered':sip_registrations.objects.filter(sip_user=p.tel_number)})
    context["phones"] = phones
    context["title"] = _(u"Internal numbers")
    context["current_view_name"] = "account_phones_list"
    #
    cur = connections[settings.BILLING_DB].cursor()
    cur.execute("SELECT id FROM billservice_account WHERE assigned_to=%s;", (profile.billing_account_id,))
    qwe = cur.fetchall()
    l = []
    for qw in qwe:
        cur.execute("SELECT * FROM internal_numbers WHERE account_id=%s;", (qw,))
        www = cur.fetchall()
#        context["fixed_users"] = www
        l.append(www)
    transaction.commit_unless_managed(settings.BILLING_DB)
    context["fixed_users"] = l
    return context

@login_required
# @check_for_sign_applications([])
@render_to("phones/edit.html")
def account_phone_edit(request, tel_number_id):

    if request.user.get_profile().is_card:
        raise Http404
    "Редактирование выбранного номера"
    user = request.user
    profile = user.get_profile()
#    if not profile.is_juridical:
#        raise Http404
    bac = profile.billing_account
    context = {}
    context["current_view_name"] = "account_phones_list"
    try:
        phone = TelNumber.objects.get(id=tel_number_id)
    except Exception, e:
        log.add("Exception 1 in telnumbers.views.account_phone_edit: '%s'" % e)
        raise e

    if request.POST:
        if request.POST.get("save"):
            form = ChangeTelNumberForm(request.POST.copy(), billing_account=profile.billing_account)
            if form.is_valid():
                # а вот тут какраз и сохраняем телефон
                phone.password = form.cleaned_data["password"]
                phone.internal_phone = form.cleaned_data["internal_phone"]
                phone.person_name = form.cleaned_data["person_name"]
                phone.save()
                request.notifications.add(_(u"Phone was changed succesfully"), "success")
                return HttpResponseRedirect("../")
        else:
            return HttpResponseRedirect("../")
    else:
        form = ChangeTelNumberForm(instance=phone, billing_account=profile.billing_account)

    context["form"] = form
    context["title"] = _(u"Editing a phone number %s") % phone
    return context

@login_required
@render_to("phones/add.html")
@decorator_for_sign_applications()
def account_phone_add(request):
#    else:
#        return HttpResponseRedirect(reverse('account_phone_add'))
    if request.user.get_profile().is_card:
        raise Http404
    "Добавление номера"
    user = request.user
    profile = user.get_profile()
#    if not profile.is_juridical:
#        raise Http404
    bac = profile.billing_account
    context = {}
    context["current_view_name"] = "account_phones_list"


    '''
    if profile.is_hostel:
        from common import pwgen
        for qw in xrange(100):
            next_number = TelNumber.get_next_free_number(profile.is_hostel, profile.is_juridical)
            context["next_number"] = next_number
            password1 = pwgen.random_pwd()
            next_number_r = str(next_number)
            internal_phone = "%s" % next_number_r[0] + "%s" % next_number_r[4:]
            number = TelNumber.create(
                    bac,
                    next_number = next_number,
                    is_juridical = profile.is_juridical,
                    password = password1,
                    person_name = next_number,
                    internal_phone = int(internal_phone),
                )
        request.notifications.add(_(u"Number was succesfully added."), "success")
        return HttpResponseRedirect("../")
    '''


    next_number = TelNumber.get_next_free_number(profile.is_hostel, profile.is_juridical)
    context["next_number"] = next_number
    try:
        package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
        data_temp = eval(package_obj.data)
        request.POST = data_temp
        package_obj.activate = True
        package_obj.save()
    except Package_on_connection_of_service.DoesNotExist:
        pass
    if request.POST:
        if request.POST.get("add"):
            form = TelNumberForm(request.POST.copy(), billing_account=profile.billing_account)
            if form.is_valid():
                request_post = {}
                for key, value in request.POST.iteritems():
                    request_post[key] = value
                successfully_create = create_package(request.user, \
                    reverse('account_phone_add'), \
                    reverse('account_phones_list'), \
                    '%s' % request_post, \
                    ['telematic_services_contract'])
                if successfully_create:
                    return HttpResponseRedirect(reverse('account_phone_add'))
                # а вот тут какраз и сохраняем телефон
                number_obj = TelNumber.create(
                    bac,
                    next_number=next_number,
                    is_juridical=profile.is_juridical,
                    password=form.cleaned_data["password"],
                    person_name=form.cleaned_data["person_name"],
                    internal_phone=form.cleaned_data["internal_phone"],
                )
                request.notifications.add(_(u"Number was succesfully added."), "success")
                return HttpResponseRedirect("../")
        else:
            return HttpResponseRedirect("../")
    else:
        form = TelNumberForm(billing_account=profile.billing_account)

    context["form"] = form
    context["title"] = _(u"Adding a number %s") % next_number
    return context


@login_required
@render_to("phones/delete.html")
def account_phone_delete(request, tel_number_id):
    if request.user.get_profile().is_card:
        raise Http404
    "Удаление номера"
    user = request.user
    profile = user.get_profile()
    bac = profile.billing_account
    context = {}
    number_obj = TelNumber.objects.get(id=tel_number_id)
    number_zakaz_qs = TelNumbersZakazy.objects.filter(number__id=tel_number_id, status_number__id=1)
    if number_zakaz_qs:
        number_zakaz_obj = number_zakaz_qs[0]
    else:
        raise Http404
    if number_zakaz_obj.bill_account != bac:
        raise Http404
    context['title'] = u'Удаление номера %s' % number_obj.tel_number
    context["current_view_name"] = "account_phones_list"
    context['number'] = number_obj.tel_number
    spis_group = []
    groups_queryset = TelNumbersGroup.objects.filter(numbers__id=tel_number_id)
    for group_obj in groups_queryset:
        if len(group_obj.numbers.all()) == 1:
            spis_group.append(group_obj)
    context['spis_group'] = spis_group
    if request.POST.get('delete'):
        for group_obj in groups_queryset:
            if len(group_obj.numbers.all()) == 1:
                ext_queryset = ExternalNumber.objects.filter(phone_numbers_group=group_obj.id)
                for ext_number in ext_queryset:
                    ext_number.phone_numbers_group = None
                    ext_number.save()
                group_obj.delete()
            else:
                group_obj.numbers.remove(number_obj)
        number_obj.account, number_obj.password, number_obj.internal_phone, number_obj.person_name = None, None, None, None
        number_obj.save()
        number_zakaz_obj.date_deactivation = datetime.datetime.now()
        number_zakaz_obj.status_number_id = 2
        number_zakaz_obj.save()
        request.notifications.add(u'Номер успешно удален', 'success')
        return HttpResponseRedirect(reverse('account_phones_list'))
    elif request.POST.get('cancel'):
        return HttpResponseRedirect(reverse('account_phones_list'))
    return context


@login_required
@render_to('phones/statistics.html')
def account_phone_statistics(request, tel_number_id):
    import math
    from lib.paginator import SimplePaginator
    from billing.models import BillservicePhoneTransaction, BillserviceSubAccount
    from account.forms import BalanceFilterForm, first_date, last_date
    from account.views import RQ2QS
    from datetime import timedelta
    from django.db.models import Q
    from django.db import connection
    from fs.models import Record_talk_activated_tariff
    from lib.http import get_query_string

    profile = request.user.get_profile()
    if 'filter' in request.GET:
        form = BalanceFilterForm(request.GET)
    else:
        form = BalanceFilterForm()
    date_from = first_date()
    date_to = last_date()
    caller_number = called_number = group = call_type = call_length_type = ""
    order_by = "datetime"
    order_type = "DESC"
    if "order_by" in request.GET:
            order_by = request.GET.get("order_by")
    if "order_type" in request.GET:
            order_type = request.GET.get("order_type")
    if form.is_valid():
        date_from = form.cleaned_data["date_from"]
        date_to = form.cleaned_data["date_to"]
        if date_from and date_to:
            if date_from > date_to:
                request.notifications.add(_(u"You have selected an incorrect date interval!"), "warning")
                return HttpResponseRedirect("/account/phones/statistics/%s/" % tel_number_id)
            else:
                if (date_to.month - date_from.month) > 2 or date_from.year != date_to.year:
                    request.notifications.add("Разница между 'дата с' и  'дата по' должна быть не более двух месяцев!", "warning")
                    return HttpResponseRedirect("/account/phones/statistics/%s/" % tel_number_id)
                if date_from < (datetime.date.today() - timedelta(days=365)):
                    request.notifications.add("'Дата с' должна быть не более чем год назад!", "warning")
                    return HttpResponseRedirect("/account/record_balance/")
        caller_number = form.cleaned_data["caller_number"]
        called_number = form.cleaned_data["called_number"]
        group = form.cleaned_data["group"]
        call_length_type = form.cleaned_data["call_length_type"]
        call_type = form.cleaned_data["call_type"]

    if date_to:
        date_to += timedelta(days=1)

    tel_number = BillserviceSubAccount.objects.get(pk=tel_number_id).username
    rq = RQ2QS(# !!!!!!!!!! вероятно здесь все же стоит использовать обычный QuerySet,
               # но со всякими дополнительными параметрами, вроде QuerySet.extra(...)
               # (для увеличения производительности)
        profile.billing_account_id,
        date_from,
        date_to,
        tel_number=tel_number,
        caller_number=caller_number,
        called_number=called_number,
        group=group,
        call_length_type=call_length_type,
        call_type=call_type,
        order_by=order_by,
        order_type=order_type
    )
    record_tarif = Record_talk_activated_tariff.objects.filter(Q(billing_account_id=profile.billing_account_id) & \
                                                                            Q(date_activation__lt=datetime.datetime.now()) & \
                                                                            (Q(date_deactivation=None) | \
                                                                              Q(date_deactivation__gt=datetime.datetime.now())))
    user_with_record_tarif = False
    if record_tarif:
        user_with_record_tarif = True
    ######################### ?подсчет статистики ################################
    statistics = {}
    cur = connections[settings.BILLING_DB].cursor()
    cur.execute(rq.make_query(count=True))
    rq_stat = cur.fetchone()
    transaction.commit_unless_managed(settings.BILLING_DB)
    stat_count = 0
    if rq_stat[0] > 0:
        stat_count = rq_stat[0]
        stat_time = "%s:%s" % divmod(int(rq_stat[1] / rq_stat[0]), 60)
        stat_price = rq_stat[2]
        stat_count_held = 100.0 / float(stat_count) * rq_stat[3]
        stat_total_time = "%s" % (rq_stat[1] / 60)
    if stat_count > 0:
        statistics = {
                      'count' : stat_count,
                      'count_held' : stat_count_held,
                      'time' : stat_time,
                      'price' : stat_price,
                      'total_time' : stat_total_time
                      }
    else:
        statistics = None
    query = get_query_string(request, exclude=("page",))
    paginator = SimplePaginator(rq, 50, "?page=%%s&%s" % query)
    paginator.set_page(request.GET.get("page", 1))
    return {
        "title": _(u"Calls specification"),
        "form": form,
        "transactions": paginator.get_page(),
        "paginator": paginator,
        "language": "ru",  # TODO: implement some algorithm if needed
        "is_juridical": profile.is_juridical,
        "statistics" : statistics,
        "use_record" : user_with_record_tarif,
        "tel_number_id" : tel_number_id,
        "tel_number" : tel_number
    }



#=================================================================================================================================
#=================================================================================================================================
#=================================================================================================================================
#=================================================================================================================================
#=================================================================================================================================
#=================================================================================================================================
#===========      надо внимательно просмотреть, что же там делается внизу:
#=================================================================================================================================
#=================================================================================================================================
#=================================================================================================================================
#=================================================================================================================================
#=================================================================================================================================








# PHONES
@login_required
@render_to('account/phones.html')
def account_phones(request):

    if request.user.get_profile().is_card:
        raise Http404
    if not request.user.get_profile().is_juridical:
        raise Http404
    context = {}
    profile = request.user.get_profile()
    context['billing_account'] = profile.billing_account
    if request.method == 'POST':
        # save a tel number
        form = TelNumberForm(request.POST.copy(), billing_account=profile.billing_account)
        if form.is_valid():
            phone_id = nextnum.add_number(account=profile.billing_account,
                                         password=form.cleaned_data['password'],
                                         internal_phone=form.cleaned_data.get('internal_phone', ''),
                                         person_name=form.cleaned_data.get('person_name', ''),
                                         jur=profile.is_juridical)
            if phone_id:
                request.notifications.add(_(u"Number was succesfully added."), 'success')
            else:
                request.notifications.add(_("An error occured. Try again or contact administrator"), 'error')
            form = TelNumberForm(billing_account=profile.billing_account)
    else:
        form = TelNumberForm(billing_account=profile.billing_account)

    context['form'] = form
    context['action'] = ''
    context['phones'] = profile.billing_account.phones
    context['title'] = _(u'Internal numbers')
    context['current_view_name'] = 'account_profile'
    return context


@login_required
@render_to('account/edit_phone.html')
def account_edit_phone(request, tel_number_id):

    if request.user.get_profile().is_card:
        raise Http404
    if not request.user.get_profile().is_juridical:
        raise Http404
    context = {}
    try:
        tel_number = TelNumber.objects.get(pk=tel_number_id)
    except TelNumber.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        if 'add_to_external_action' in request.POST:
            try:
                group = TelNumbersGroup(pk=request.POST.get('group_id'))
            except:
                pass
            else:
                tn, created = TelNumbersGroupNumbers.objects \
                                       .get_or_create(tel_number=tel_number.tel_number, \
                                               telnumbersgroup=group)
                request.notifications.add(_(u"Changes were saved."), 'success')
                return HttpResponseRedirect(reverse('account_phones'))
        else:
            form = ChangeTelNumberForm(request.POST.copy(), instance=tel_number, billing_account=request.user.get_profile().billing_account)
            if form.is_valid():
                form.save()
                request.notifications.add(_(u"Changes were saved."), 'success')
                return HttpResponseRedirect(reverse('account_phones'))

    else:
        form = ChangeTelNumberForm(instance=tel_number, billing_account=request.user.get_profile().billing_account)

    '''
    # external phones
    groups = [g for g in
        request.user.get_profile().billing_account.external_phone_groups \
        if 0 == TelNumbersGroupNumbers.objects.filter(telnumbersgroup = g, \
                                               tel_number = tel_number.tel_number) \
                .count()]
    '''
    groups = []
    # короче эта функция вообще нигде не вызовется


    context['title'] = _(u'Edit phone number %(num)s') % {'num':tel_number.tel_number}
    context['current_view_name'] = 'account_profile'
    context['form'] = form
    context['groups'] = groups
    return context

