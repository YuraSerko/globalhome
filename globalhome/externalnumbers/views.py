# coding: utf-8
from django.contrib.auth import authenticate, login
from django.utils.translation import ugettext_lazy as _
from django.http import Http404, HttpResponseRedirect, HttpResponse
from externalnumbers.models import ExternalNumber, ExternalNumberTarif
from lib.decorators import render_to, login_required
import log
from externalnumbers.forms import AddExternalNumberForm
from telnumbers.forms import SelectWithAddGroupForm, group_widget_data
# from django.db import transaction
from telnumbers.models import TelNumbersGroup, TelNumber
from django.core.urlresolvers import reverse
from externalnumbers.consts import REGIONS, NUMBER800_REGION
from findocs.models import FinDocSignedZakazy, Package_on_connection_of_service
from findocs.views import create_package
from django.contrib.auth.models import User
# from findocs.models import FinDocSignApplication
from services.models import AvailableService, AddSPTransaction, BalanceException
from findocs.models import FinDoc, FinDocSigned
from account.models import Profile, ActionRecord
import datetime
import calendar
from django.utils import simplejson
import random
import dateutil.parser
import string
from django.shortcuts import render_to_response
from django.db import connections, transaction
from settings import BILLING_DB
from billing.models import create_billing_account
from account.forms import UserLoginForm2, UserRegistrationForm
from findocs import decorator_for_sign_applications
from data_centr.models import Zakazy, Tariff, Price_connection, Status_zakaza, Service_type, OS, CPU, RAM, HDD, Data_centr_payment
from data_centr.views import cost_dc, send_mail_check, add_record_in_data_centr_payment, add_record_in_priority_of_services, write_off_of_money, add_document_in_dict_for_send
from dateutil.relativedelta import relativedelta
import sys, os
from page.views import panel_base_auth
from django.db.models import Q
from findocs.models import Rules_of_drawing_up_documents, Check
from findocs import get_signed
from content.views import pannel_construct
from lib.decorators import limit_con_service
from externalnumbers.consts import NUMBER800_REGION


@login_required
@render_to("list.html")
def external_list(request):
    "Отображает список местных телефонных номеров пользователя"
    user = request.user
    profile = user.get_profile()
    context = {}
    context["add"] = True
    if profile.is_card:
        raise Http404
    now = datetime.datetime.now()
    bac = profile.billing_account
    context["globalhome"] = True
    context["current_view_name"] = "external_phones_list"
    context["profile"] = profile

    cont_numbers = ExternalNumber.objects.filter(account=bac).exclude(region = NUMBER800_REGION)
    numbers = []
    for i in cont_numbers:
        ext_obj = ExternalNumber.objects.get(number=i.number)
        try:
            zakaz_obj = Zakazy.objects.get(Q(ext_numbers=ext_obj) & Q(bill_account=bac) & (Q(date_deactivation__gt=now) | Q(date_deactivation=None)))
            date_deactivation = zakaz_obj.date_deactivation
        except:
            date_deactivation = None
        numbers.append({"id":i.id, "number":i.number, "region":i.region_str,
                        "phone_numbers_group":i.phone_numbers_group, "date_deactivation":date_deactivation})
    context['numbers'] = numbers
    context["have_free_numbers"] = bool(ExternalNumber.free_numbers.all().count() > 0)
    return context


@login_required
@render_to("edit.html")
def external_edit(request, number_id):
    "Отображает форму редактирования внешнего номера пользователя"
    user = request.user
    profile = user.get_profile()
    if profile.is_card:
        raise Http404
    bac = profile.billing_account
    try:
        number = ExternalNumber.objects.get(id=number_id)
    except Exception, e:
        log.add("Exception 1 in externalnumbers.views.external_edit: '%s'" % e)
        raise e
    if number.account != bac:
        log.add("Someone tryes to edit local number which own some other account! user = %s, number = %s" % (user, number))
        raise Http404
    context = {}
    context["current_view_name"] = "external_phones_list"
    context["profile"] = profile
    context["title"] = u'Редактирование городского номера %s' % number
    context["number"] = number
    if number.phone_numbers_group is None:
        context["no_group"] = True

    groups = bac.telnumbersgroup_set.all()
    context["groups"] = groups

    try:
        g_id = number.phone_numbers_group.id
    except:
        g_id = -1
    choices, settings = group_widget_data(groups, g_id)

    if request.POST:
        # if request.POST.get("get_groups"):
        #    return HttpResponse(get_groups_JSON())
        if request.POST.get("save"):

            form = SelectWithAddGroupForm(request.POST.copy(), choices=choices, settings=settings)

            if form.is_valid():
                group_id = form.cleaned_data.get("user_groups")
                try:
                    group = TelNumbersGroup.objects.get(id=group_id)
                except Exception, e:
                    log.add("Exception 3 in externalnumbers.views.external_edit: '%s'" % e)
                    raise e
                number.phone_numbers_group = group
                number.save(no_assigned_at_save=True)
                request.notifications.add(_(u"Changes have been successfully applied"), "success")
            return HttpResponseRedirect(reverse("external_phones_list"))
        else:
            return HttpResponseRedirect(reverse("external_phones_list"))
    else:
        form = SelectWithAddGroupForm(choices=choices, settings=settings)
        context["form"] = form

    return context


@login_required
@render_to("add.html")
def external_add(request):
    "Добавление внешнего номера"
    cur = connections[BILLING_DB].cursor()
    user = request.user
    profile = user.get_profile()
    if profile.is_card:
        raise Http404
    bac = profile.billing_account

    context = {}
    context["current_view_name"] = "external_phones_list"
    context["title"] = u'Заказ городских телефонных номеров'

    free_numbers_count = 0
    nbr = {}

#    n_lim = ExternalNumber.free_numbers_limited(10)
#    for n in n_lim:
#        print "tut:%s" % n
#
#    for n in n_lim:
#        row = nbr.get(n.region)
#        if row:
#            row.append(n)
#        else:
#            nbr[n.region] = [n, ]


    groups = bac.telnumbersgroup_set.all()
    choices, settings = group_widget_data(groups, -1)

    cur.execute("""SELECT external_numbers_tarif.id,external_numbers_tarif.name,billservice_addonservice.cost FROM external_numbers_tarif LEFT JOIN billservice_addonservice
ON external_numbers_tarif.price_add=billservice_addonservice.id where precode=1""")
    gr = cur.fetchall()
    tz1 = []
    for g in gr:
        p = {}
        p['name'] = g[1]
        p['price'] = float(g[2]) / 1.18
        p['external'] = ExternalNumber.get_numbers_tarif_limit_random(5, g[0])
        free_numbers_count += p['external'].count()
        tz1.append(p)
    tz1.sort(key=lambda x:x['price'])
    context['group'] = tz1

    tz2 = []
    cur.execute("""SELECT external_numbers_tarif.id,external_numbers_tarif.name,billservice_addonservice.cost FROM external_numbers_tarif  LEFT JOIN billservice_addonservice
ON external_numbers_tarif.price_add=billservice_addonservice.id where precode=3""")
    gr = cur.fetchall()
    for g in gr:
        p = {}
        p['name'] = g[1]
        p['price'] = float(g[2]) / 1.18
        p['external'] = ExternalNumber.get_numbers_tarif_limit_random(5, g[0])
        free_numbers_count += p['external'].count()
        tz2.append(p)
    tz2.sort(key=lambda x:x['price'])
    context['group1'] = tz2

    tz3 = []
    cur.execute("""SELECT external_numbers_tarif.id,external_numbers_tarif.name,billservice_addonservice.cost FROM external_numbers_tarif LEFT JOIN billservice_addonservice
ON external_numbers_tarif.price_add=billservice_addonservice.id where precode=2""")
    gr = cur.fetchall()
    transaction.commit_unless_managed(using=BILLING_DB)
    for g in gr:
        p = {}
        p['name'] = g[1]
        p['price'] = float(g[2]) / 1.18
        p['external'] = ExternalNumber.get_numbers_tarif_limit_random(5, g[0])
        free_numbers_count += p['external'].count()
        tz3.append(p)
    tz3.sort(key=lambda x:x['price'])
    context['group2'] = tz3

    context["free_numbers_count"] = free_numbers_count

    if request.POST:
        form = AddExternalNumberForm(request.POST.copy(), numbers_by_regions=nbr, choices=choices, settings=settings)

        if request.POST.get("checkout"):
            if form.is_valid():

                nums_ids = form.cleaned_data["numbers"]
                group_id = form.cleaned_data["user_groups"]
                numbers = []
                for nums in nums_ids:
                    external_number_obj = ExternalNumber.objects.get(id=nums)
                    numbers.append(external_number_obj.number)
                data = {
                        "numbers": numbers,
                        "group_id": group_id,
                        }
                user_obj = User.objects.get(username=user)
                # а сейчас резервируем новые выбранные номера
                for add_number in numbers:
                    external_number_obj = ExternalNumber.objects.get(number=add_number)
                    external_number_obj.phone_numbers_group = None
                    external_number_obj.region = None
                    external_number_obj.account = None
                    external_number_obj.is_free = False
                    external_number_obj.is_reserved = True
                    external_number_obj.assigned_at = datetime.datetime.now()
                    external_number_obj.auth_user = user_obj.id
                    external_number_obj.save()
                successfully_create = create_package(request.user, \
                                            reverse('add_number_final'), \
                                            reverse('external_phones_list'), \
                                            data, \
                                            ['telematic_services_contract', 'localphone_services_contract', 'localphone_orderform'])
                if not successfully_create:
                    raise Http404
                return HttpResponseRedirect(reverse("add_number_final"))
            else:
                context["errors"] = True
        else:
            return HttpResponseRedirect(reverse("external_phones_list"))
    else:
        form = AddExternalNumberForm(numbers_by_regions=nbr, choices=choices, settings=settings)

    context["form"] = form

    return context


@login_required
@render_to("delete.html")
def external_delete(request, number_id):
    "Удаление внешнего номера"
    user = request.user
    profile = user.get_profile()
    if profile.is_card:
        raise Http404
#    if not profile.is_juridical:
#        raise Http404
    bac = profile.billing_account
    try:
        number = ExternalNumber.objects.get(id=number_id)
    except Exception, e:
        log.add("Exception 1 in externalnumbers.views.external_edit: '%s'" % e)
        raise e
    if number.account != bac:
        log.add("Someone tries to delete local number which own some other account! user = %s, number = %s" % (user, number))
        raise Http404

    context = {}
    context["current_view_name"] = "external_phones_list"
    context["profile"] = profile
    context["title"] = _(u"Detaching local number")
    context["number"] = number

    if request.POST:
        if request.POST.get("cancel"):
            return HttpResponseRedirect("../../")
        if request.POST.get("detach"):
            # отсоединяем услугу местного номера
            from services.models import AssignedServicePacket
            # найти назначенный пакет услуг по этому пользователю, слагу пакета услуг и id номера

            asps = AssignedServicePacket.filter_by_params({ "localnumbers_add_num_id": number.id }, user=user, packet_slug="")
            if asps:
                asp = asps[0]
                # запустить отключение этого пакета услуг
                asp.detach(number_id=number_id)
            else:
                log.add("Service error in externalnumbers.views.external_delete: asps is empty!")
                request.notifications.add(_(u"Internal service error. Please contact the support."), "error")
            return HttpResponseRedirect("../../")
    return context


@login_required
@decorator_for_sign_applications()
@render_to("delete.html")
def external_number_delete(request, number_id):
    try:
        package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
    except Package_on_connection_of_service.DoesNotExist:
        successfully_create = create_package(request.user, \
                                '/account/localphones/delete/%s/' % number_id, \
                                reverse('external_phones_list'), \
                                '',
                                ['localphone_detach'])
        if not successfully_create:
            raise Http404
        else:
            return HttpResponseRedirect('/account/localphones/delete/%s/' % number_id)
    try:
        now = datetime.datetime.now()
        date_next_start_month_temp = now + relativedelta(months=1)
        date_next_start_month = datetime.datetime(date_next_start_month_temp.year, date_next_start_month_temp.month, 1, 0, 0, 0)
        ext_number_obj = ExternalNumber.objects.get(id=number_id)
        profile = Profile.objects.get(user=request.user)
        bac = profile.billing_account
        zakaz = Zakazy.objects.get(ext_numbers=ext_number_obj, bill_account=bac, date_deactivation=None)
        zakaz.date_deactivation = date_next_start_month
        zakaz.save()
        package_obj.activate = True
        package_obj.save()
        request.notifications.add(_(u"Номер успешно откреплен!"), "success")
    except Exception, e:
        log.add("Exception in external_number_delete: '%s'" % str(e).decode('utf-8'))
        exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        log.add("Exception in external_number_delete: file:%s line:%s" % (fname, exc_tb.tb_lineno))
        request.notifications.add(_(u"Не удалось удалить номер, обратитесь в техподдержку!"), "warning")
    return HttpResponseRedirect(reverse("external_phones_list"))


def test_drop(user):
    try:

        b = User.objects.get(username=user)
        d = Profile.objects.get(user=b)
        print d.is_juridical
        if d.is_juridical == True:
            t = FinDoc.objects.get(slug="no_telematik")
        else:
            t = FinDoc.objects.get(slug="no_telematik2")
        c = FinDocSigned.objects.get(findoc=t, signed_by=b)
        return False
    except:
        return True

@render_to("mngs.html")
def mng(request):


    cur = connections[BILLING_DB].cursor()
    context = {}
    context['pannel'] = pannel_construct(request)
    cur.execute("""SELECT id,cost FROM billservice_addonservice""")
    abon = dict(cur.fetchall())
    cur.execute("""SELECT id,prepaid_minutes FROM billservice_addonservice""")
    prepaid_minutes = dict(cur.fetchall())
    cur.execute("""SELECT external_numbers_tarif.id,external_numbers_tarif.name,billservice_addonservice.cost,external_numbers_tarif.price_abon FROM external_numbers_tarif LEFT JOIN billservice_addonservice
ON external_numbers_tarif.price_add=billservice_addonservice.id where precode=1""")
    gr = cur.fetchall()
    tz1 = []
    for g in gr:
        p = {}
        p['id'] = g[0]
        p['name'] = g[1]
        p['price'] = float(g[2]) / 1.18
        p['abon'] = float(abon[g[3]]) / 1.18
        p['prepaid_minutes'] = float(prepaid_minutes[g[3]])
        p['external'] = ExternalNumber.get_numb_tarif_limit(5, g[0], 1, '7495')
        tz1.append(p)
    tz1.sort(key=lambda x:x['price'])
    context['group'] = tz1
    tz2 = []
    cur.execute("""SELECT external_numbers_tarif.id,external_numbers_tarif.name,billservice_addonservice.cost,external_numbers_tarif.price_abon FROM external_numbers_tarif  LEFT JOIN billservice_addonservice
ON external_numbers_tarif.price_add=billservice_addonservice.id where precode=3""")
    gr = cur.fetchall()
    for g in gr:
        p = {}
        p['id'] = g[0]
        p['name'] = g[1]
        p['price'] = float(g[2]) / 1.18
        p['abon'] = float(abon[g[3]]) / 1.18
        p['prepaid_minutes'] = float(prepaid_minutes[g[3]])
        p['external'] = ExternalNumber.get_numb_tarif_limit(5, g[0], 2, '7812')
        tz2.append(p)
    tz2.sort(key=lambda x:x['price'])
    context['group1'] = tz2
    tz3 = []
    cur.execute("""SELECT external_numbers_tarif.id,external_numbers_tarif.name,billservice_addonservice.cost,external_numbers_tarif.price_abon FROM external_numbers_tarif LEFT JOIN billservice_addonservice
ON external_numbers_tarif.price_add=billservice_addonservice.id where precode=2""")
    gr = cur.fetchall()
    transaction.commit_unless_managed(using=BILLING_DB)
    for g in gr:
        p = {}
        p['id'] = g[0]
        p['name'] = g[1]
        p['price'] = float(g[2]) / 1.18
        p['abon'] = float(abon[g[3]]) / 1.18
        p['prepaid_minutes'] = float(prepaid_minutes[g[3]])
        p['external'] = ExternalNumber.get_numb_tarif_limit(5, g[0], 1, '7499')
        tz3.append(p)
    tz3.sort(key=lambda x:x['price'])
    context['meta_title'] = u'Многоканальный номер подключить. АТС для офиса бесплатно'
    context['meta_description'] = u'Подключить многоканальный прямой номер. АТС в подарок!'
    context['meta_keywords'] = u'многоканальный номер, прямой номер, городской номер, офисная атс, подключить номер'
    context['group2'] = tz3
    return panel_base_auth(request, context)



def hot_key(request):
    "Добавление внешнего номера"
    context = {}
    param = {}
    errors = {}
    user = request.user
    if user.is_anonymous():
        context['user'] = ""
    else:
        context['user'] = user
        profile = user.get_profile()
        ba_id = profile.billing_account.id
        group_obj = TelNumbersGroup.objects.filter(account=ba_id)
        context['group_numbers'] = group_obj
        if profile.is_card:
            context['user'] = "is card"
    cur = connections[BILLING_DB].cursor()
    cur.execute("""SELECT id,cost FROM billservice_addonservice""")
    abon = dict(cur.fetchall())
    cur.execute("""SELECT external_numbers_tarif.id,external_numbers_tarif.name,billservice_addonservice.cost,external_numbers_tarif.price_abon FROM external_numbers_tarif LEFT JOIN billservice_addonservice
                   ON external_numbers_tarif.price_add=billservice_addonservice.id where precode=1""")
    gr = cur.fetchall()
    tz1 = []
    for g in gr:
        p = {}
        p['name'] = g[1]
        p['price'] = float(g[2]) / 1.18 
        p['abon'] = float(abon[g[3]]) / 1.18  
        p['external'] = ExternalNumber.objects.filter(tarif_group=g[0], is_free=True)
        tz1.append(p)
    tz1.sort(key=lambda x:x['price'])
    context['group'] = tz1
    tz2 = []
    cur.execute("""SELECT external_numbers_tarif.id,external_numbers_tarif.name,billservice_addonservice.cost,external_numbers_tarif.price_abon FROM external_numbers_tarif  LEFT JOIN billservice_addonservice
                   ON external_numbers_tarif.price_add=billservice_addonservice.id where precode=3""")
    gr = cur.fetchall()
    for g in gr:
        p = {}
        p['name'] = g[1]
        p['price'] = float(g[2]) / 1.18
        p['abon'] = float(abon[g[3]]) / 1.18
        p['external'] = ExternalNumber.objects.filter(tarif_group=g[0], is_free=True)
        tz2.append(p)
    tz2.sort(key=lambda x:x['price'])
    context['group1'] = tz2
    tz3 = []
    cur.execute("""SELECT external_numbers_tarif.id,external_numbers_tarif.name,billservice_addonservice.cost,external_numbers_tarif.price_abon FROM external_numbers_tarif LEFT JOIN billservice_addonservice
                   ON external_numbers_tarif.price_add=billservice_addonservice.id where precode=2""")
    gr = cur.fetchall()
    transaction.commit_unless_managed(using=BILLING_DB)
    for g in gr:
        p = {}
        p['name'] = g[1]
        p['price'] = float(g[2]) / 1.18
        p['abon'] = float(abon[g[3]]) / 1.18
        p['external'] = ExternalNumber.objects.filter(tarif_group=g[0], is_free=True)
        tz3.append(p)
    tz3.sort(key=lambda x:x['price'])
    context['group2'] = tz3
    if request:
        if request.POST.has_key('face'):
            if not request.POST.has_key('numbers'):
                errors['numbers'] = True
                context['errors'] = errors
                return render_to_response("s1_ext_num.html", context)

            param['face'] = request.POST['face']
            numbers_list = request.POST.getlist('numbers')
            str_number = " ".join([item for item in numbers_list])
            number_list = str_number.split()
            result = []
            import re
            rexp = r"reg_(\d+)_id_(\d+)"
            r = re.compile(rexp)
            for v in number_list:
                m = r.match(v)
                if m:
                    data = r.findall(v)[0]
                    if len(data) == 2:
                        ids = int(data[1])
                        result.append(ids)
            numbers = []
            for res_id in result:
                object_numbers = ExternalNumber.objects.get(id=res_id)
                region = object_numbers.region
                id_tarif = object_numbers.tarif_group
                number = object_numbers.number
                numbers.append(number)
                param['numbers'] = numbers
                param['id_reg'] = str(region)
                param['id_tarif'] = id_tarif
                param['back'] = 1
                if request.POST.has_key('group_numbers'):
                    param['group_id'] = request.POST['group_numbers']
                icode = 0
                if str(id_tarif) in ('1', '3', '5'):
                    icode = 7495
                if str(id_tarif) in ('5', '7', '9'):
                    icode = 7499
                if str(id_tarif) in ('6', '8', '10'):
                    icode = 7812
                param['icode'] = str(icode)
                context['icode'] = str(icode)
                context['id_tarif'] = id_tarif
            context['data'] = simplejson.dumps(param)
            context['back'] = True
            if param['face'] == '0':
                form_reg = UserRegistrationForm()
                context['form_reg'] = form_reg
                return render_to_response("s2.html", context)
            elif param['face'] == '1':
                form_login = UserLoginForm2()
                context['form_login'] = form_login
                return render_to_response("s3.html", context)
            # если пользователь уже в системе
            elif param['face'] == '2':
                try:
                    user_obj = User.objects.get(username=user)
                    param['redirect_after_reg'] = reverse('add_number_final')
                    context['data'] = simplejson.dumps(param)
                    # а сейчас резервируем новые выбранные номера
                    for add_number in param['numbers']:
                        external_number_obj = ExternalNumber.objects.get(number=add_number)
                        external_number_obj.phone_numbers_group = None
                        external_number_obj.region = None
                        external_number_obj.account = None
                        external_number_obj.is_free = False
                        external_number_obj.is_reserved = True
                        external_number_obj.assigned_at = datetime.datetime.now()
                        external_number_obj.auth_user = user_obj.id
                        external_number_obj.save()
                    successfully_create = create_package(request.user, \
                                                reverse('add_number_final'), \
                                                reverse('external_phones_list'), \
                                                context['data'], \
                                                ['telematic_services_contract', 'localphone_services_contract', 'localphone_orderform'])
                    if not successfully_create:
                        raise Http404
                    return render_to_response("s8.html", context)
                except Exception, e:
                    print e
                    raise Http404
            else:
                raise Http404
    return render_to_response("s1_ext_num.html", context)

def step_1(request, id_tarif, icode):
    try:
        context = {}
        user = request.user.username
        context['user'] = user
        param = {}
        if not user and not request.GET.has_key('face'):
            start = False
        else:
            start = True
        try:
            region = 0
            if str(icode) in ('7495', '7499'):
                region = 1
            if str(icode) == '7812':
                region = 2
        except Exception, e:
            print e

        context['external'] = ExternalNumber.get_numbers_tarif_limit_random(10, int(id_tarif))
        errors = {}
        if not context['external']:
            errors['none_numbers'] = True
            context['errors'] = errors
        context['id_reg'] = region
        context['id_tarif'] = id_tarif
        context['icode'] = icode
        if start:
            try:
                param['face'] = request.GET['face']
                param['numbers'] = request.GET.getlist('numbers')
            except:
                return render_to_response("s1.html", context)
            param['id_tarif'] = request.GET['id_tarif']
            param['icode'] = request.GET['icode']
            # param['numbers'] = request.GET.getlist('numbers')
            context['data'] = simplejson.dumps(param)
            try:
                request.GET['numbers']
            except Exception, e:
                print e
                errors['numbers'] = True
                context['errors'] = errors
                return render_to_response("s1.html", context)
            # context['data'] = simplejson.dumps(param)
            if param['face'] == '0':
                form_reg = UserRegistrationForm()
                context['form_reg'] = form_reg
#                 context['but_pr_val'] = "step_1('{{id_tarif}}','{{icode}}')"
                return render_to_response("s2.html", context)
            elif param['face'] == '1':
                form_login = UserLoginForm2()
                context['form_login'] = form_login
                return render_to_response("s3.html", context)
            # если пользователь уже в системе
            elif param['face'] == '2':
                try:
                    user_obj = User.objects.get(username=user)
                    param['redirect_after_reg'] = reverse('add_number_final')
                    context['data'] = simplejson.dumps(param)
                    # а сейчас резервируем новые выбранные номера
                    for add_number in param['numbers']:
                        external_number_obj = ExternalNumber.objects.get(number=add_number)
                        external_number_obj.phone_numbers_group = None
                        external_number_obj.region = None
                        external_number_obj.account = None
                        external_number_obj.is_free = False
                        external_number_obj.is_reserved = True
                        external_number_obj.assigned_at = datetime.datetime.now()
                        external_number_obj.auth_user = user_obj.id
                        external_number_obj.save()
                    successfully_create = create_package(request.user, \
                                                reverse('add_number_final'), \
                                                reverse('external_phones_list'), \
                                                context['data'], \
                                                ['telematic_services_contract', 'localphone_services_contract', 'localphone_orderform'])
                    if not successfully_create:
                        raise Http404
                    return render_to_response("s8.html", context)
                except Exception, e:
                    print e
                    raise Http404
            else:
                raise Http404
    except Exception, e:
        log.add("Exception in step_1: '%s'" % e)
        exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        log.add("Exception in step_1: file:%s line:%s" % (fname, exc_tb.tb_lineno))

    return render_to_response("s1.html", context)

def step_2_auth(request):
    context = {}
    errors = {}
    form_login = UserLoginForm2(request.GET)
    context['form_login'] = form_login
    try:
        param = simplejson.loads((str(request.GET['data'])).strip('/'))
        context['id_tarif'] = param['id_tarif']
        context['icode'] = param['icode']
    except Exception, e:
        raise Http404
    context['data'] = simplejson.dumps(param)
    try:
        if form_login.is_valid():
            user = form_login.user
            if user:
                if user.is_active:
                    login(request, user)
                    user_obj = User.objects.get(username=user.username)
                    context['data'] = simplejson.dumps(param)
                    # а сейчас резервируем новые выбранные номера
                    for add_number in param['numbers']:
                        external_number_obj = ExternalNumber.objects.get(number=add_number)
                        external_number_obj.phone_numbers_group = None
                        external_number_obj.region = None
                        external_number_obj.account = None
                        external_number_obj.is_free = False
                        external_number_obj.is_reserved = True
                        external_number_obj.assigned_at = datetime.datetime.now()
                        external_number_obj.auth_user = user_obj.id
                        external_number_obj.save()
                    successfully_create = create_package(request.user, \
                                                reverse('add_number_final'), \
                                                reverse('external_phones_list'), \
                                                context['data'], \
                                                ['telematic_services_contract', 'localphone_services_contract', 'localphone_orderform'])
                    if not successfully_create:
                        raise Http404
                    return render_to_response("s8.html", context)

            if user is None:
                errors['error_auth'] = True
                context['errors'] = errors
                return render_to_response("s3.html", context)
        else:
            if param.get('back') == 1:
                context['back'] = 1
            errors['error_auth'] = True
            context['errors'] = errors
            return render_to_response("s3.html", context)
    except Exception, e:
        print e
    else:
        return render_to_response("s3.html", context)

def step_2_reg(request):
    context = {}
    errors = {}
    form_reg = UserRegistrationForm(request.GET)
    context['form_reg'] = form_reg
    try:
        param = simplejson.loads((str(request.GET['data'])).strip('/'))
        param['redirect_after_reg'] = reverse('add_number_final')
        context['id_tarif'] = param['id_tarif']
        context['icode'] = param['icode']
        param['numbers']


        context['data'] = simplejson.dumps(param)
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        log.add("step_2_reg: file:%s row:%s e:%s" % (fname, exc_tb.tb_lineno, e))
        raise Http404

    if form_reg.is_valid():
        user = form_reg.save()
        for add_number in param['numbers']:
            try:
                external_number_obj = ExternalNumber.objects.get(number=str(add_number))
            except ExternalNumber.DoesNotExist:
                continue
            external_number_obj.phone_numbers_group = None
            external_number_obj.region = None
            external_number_obj.account = None
            external_number_obj.is_free = False
            external_number_obj.is_reserved = True
            external_number_obj.assigned_at = datetime.datetime.now()
            external_number_obj.auth_user = user.id
            external_number_obj.save()
        ActionRecord.registrations.create_inactive_user_key(
            new_user=user,
            row_password = user.password,
            #row_password=form_reg.get_row_password(),
            send_email=True,
            )
        successfully_create = create_package(user, \
                            reverse('add_number_final'), \
                            reverse('external_phones_list'), \
                            context['data'], \
                            ['telematic_services_contract', 'localphone_services_contract', 'localphone_orderform'])
        if not successfully_create:
            raise Http404
        return render_to_response("s8_reg.html", context)
    else:
        if param.get('back') == 1:
            context['back'] = 1
        errors['error_auth'] = True
        context['errors'] = errors
        return render_to_response("s2.html", context)

@login_required
@limit_con_service([3], 'telephony')
@decorator_for_sign_applications()
def add_number_final(request, param={}):
    user_obj = User.objects.get(username=request.user.username)
    try:
        package_obj = Package_on_connection_of_service.objects.get(user=user_obj, activate=False, deactivate=False)
    except:
        raise Http404
    if not request.POST:
        request.POST = request.GET
    if not param:
        param = package_obj.data
    if not param:
        return HttpResponseRedirect(reverse("external_phones_list"))

    param = eval(param)
    profile = Profile.objects.get(user=user_obj)
    bac = profile.billing_account
    tel_number_obj = TelNumber.objects.filter(account=bac).order_by('tel_number')[:1]
    if tel_number_obj:
        for i in tel_number_obj:
            number = i
    else:
        # Добавляем внутренний номер
        next_number = TelNumber.get_next_free_number(profile.is_hostel, profile.is_juridical)
        next_number_str = str(next_number)
        password = ''
        for i in range(4):
            password = password + random.choice('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')
        number = TelNumber.create(
            bac,
            next_number=next_number,
            is_juridical=profile.is_juridical,
            password=password,
            person_name=user_obj.username,
            internal_phone=int(next_number_str[0:1] + next_number_str[len(next_number_str) - 3:len(next_number_str)]),
        )
        number.save()
    numbers = [number]
    # Добавляем группу к полученному номеру
    if param.has_key('group_id'):
        group = TelNumbersGroup.objects.get(id=param['group_id'])
    else:
        i = 1
        while 1:
            group_obj = TelNumbersGroup.objects.filter(account=bac, name='group_%s' % string.zfill(i, 4))
            if group_obj:
                i += 1
            else:
                group_name = 'group_%s' % string.zfill(i, 4)
                break
        group = TelNumbersGroup.create(group_name, bac, numbers)
        group.save()
    # закрепляем за созданной группой местный номер
    if not param.has_key('numbers'):
        log.add("add_number_final: 720")
        raise Http404
    for add_number in param['numbers']:
        if add_number[0:4] in ('7495', '7499'):
            region = 1
        elif add_number[0:4] == '7812':
            region = 2
        else:
            log.add("add_number_final: 728")
            raise Http404
        external_number_obj = ExternalNumber.objects.get(number=add_number)
        external_number_obj.phone_numbers_group = group
        external_number_obj.account = bac
        external_number_obj.is_free = False
        external_number_obj.is_reserved = False
        external_number_obj.assigned_at = datetime.datetime.now()
        external_number_obj.region = region
        external_number_obj.save()
    # Добавляем запись в таблицу data_centr_zakazy для дальнейшего списания денег
    status_obj = Status_zakaza.objects.get(id=2)
    service_type_obj = Service_type.objects.get(id=3)
    hidden_id = []
    #cur = connections[BILLING_DB].cursor()
    #cur.connection.set_isolation_level(1)
    for add_number in param['numbers']:
        external_number_obj = ExternalNumber.objects.get(number=add_number)

        external_number_tariff = ExternalNumberTarif.objects.get(id = external_number_obj.tarif_group)
        tariff_obj = external_number_tariff.data_centr_tariff
        connection_cost = external_number_tariff.data_centr_price_connection
        zakaz = Zakazy(
                     bill_account=bac,
                     section_type=1,
                     status_zakaza=status_obj,
                     service_type=service_type_obj,
                     tariff=tariff_obj,
                     connection_cost=connection_cost,
                     date_create=datetime.datetime.now(),
                     date_activation=datetime.datetime.now(),
                     )
        zakaz.save()
        external_number_obj = ExternalNumber.objects.get(number=add_number)
        zakaz.ext_numbers.add(external_number_obj)
        zakaz.save()
        hidden_id.append(zakaz.id)
        cost = float(cost_dc(zakaz.id))
        zakaz.cost = '%.2f' % cost
        zakaz.save()

        findocsign_queryset = package_obj.findoc_sign.filter(findoc__slug='localphone_orderform')
        if findocsign_queryset:
            findocsign_obj = findocsign_queryset[0]
        fin_doc_zakaz = FinDocSignedZakazy(
                                           fin_doc=findocsign_obj,
                                           zakaz_id=zakaz.id,
                                           )
        fin_doc_zakaz.save()
        findocsign_queryset = package_obj.findoc_sign.filter(findoc__slug='telematic_services_contract')
        if not findocsign_queryset:
            findocsign_obj = get_signed(profile.user, "telematic_services_contract")
        else:
            findocsign_obj = findocsign_queryset[0]
        fin_doc_zakaz = FinDocSignedZakazy(
                                           fin_doc=findocsign_obj,
                                           zakaz_id=zakaz.id,
                                           )
        fin_doc_zakaz.save()
        findocsign_queryset = package_obj.findoc_sign.filter(findoc__slug='localphone_services_contract')
        if not findocsign_queryset:
            findocsign_obj = get_signed(profile.user, "localphone_services_contract")
        else:
            findocsign_obj = findocsign_queryset[0]
        fin_doc_zakaz = FinDocSignedZakazy(
                                           fin_doc=findocsign_obj,
                                           zakaz_id=zakaz.id,
                                           )
        fin_doc_zakaz.save()
        # добавляем по очереди записи в две таблицы
        add_record_in_data_centr_payment(zakaz)
        add_record_in_priority_of_services(zakaz)

#        if bac.auto_paid:
#            write_off_of_money(bac, [zakaz.id])
    package_obj.activate = True
    package_obj.save()
    rule_obj = Rules_of_drawing_up_documents.objects.get(id=4)
    spis_rules = Check.group_rules(profile, [rule_obj.id], 'type_check')
    content_check_id = Check.create_check(request.user, spis_rules, False, hidden_id)
    dict_documents_for_send = add_document_in_dict_for_send({}, request.user.id, 'Check', content_check_id)
    send_mail_check(dict_documents_for_send)

    request.notifications.add(_(u'Услуга "Предоставление городского номера" успешно добавлена!'), "success")
    return HttpResponseRedirect(reverse("external_phones_list"))

