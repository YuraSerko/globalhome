# coding: utf-8
import os.path
from lib.decorators import render_to, login_required, limit_con_service
from internet.forms import VpnAuthForm, VpnFormEdit
from internet.models import VpnAuth, Connection_address, ScheduleConnectionInternet, \
    Internet_street, Internet_house
from lib.utils import get_now
from account.models import Profile, ActionRecord
from django.shortcuts import HttpResponseRedirect, HttpResponse
from django.http import Http404
from page.views import panel_base_auth
from data_centr.models import Tariff, Price
from django.utils import simplejson
from account.forms import UserLoginForm2, UserRegistrationForm
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from findocs.views import create_package
from django.contrib.auth import login
from billing.models import BillserviceAccount  # @UnresolvedImport
from data_centr.models import Zakazy, Status_zakaza, IP, Status_ip
from django.db.models import Q
from findocs.models import Package_on_connection_of_service
from data_centr.views import cost_dc, send_mail_check, add_record_in_data_centr_payment, add_record_in_priority_of_services, write_off_of_money, add_document_in_dict_for_send
from findocs import decorator_for_sign_applications
from django.utils.translation import ugettext_lazy as _
import datetime, copy
from dateutil.relativedelta import relativedelta  # @UnresolvedImport
from django.conf import settings  # @UnusedImport
from findocs.models import FinDocSignedZakazy, Rules_of_drawing_up_documents, Check
from django.shortcuts import get_object_or_404
from notify.context_processors import notifications
from data_centr.models import Priority_of_services
from findocs import get_signed
from lib.mail import send_email
from billing_models import SubAccount
from django.template import  RequestContext
dict_persons = {'legal_entity':[1], 'individual':[2], 'cottage_settlement':[3]}
dict_profile_count_ip = {"True":8, "False":4}
from content.views import pannel_construct
from models import Internet_city
from django.contrib.admin.views.decorators import staff_member_required
from findocs.models import FinDoc, FinDocTemplate, FinDocSignApplication, FinDocSigned, Package_on_connection_of_service, \
                            Rules_of_drawing_up_documents, Check, Act, Invoice, Download_documents, Download_checks, Print_act
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import Group

@staff_member_required
def ajax_schedule_connection(request):
    if request.POST.has_key('item'):
        obj = Connection_address.objects.get(id=request.POST['item'])
        distr_id = obj.home_administration.all()[0].district_administration.id
        id_obj = ScheduleConnectionInternet.objects.filter(district=distr_id)
        str_id = '; '.join(t.date + u'_' + t.time  for t in id_obj)
        data_title_str = u''
        for li in id_obj:
            data_title_str = data_title_str + str(li.date) + u'_' + str(li.time) + u'%' + li.adress.__unicode__() + u'  ' + u'кв.' + li.flat + ';'
        work_day = datetime.datetime.now().date() + relativedelta(days=3)
        if work_day.weekday() == 5:
            work_day = work_day + relativedelta(days=2)
        elif work_day.weekday() == 6:
            work_day = work_day + relativedelta(days=1)
        work_day = str(work_day.day) + "-" + str(work_day.month) + "-" + str(work_day.year)
        resp = str_id + u'   ' + data_title_str + u'   ' + work_day
    else:
        raise Http404

    return HttpResponse(resp)




@login_required
@render_to('vpn_user.html')
def vpn_users(request):
    context = {}
    context['edit'] = False
    context['title'] = u'Список Ваших VPN аккаунтов'
    context['current_view_name'] = "vpn_users"
    profile = Profile.objects.get(user=request.user)
    vpn_logins = VpnAuth.objects.filter(billing_account_id=profile.billing_account_id, visible=True)
    vpn_login = []
    for i in vpn_logins:
        vpn_login.append({'id' : i.id, 'login' : i.login, 'value' : i.value })
    context['vpn_logins'] = vpn_login
    context["add"] = True
    return context


@login_required
@render_to('vpn_user_add.html')
def vpn_users_add(request):
    context = {}
    context['title'] = u'Добавление VPN аккаунта'
    context['current_view_name'] = "vpn_users"
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = VpnAuthForm(request.POST.copy())
        if form.is_valid():
            cd = form.cleaned_data
            if VpnAuth.objects.filter(login=cd['login']):
                request.notifications.add(u'Данный логин уже существует.', 'error')
            elif cd['password'] != cd['password_check']:
                request.notifications.add(u'Пароли не совпадают!', 'error')
            else:
                context = {}
                VpnAuth.objects.create(login=cd['login'], value=cd['password'], billing_account_id=profile.billing_account_id)
                request.notifications.add(u'Данные успешно добавлены', 'success')
                return HttpResponseRedirect("/account/internet/vpn/")
    else:
        form = VpnAuthForm()
    context['form'] = form
    return context


@login_required
@render_to('vpn_user_edit.html')
def vpn_users_edit(request, vpn_id):
    context = {}
    context['edit'] = True
    context['title'] = u'Изменить пароль к VPN аккаунту'
    context['current_view_name'] = "vpn_users"
    profile = Profile.objects.get(user=request.user)
    try:
        st = VpnAuth.objects.get(id=vpn_id, billing_account_id=profile.billing_account_id, visible=True)
        if st:
            if request.method == 'POST':
                form = VpnFormEdit(request.POST.copy())
                if form.is_valid():
                    form_login = form.cleaned_data.get('login')
                    form_password = form.cleaned_data.get('password')
                    form_password_check = form.cleaned_data.get('password_check')
                    if form_password != form_password_check:
                        request.notifications.add(u'Пароли не совпадают', 'error')
                    else:
                        try:
                            st = VpnAuth.objects.get(login=form_login, billing_account_id=profile.billing_account_id, visible=True)
                            st.value = form_password
                            st.save()
                            request.notifications.add(u'Редактирование успешно завершено', 'success')
                            return HttpResponseRedirect("/account/internet/vpn/")
                        except VpnAuth.DoesNotExist:
                            raise Http404
                else:
                    context['form'] = form
                    return context
    except VpnAuth.DoesNotExist:
        raise Http404
    context['form'] = VpnFormEdit(initial={'login': st.login })
    return context


@login_required
@render_to('vpn_user_del.html')
def vpn_users_del(request, vpn_id):
    context = {}
    profile = Profile.objects.get(user=request.user)
    try:
        st = VpnAuth.objects.get(id=vpn_id, billing_account_id=profile.billing_account_id, visible=True)
    except VpnAuth.DoesNotExist:
        raise Http404
    context['vpn'] = st
    context['vpn_id'] = vpn_id
    context['title'] = u'Удаление VPN аккаунта'
    context['current_view_name'] = "vpn_users"
    return context


@login_required
def vpn_users_deleting(request, vpn_id):
    profile = Profile.objects.get(user=request.user)
    try:
        st = VpnAuth.objects.get(id=vpn_id, billing_account_id=profile.billing_account_id, visible=True)
        st.visible = False
        st.save()
    except VpnAuth.DoesNotExist:
        raise Http404
    request.notifications.add(u'Удаление успешно завершено', 'success')
    return HttpResponseRedirect("/account/internet/vpn/")


@render_to('show_internet.html')
def show_internet(request):
    context = {}
    return panel_base_auth(request, context)


@render_to('show_wifi.html')
def show_wifi(request):
    context = {}
    return panel_base_auth(request, context)


@render_to('internet_cover_zone.html')
def internet_cover_zone(request):
    context = {}
    #  for coordinates
    coordhotspot = Connection_address.objects.filter(persons__id=2, readiness_degree__in=[2, 3, 4, 5, 6, 7]).all()
    context['coordhotspot'] = coordhotspot
    allcities = Internet_city.objects.all()
    context['allcities'] = allcities
    return panel_base_auth(request, context)


def get_tariffs(context, person=[]):
    inet_tariff = []
    tariff_queryset = Tariff.objects.filter(service_type=8, for_person__id__in=person, individual=False, archive=False).order_by('speed_inet', '-id')
    for tariff_obj in tariff_queryset:
        if 2 in person or 3 in person:
            cost = tariff_obj.price_id.cost
        else:
            cost = tariff_obj.price_id.cost / 1.18
        inet_tariff.append({"id": tariff_obj.id, "name":tariff_obj.name, "cost": cost, "speed_inet":tariff_obj.speed_inet})
    context['inet_tariff'] = inet_tariff
    return context


@render_to('internet_tariff_legal_entity.html')
def internet_legal_entity(request):
    context = {}
    context['pannel'] = pannel_construct(request)
    context['title'] = u'Интернет для юридических лиц'
    context['type_face'] = 'legal_entity'
    context = get_tariffs(context, [1])
    return panel_base_auth(request, context)


@render_to('internet_tariff_legal_entity.html')
def internet_individual(request):
    context = {}
    context['pannel'] = pannel_construct(request)
    context['title'] = u'Интернет для физических лиц'
    context['type_face'] = 'individual'
    context = get_tariffs(context, [2])
    #  for coordinates
    coordhotspot = Connection_address.objects.filter(persons__id=2).all()
    context['coordhotspot'] = coordhotspot
    allcities = Internet_city.objects.all()
    context['allcities'] = allcities
    context['notes'] = [('*', 'c бесплатной установкой нашего маршрутизатора Wi-Fi.  Доступ в интернет будет осуществляться через сайт globalhome.mobi.')]
    return panel_base_auth(request, context)



@render_to('internet_individual_coverage_map.html')
def internet_individual_coverage_map(request):
    context = {}
    allcities = Internet_city.objects.all()
    context['allcities'] = allcities
    return panel_base_auth(request, context)

# передаем ajax точки в html internet_tariff_legal_entity.html
@render_to('internet_tariff_legal_entity.html')
def ajax_internet_indivdiual_points(request):
    coordhotspot_st = ''
    coordhotspot = Connection_address.objects.filter(persons__id=2).select_related()
    for c in coordhotspot:
        coordhotspot_st = coordhotspot_st + str(c.x) + ',' + str(c.y) + ',' + c.street.street_type + " " + c.street.street + " " + c.house.house + ":"
        dlina = len(coordhotspot_st) - 1
        coordhotspot_string = coordhotspot_st[0:dlina]
    return HttpResponse(u'%s' % (coordhotspot_string))

@render_to('internet_tariff_legal_entity.html')
def internet_cottage_settlement(request):
    context = {}
    context['pannel'] = pannel_construct(request)
    context['title'] = u'Интернет для коттеджных поселков'
    context['type_face'] = 'cottage_settlement'
    context = get_tariffs(context, [3])
    return panel_base_auth(request, context)

def ajax_interactive_search(request):
    if not request.POST.has_key('item') or not request.POST.has_key('city'):
        raise Http404
    adrress = request.POST['item']
    city = request.POST['city']
    if adrress == ' ':
        return HttpResponse('')
    qs_street = Connection_address.objects.filter(street__street__icontains=adrress.encode('utf-8'), city=city)
    nqs = qs_street.distinct('street')
    html = ""
    if len(nqs) <= 3:
        for qs_obj in nqs:
            house_obj = Connection_address.objects.filter(street=qs_obj.street)
            html = html + " %s<br/>" % qs_obj.street
            for house in house_obj:
                html = html + "<a href='/internet/'> %s</a>" % house.house
            html = html + "<br>"
        return HttpResponse(html)
    else:
        for qs_obj in nqs:
            html = html + " %s<br/>" % qs_obj.street
        return HttpResponse(html)

def ajax_interactive_search_point(request, per_id):
    # set readiness_degree
    noaddress = False
    if not request.POST.has_key('item') or not request.POST.has_key('city'):
        raise Http404
    adrress = request.POST['item']
    city = request.POST['city']
    if adrress == ' ':
        return HttpResponse('')
    if (per_id == '5'):
        qs_street = Connection_address.objects.filter(readiness_degree6__exact=1, \
                                                       street__street__icontains=adrress.encode('utf-8'), \
                                                       city__city=city.encode('utf-8'), persons__id=per_id)
    if (per_id == '2'):
        qs_street = Connection_address.objects.filter(readiness_degree0__exact=1, \
                                                       street__street__icontains=adrress.encode('utf-8'), \
                                                       city__city=city.encode('utf-8'), persons__id=per_id)
    nqs = qs_street.distinct('street')
    if (not qs_street):
        noaddress = True
    html = ""
    if noaddress:
        html = html + "<font color=grey>По данному условию адресов не найдено"
    if len(nqs) <= 3:
        for qs_obj in nqs:
            if (per_id == '5'):
                house_obj = Connection_address.objects.filter(readiness_degree6__exact=1, \
                                                               street=qs_obj.street, persons__id=per_id)
            if (per_id == '2'):
                house_obj = Connection_address.objects.filter(readiness_degree0__exact=1, \
                                                               street=qs_obj.street, persons__id=per_id)
            html = html + "<div> %s" % qs_obj.street
            html = html + "<div>"
            house_len = len(house_obj)
            i = 1
            for house in house_obj:
                if (i != house_len):
                    html = html + "<a class ='rt'  value = '%s, %s, %s' onclick = 'val_a(this, %s)'> %s,</a>" % (house.y, house.x, str(house.id), house.id, house.house)
                if (i == house_len):
                    html = html + "<a class ='rt'  value = '%s, %s, %s' onclick = 'val_a(this, %s)'> %s</a>" % (house.y, house.x, str(house.id), house.id, house.house)
                i = i + 1;
            html = html + "</div></div>"
        return HttpResponse(html)
    else:
        for qs_obj in nqs:
            html = html + " %s<br/>" % qs_obj.street
        return HttpResponse(html)


def ajax_change_tariff(request, type_face):
    if request.GET.has_key('tariff'):
        tariff = request.GET['tariff']
    else:
        tariff = False
    if request.GET.has_key('count_static_ip'):
        count_static_ip = request.GET['count_static_ip']
    else:
        count_static_ip = 0
    price_obj = Price.objects.get(id=36)
    if tariff:
        tariff_obj = get_object_or_404(Tariff, id=tariff)
        if type_face in ('individual', 'cottage_settlement',):
            cost = tariff_obj.price_id.cost + int(count_static_ip) * float(price_obj.cost)
        elif type_face in ('legal_entity'):
            cost = tariff_obj.price_id.cost / 1.18 + int(count_static_ip) * float(price_obj.cost / 1.18)
    else:
        if type_face in ('individual', 'cottage_settlement',):
            cost = int(count_static_ip) * float(price_obj.cost)
        elif type_face in ('legal_entity'):
            cost = int(count_static_ip) * float(price_obj.cost / 1.18)
    return HttpResponse(cost)


def ajax_change_city(request, type_face):
    if not request.GET.has_key('city') or not type_face in ('individual', 'legal_entity', 'cottage_settlement',):
        raise Http404
    city = request.GET['city']
    dict_street = Connection_address.objects.filter(city__city=city, persons__id__in=dict_persons[type_face]).order_by('street__street').distinct().values('street__street')
    if not dict_street:
        raise Http404
    str_street = ','.join([i["street__street"] for i in dict_street]).rstrip(', ')
    return HttpResponse(str_street)


def ajax_change_street(request, type_face):
    if not request.GET.has_key('street') or not type_face in ('individual', 'legal_entity', 'cottage_settlement',):
        raise Http404
    city = request.GET['city']
    street = request.GET['street']
    dict_house = Connection_address.objects.filter(city__city=city, street__street=street, persons__id__in=dict_persons[type_face]).order_by('house__house').distinct().values('house__house')
    if not dict_house:
        raise Http404
    str_house = ','.join([i["house__house"] for i in dict_house]).rstrip(', ')
    return HttpResponse(str_house)


def ajax_step_zakaz(request, account, type_face):
    print 'ajax_step_zakaz'
    if not type_face in ('individual', 'legal_entity', 'cottage_settlement',):
        raise Http404
    context = {}
    try:
        user_obj = User.objects.get(username=request.user.username)
        profile = Profile.objects.get(user=user_obj)
    except:
        profile = ''
    if profile:
        if (type_face in ('individual', 'cottage_settlement',)) and (profile.is_juridical):
            return render_to_response("step_not_physical.html", context)
        elif (type_face == 'legal_entity') and (not profile.is_juridical):
            return render_to_response("step_not_juridical.html", context)
    # context['inet_tariff'] = Tariff.objects.filter(service_type=8, for_person__id__in=dict_persons[type_face], individual=False, archive=False)
    price_obj = Price.objects.get(id=36).cost
    if type_face == "legal_entity":
        price_obj = price_obj / 1.18
        get_tariffs(context, [1])
    elif type_face == "individual":
        get_tariffs(context, [2])
    elif type_face == "cottage_settlement":
        get_tariffs(context, [3])

    context['user'] = request.user.username
    dict_city = Connection_address.objects.filter(persons__id__in=dict_persons[type_face]).order_by('city__city').distinct().values('city__city')
    context['spis_city'] = [i["city__city"] for i in dict_city]
    context['account'] = account
    context['type_face'] = type_face
    context['port_price'] = price_obj
    return render_to_response("step_zakaz.html", context)


def ajax_step_auth(request, account, type_face):
    print 'ajax_step_auth'
    print "GET = %s" % request.GET
    param, context = {}, {}
    account = eval(account)

    try:
        param['tariff'], param['city'], param['street'], param['house'], param['type_face'] = \
        request.GET['tariff'], request.GET['city'], request.GET['street'], request.GET['house'], type_face
        if not account:
            param['face'] = request.GET['face']
        equipment = []
        dict_equipment = {'switch':u'Свитч', 'router':u'Маршрутизатор', 'AP':u'Точка доступа', 'NIC':u'Сетевая карта'}
        for key, value in dict_equipment.items():
            if request.GET.has_key('equip_%s' % key):
                equipment.append(value)
        count_static_ip = 0
        if request.GET.has_key('count_static_ip'):
            count_static_ip = request.GET['count_static_ip']
        str_equipment = ', '.join([x for x in equipment]).rstrip(', ')
        param['equipment'] = str_equipment
        param['count_static_ip'] = count_static_ip
    except Exception, e:
        print 'e = %s' % e
        raise Http404
    try:
        Connection_address.objects.get(city__city=param['city'], street__street=param['street'], house__house=param['house'])
        tariff_obj = Tariff.objects.get(id=param['tariff'])
        person_obj = tariff_obj.for_person.all()[0]
    except Exception, e:
        raise Http404
    context['data'] = simplejson.dumps(param)
    context['type_face'] = type_face
    if not account:
        if param['face'] == '0':
            form_reg = UserRegistrationForm()
            context['form_reg'] = form_reg
            return render_to_response("step_reg2.html", context_instance=RequestContext(request, context))
        elif param['face'] == '1':
            form_login = UserLoginForm2()
            context['form_login'] = form_login
            return render_to_response("step_login2.html", context)
        # если пользователь уже в системе
        elif param['face'] == '2':
            try:
                if person_obj.id in (2, 3,):
                    successfully_create = create_package(request.user,
                                            reverse('add_inet_final'),
                                            reverse('my_inet'),
                                            param,
                                            ['dogovor_oferta'])
                else:
                    successfully_create = create_package(request.user,
                                            reverse('add_inet_final'),
                                            reverse('my_inet'),
                                            param,
                                            ['telematic_data_centr', 'usluga_peredachi_dannyh_s_predoplatoi_internet'])
                if not successfully_create:
                    raise Http404
                return render_to_response("s8.html", context)
            except Exception, e:
                print e
                raise Http404
        else:
            raise Http404
    else:
        if person_obj.id in (2, 3,):
            successfully_create = create_package(request.user,
                                    reverse('add_inet_final'),
                                    reverse('my_inet'),
                                    param,
                                    ['dogovor_oferta'])
        else:
            successfully_create = create_package(request.user,
                                    reverse('add_inet_final'),
                                    reverse('my_inet'),
                                    param,
                                    ['telematic_data_centr', 'usluga_peredachi_dannyh_s_predoplatoi_internet'])
        if not successfully_create:
            raise Http404
        return HttpResponse(reverse('add_inet_final'))


def ajax_step_login(request):
    print 'ajax_step_login'
    context = {}
    errors = {}
    form_login = UserLoginForm2(request.GET)
    context['form_login'] = form_login
    print request.GET
    try:
        param = simplejson.loads((str(request.GET['data'])).strip('/'))
    except Exception, e:
        raise Http404
    context['data'] = simplejson.dumps(param)
    try:
        if form_login.is_valid():
            user = form_login.user
            if user:
                if user.is_active:
                    login(request, user)
                    tariff_obj = Tariff.objects.get(id=param['tariff'])
                    person_obj = tariff_obj.for_person.all()[0]
                    if person_obj.id in (2, 3,):
                        successfully_create = create_package(request.user,
                                                reverse('add_inet_final'),
                                                reverse('my_inet'),
                                                param,
                                                ['dogovor_oferta'])
                    else:
                        successfully_create = create_package(request.user,
                                                reverse('add_inet_final'),
                                                reverse('my_inet'),
                                                param,
                                                ['telematic_data_centr', 'usluga_peredachi_dannyh_s_predoplatoi_internet'])
                    if not successfully_create:
                        raise Http404
                    return render_to_response("s8.html", context)
            if user is None:
                errors['error_auth'] = True
                context['errors'] = errors
                return render_to_response("step_login2.html", context)
        else:
            errors['error_auth'] = True
            context['errors'] = errors
            return render_to_response("step_login2.html", context)
    except Exception, e:
        print e
    else:
        return render_to_response("step_login2.html", context)


def ajax_step_registration(request):
    print 'ajax_step_registration'
    context = {}
    errors = {}
    form_reg = UserRegistrationForm(request.GET)
    context['form_reg'] = form_reg
    try:
        param = simplejson.loads((str(request.GET['data'])).strip('/'))
    except Exception, e:
        print e
        raise Http404
    context['data'] = simplejson.dumps(param)

    if form_reg.is_valid():
        user = form_reg.save()
        ActionRecord.registrations.create_inactive_user_key(
            new_user=user,
            row_password=form_reg.get_row_password(),
            send_email=True,
            )
        tariff_obj = Tariff.objects.get(id=param['tariff'])
        person_obj = tariff_obj.for_person.all()[0]
        if person_obj.id in (2, 3,):
            successfully_create = create_package(user,
                                    reverse('add_inet_final'),
                                    reverse('my_inet'),
                                    param,
                                    ['dogovor_oferta'])
        else:
            successfully_create = create_package(user,
                                    reverse('add_inet_final'),
                                    reverse('my_inet'),
                                    param,
                                    ['telematic_data_centr', 'usluga_peredachi_dannyh_s_predoplatoi_internet'])
        if not successfully_create:
            raise Http404
        return render_to_response("s8_reg.html", context)
    else:
        errors['error_auth'] = True
        context['errors'] = errors
        return render_to_response("step_reg2.html", context)


@login_required
@limit_con_service([8, 10], 'internet')
@decorator_for_sign_applications()
def add_inet_final(request):
    print 'add_inet_final'
    user_obj = User.objects.get(username=request.user.username)
    profile = Profile.objects.get(user=user_obj)
    bac = profile.billing_account
    try:
        package_obj = Package_on_connection_of_service.objects.get(user=user_obj, activate=False, deactivate=False)
    except:
        raise Http404
    param = package_obj.data
    if not param:
        return HttpResponseRedirect(reverse("my_inet"))
    param = eval(param)
    tariff_obj = Tariff.objects.get(id=param['tariff'])
    zakaz = Zakazy(
                 bill_account=bac,
                 section_type=3,
                 status_zakaza_id=1,
                 service_type_id=8,
                 tariff=tariff_obj,
                 date_create=datetime.datetime.now(),
                 city=param['city'],
                 street=param['street'],
                 house=param['house'],
                 count_ip=param['count_static_ip'],
                 equipment=param['equipment'],
                 )
    zakaz.save()
    mailname = profile.get_company_name_or_family
    if profile.is_juridical:
        findocsign_queryset = package_obj.findoc_sign.filter(findoc__slug='telematic_data_centr')
        if not findocsign_queryset:
            findocsign_obj = get_signed(user_obj, "telematic_data_centr")
        else:
            findocsign_obj = findocsign_queryset[0]
    else:
        findocsign_queryset = package_obj.findoc_sign.filter(findoc__slug='dogovor_oferta')
        if findocsign_queryset:
            findocsign_obj = findocsign_queryset[0]
    fin_doc_zakaz = FinDocSignedZakazy(
                                       fin_doc=findocsign_obj,
                                       zakaz_id=zakaz.id,
                                       )
    fin_doc_zakaz.save()
    cost = float(cost_dc(zakaz.id))
    zakaz.cost = '%.2f' % cost
    zakaz.save()
    package_obj.activate = True
    package_obj.save()
    subject = u"Новый запрос на услугу 'Доступ в интернет'"
    # send_email(u"Новый запрос на услугу 'Доступ в интернет'", "Заказ № %s" % zakaz.id, settings.DEFAULT_FROM_EMAIL, ["Zz1n@globalhome.su", 'sales@globalhome.su', 'noc@globalhome.su'])
    try:
        group = Group.objects.get(name='Internet')
        users = group.user_set.all()
        maillist = []
        for us in users:
            if us.email:
                maillist.append(us.email)
    except:
        maillist = ["sssr@globalhome.su", 'noc@globalhome.su']
    mailhtml = u'''
                <table>
                    <tbody>
                        <tr>
                            <td>Логин</td><td>%s</td>
                        </tr>
                        <tr>
                            <td>Ф.И.О./Название</td><td>%s</td>
                        </tr>
                        <tr>
                            <td>Город</td><td>%s</td>
                        </tr>
                        <tr>
                            <td>Улица</td><td>%s</td>
                        </tr>
                        <tr>
                            <td>Дом</td><td>%s</td>
                        </tr>
                        <tr>
                            <td>Оборудование</td><td>%s</td>
                        </tr>
                        <tr>
                            <td>Кол-во статических ip</td><td>%s</td>
                        </tr>
                        <tr>
                            <td>Тариф</td><td>%s</td>
                        </tr>
                        <tr>
                            <td colspan="2"><a href="%s">Ссылка на заказ</a></td>
                        </tr>
                    </tbody>
                </table>
                ''' % (request.user.username, mailname, param['city'], param['street'],
                       param['house'], param['equipment'], param['count_static_ip'],
                       tariff_obj.name, "http://" + request.META['HTTP_HOST'] + "/admin/data_centr/zakazy/" + str(zakaz.id) + "/")

    msg = EmailMultiAlternatives(u'%s' % subject, '', settings.DEFAULT_FROM_EMAIL, maillist)
    msg.attach_alternative(mailhtml, "text/html")
    msg.send()


    request.notifications.add(_(u'Заявка на услугу "Доступ в интеренет" успешно сформирована!'), "success")
    return HttpResponseRedirect(reverse("my_inet"))


@login_required
@render_to('my_inet.html')
def my_inet(request):
    context = {}
    bill_acc = BillserviceAccount.objects.get(username=request.user.username)
    cont_zayavki = Zakazy.objects.filter(Q(bill_account=bill_acc.id) & Q(service_type=8) & (Q(status_zakaza=1) | Q(status_zakaza=6)) & Q(date_deactivation=None)).order_by('id')
    zayavki = []
    tariff_obj = Tariff.objects.get(id=26)
    for i in cont_zayavki:
        try:
            cost = i.cost
            if i.count_ip:
                cost += i.count_ip * tariff_obj.price_id.cost
            cost = '%.2f' % cost
        except:
            cost = 0
        date_create = datetime.datetime.strftime(i.date_create, "%d.%m.%Y %H:%M:%S")
        zayavki.append({"id":i.id, "tariff":i.tariff, "cost":cost, "date_create":date_create, "status_zayavki": i.status_zakaza})
    if list(zayavki) == []:
        context['check_zayavki'] = 'true'
        context['zayavki'] = []
    else:
        context['zayavki'] = zayavki
    cont_zakazy = Zakazy.objects.filter((Q(status_zakaza=2) | Q(status_zakaza=4)) & Q(bill_account=bill_acc.id) & Q(service_type=8)).exclude(date_activation=None).order_by('id')
    zakazy = []
    spis_zakaz_id = []
    for zakaz in cont_zakazy:
        spis_zakaz_id.append(zakaz.id)
    cont_pod_zakazy = Zakazy.objects.filter((Q(status_zakaza=2) | Q(status_zakaza=4)) & Q(bill_account=bill_acc.id) & Q(main_zakaz__in=spis_zakaz_id)).exclude(date_activation=None).order_by('id')
    dict_abbr_for_person = {1:u'ю', 2:u'ф', 3:u'к', 4:u'о'}
    dict_message_for_person = {1:u'Интернет для юридических лиц',
                               2:u'Интернет для физических лиц',
                               3:u'Интернет для коттеджных поселков',
                               4:u'Интернет для операторв связи'}
    for i in cont_zakazy:
        try:
            cost = i.cost
            cost = '%.2f' % cost
        except:
            cost = 0
        if i.date_deactivation:
            date_deactivation = datetime.datetime.strftime(i.date_deactivation, "%d.%m.%Y")
        else:
            date_deactivation = i.date_deactivation
        if i.date_activation > datetime.datetime.now():
            test_date_activation = True
        else:
            test_date_activation = False
        date_create = datetime.datetime.strftime(i.date_create, "%d.%m.%Y %H:%M:%S")
        date_activation = datetime.datetime.strftime(i.date_activation, "%d.%m.%Y")
        zakazy.append({"id":i.id, "service": '%s<br />(%s)' % (i.service_type, i.tariff), "cost":cost, "date_deactivation":date_deactivation, \
                        "date_activation":date_activation, "status_zakaza":i.status_zakaza.status, "test_date_activation":test_date_activation, \
                        "for_person":dict_abbr_for_person[i.tariff.for_person.all()[0].id], "message_for_person":dict_message_for_person[i.tariff.for_person.all()[0].id]})
    pod_zakazy = []
    for j in cont_pod_zakazy:
        ip = j.ip.all()[0]
        cost = j.cost
        if j.date_deactivation:
            date_deactivation = datetime.datetime.strftime(j.date_deactivation, "%d.%m.%Y")
        else:
            date_deactivation = j.date_deactivation
        if j.date_activation > datetime.datetime.now():
            test_date_activation = True
        else:
            test_date_activation = False
        date_activation = datetime.datetime.strftime(i.date_activation, "%d.%m.%Y")
        pod_zakazy.append({"id":j.id, "service":'%s<br />(%s)' % (j.service_type, ip), "cost":cost, "date_deactivation":date_deactivation, \
                           "date_activation":date_activation, "status_zakaza":j.status_zakaza.status, "main_zakaz":j.main_zakaz, \
                           "test_date_activation":test_date_activation})
    if not list(cont_zakazy):
        context['check_zakazy'] = 'true'
        context['zakazy'] = []
        context['pod_zakazy'] = []
    else:
        context['zakazy'] = zakazy
        context['pod_zakazy'] = pod_zakazy
    context['current_view_name'] = 'my_inet'
    context['now'] = datetime.datetime.now()
    return context


@login_required
def view_inet_zayavka(request, zayavka_id):
    print 'view_inet_zayavka'
    context = {}
    bill_acc = BillserviceAccount.objects.get(username=request.user.username)
    try:
        tariff_obj = Tariff.objects.get(id=26)
        zakaz_obj = Zakazy.objects.get(id=int(zayavka_id), bill_account=bill_acc)
        try:
            cost = zakaz_obj.cost
            if zakaz_obj.count_ip:
                cost += zakaz_obj.count_ip * tariff_obj.price_id.cost
            cost = '%.2f' % cost
        except:
            cost = 0
        zakaz_dict = {'id':zakaz_obj.id, 'tariff': zakaz_obj.tariff, 'city': zakaz_obj.city, 'street': zakaz_obj.street, \
                      'house': zakaz_obj.house, 'cost': cost}
        if not zakaz_obj.date_activation:
            if zakaz_obj.count_ip > 0:
                zakaz_dict['count_ip'] = zakaz_obj.count_ip
        else:
            ip = ''
            zakazy_ip_queryset = Zakazy.objects.filter(Q(main_zakaz=zakaz_obj.id) & Q(status_zakaza=2) & \
                                                       (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now())))
            for zakaz_ip in zakazy_ip_queryset:
                for ip_temp in zakaz_ip.ip.all():
                    if zakaz_ip.date_deactivation:
                        date_deactivation = datetime.datetime.strftime(zakaz_ip.date_deactivation, "%d.%m.%Y")
                        ip += str(ip_temp) + ' <font style="color: red;">до %s</font>' % date_deactivation + '<br />'
                    else:
                        ip += str(ip_temp) + '<br />'
            ip = ip.strip('<br />')
            zakaz_dict['ip'] = ip
        context['zakaz_obj'] = zakaz_dict
        subaccount = SubAccount.objects.filter(account=bill_acc)
        if subaccount:
            context['inet_login'] = subaccount[0].username
            context['inet_password'] = subaccount[0].password
    except Zakazy.DoesNotExist:
        raise Http404
    if zakaz_obj.status_zakaza_id == 1:
        context['title_modal'] = u'Просмотр заявки'
        context['zakaz'] = False
    elif zakaz_obj.status_zakaza_id == 2:
        context['title_modal'] = u'Просмотр заказа'
        context['zakaz'] = True
    return render_to_response("view_inet_zakaz.html", context)


@login_required
def del_zayavka(request, zayavka_id):
    profile = Profile.objects.get(user=request.user)
    bill_acc = BillserviceAccount.objects.get(username=request.user.username)
    try:
        zakaz_obj = Zakazy.objects.get(id=int(zayavka_id), bill_account=bill_acc)
    except Zakazy.DoesNotExist:
        raise Http404
    zakaz_obj.status_zakaza = Status_zakaza.objects.get(id=3)
    zakaz_obj.date_deactivation = datetime.datetime.now()
    zakaz_obj.save()
    if not profile.is_juridical:
        findoc_sign_queryset = FinDocSignedZakazy.objects.filter(zakaz_id=zakaz_obj.id, fin_doc__findoc__slug='dogovor_oferta')
        for findoc_sign in findoc_sign_queryset:
            findoc_sign.fin_doc.cancellation_date = datetime.datetime.now()
            findoc_sign.fin_doc.save()
    request.notifications.add(_(u"Заявка успешно удалена!"), "success")
    return HttpResponseRedirect(reverse('my_inet'))




def ajax_update_zakaz(request):
    if request.is_ajax() and request.user.is_superuser:
        zayavka_id = request.GET["zayavka_id"]
        try:
            zakaz = Zakazy.objects.get(id=zayavka_id)
        except Zakazy.DoesNotExist, exc:
            return HttpResponse(exc)
        zakaz.status_zakaza_id = 6
        zakaz.save()
        return HttpResponse("Success")




@login_required
@decorator_for_sign_applications()
def activation_zayavka(request, zayavka_id):
    bill_acc = BillserviceAccount.objects.get(username=request.user.username)
    profile_obj = Profile.objects.get(user=request.user)
    try:
        package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
    except Package_on_connection_of_service.DoesNotExist:
        try:
            zakaz_obj = Zakazy.objects.get(id=zayavka_id, bill_account=bill_acc)
        except Zakazy.DoesNotExist:
            raise Http404
        if zakaz_obj.date_activation:
            raise Http404
        spis_ip = IP.objects.filter(section_type=3, status_ip=1).order_by('price_id')
        if len(spis_ip) < zakaz_obj.count_ip:
            request.notifications.add(_(u"К сожалению мы не можем Вам выдать такое количество IP-адресов!"), "warning")
            return HttpResponseRedirect(reverse('my_inet'))

        slugs = ['akt_priemki_peredachi_vypoln_rabot']
        successfully_create = create_package(request.user,
                                '/account/internet/demands/activation/%s/' % zayavka_id,
                                reverse('my_inet'),
                                '',
                                slugs)
        if not successfully_create:
            raise Http404
        else:
            return HttpResponseRedirect('/account/internet/demands/activation/%s/' % zayavka_id)
    zakaz = Zakazy.objects.get(id=zayavka_id)
    zakaz.status_zakaza_id = 2
    zakaz.date_activation = datetime.datetime.now()
    zakaz.save()

    spis_ip = IP.objects.filter(section_type=3, status_ip=1).order_by('price_id')
    tariff_obj = Tariff.objects.get(id=26)

    spis_zakaz = []
    i = 0
    ip_address = '0.0.0.0'
    for ip in spis_ip:
        if i < zakaz.count_ip:
            i += 1
            ip_obj = IP.objects.get(name=ip)
            zakaz_ip = Zakazy(
                         main_zakaz=zakaz.id,
                         bill_account=zakaz.bill_account,
                         section_type=zakaz.section_type,
                         status_zakaza_id=2,
                         service_type_id=10,
                         tariff=tariff_obj,
                         date_create=datetime.datetime.now(),
                         date_activation=datetime.datetime.now(),
                         count_ip=1,
                         )
            zakaz_ip.save()
            zakaz_ip.ip.add(ip_obj)
            status_obj = Status_ip.objects.get(id=2)
            ip_obj.status_ip = status_obj
            ip_obj.save()
            zakaz_ip.save()
            cost = float(cost_dc(zakaz_ip.id))
            zakaz_ip.cost = '%.2f' % cost
            zakaz_ip.save()
            if profile_obj.is_juridical:
                findoc_sign_zakaz = FinDocSignedZakazy.objects.get(zakaz_id=zakaz.id, fin_doc__findoc__slug='telematic_data_centr')
            else:
                findoc_sign_zakaz = FinDocSignedZakazy.objects.get(zakaz_id=zakaz.id, fin_doc__findoc__slug='dogovor_oferta')
            findoc_sign_zakaz_ip = copy.copy(findoc_sign_zakaz)
            findoc_sign_zakaz_ip.id = None
            findoc_sign_zakaz_ip.zakaz_id = zakaz_ip.id
            findoc_sign_zakaz_ip.save()
            add_record_in_data_centr_payment(zakaz_ip)
            add_record_in_priority_of_services(zakaz_ip)
            spis_zakaz.append(zakaz_ip.id)
            ip_address_obj = zakaz_ip.ip.all()[0]
            ip_address = ip_address_obj.name
    SubAccount.set_account(bill_acc, ip_address, commit=True)
    bill_acc.set_tariff(zakaz.tariff.billing_tariff, datetime.datetime.now())
    cost = float(cost_dc(zakaz.id))
    zakaz.cost = '%.2f' % cost
    zakaz.save()
    spis_zakaz.append(zakaz.id)
    package_obj.activate = True
    package_obj.save()
    add_record_in_data_centr_payment(zakaz)
    add_record_in_priority_of_services(zakaz)
    spis_rules = Check.group_rules(profile_obj, [5, 11], 'type_check', zakaz.id)
    print 'spis_rules = %s' % spis_rules
    content_check_id = Check.create_check(request.user, spis_rules, False, spis_zakaz)
    print 'check = %s' % content_check_id
    dict_documents_for_send = add_document_in_dict_for_send({}, request.user.id, 'Check', content_check_id)
    send_mail_check(dict_documents_for_send)
    write_off_of_money(zakaz.bill_account, [zakaz.id])
    return HttpResponseRedirect(reverse('my_inet'))


@login_required
@decorator_for_sign_applications()
def internet_del_zakaz(request, zakaz_id):
    profile = Profile.objects.get(user=request.user)
    bill_acc = BillserviceAccount.objects.get(username=request.user.username)
    zakaz = Zakazy.objects.get(id=zakaz_id)
    try:
        package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
    except Package_on_connection_of_service.DoesNotExist:
        try:
            Zakazy.objects.get(id=zakaz_id, bill_account=bill_acc)
        except Zakazy.DoesNotExist:
            raise Http404
        data = ''
        if zakaz.service_type.id not in (10,):
            if profile.is_juridical:
                slugs = ['dop_soglashenie_k_dogovoru']
            else:
                slugs = ['dop_soglashenie_prekraschenie_internet']
        else:
            slugs = ['dop_soglashenie_izmenenie_internet']
            ip = zakaz.ip.all()[0]
            data = "{'spis_ip':'%s'}" % ip
        successfully_create = create_package(request.user,
                                '/account/internet/demands/zakaz/%s/' % zakaz_id,
                                reverse('my_inet'),
                                data,
                                slugs,)
        if not successfully_create:
            raise Http404
        else:
            return HttpResponseRedirect('/account/internet/demands/zakaz/%s/' % zakaz_id)
    try:
        now = datetime.datetime.now()
        date_next_start_month_temp = now + relativedelta(months=1)
        date_next_start_month = datetime.datetime(date_next_start_month_temp.year, date_next_start_month_temp.month, 1, 0, 0, 0)
        zakaz.date_deactivation = date_next_start_month
        zakaz.save()
        if not profile.is_juridical:
            findoc_sign_queryset = FinDocSignedZakazy.objects.filter(zakaz_id=zakaz.id, fin_doc__findoc__slug='dogovor_oferta')
            for findoc_sign in findoc_sign_queryset:
                findoc_sign.fin_doc.cancellation_date = date_next_start_month
                findoc_sign.fin_doc.save()
        if zakaz.date_deactivation == zakaz.date_activation:
            zakaz.status_zakaza_id = 3
            zakaz.save()
            if zakaz.service_type.id in (10,):
                ip_obj = IP.objects.get(name=zakaz.ip.all()[0])
                status_obj = Status_ip.objects.get(id=1)
                ip_obj.status_ip = status_obj
                ip_obj.save()
        zakazy_ip_queryset = Zakazy.objects.filter(main_zakaz=zakaz.id, date_deactivation=None, status_zakaza=2)
        for zakaz_obj_ip in zakazy_ip_queryset:
            zakaz_obj_ip.date_deactivation = date_next_start_month
            zakaz_obj_ip.save()
            if zakaz_obj_ip.date_deactivation == zakaz.date_activation:
                zakaz_obj_ip.status_zakaza_id = 3
                zakaz_obj_ip.save()
        package_obj.activate = True
        package_obj.save()
        if zakaz.service_type.id not in (10,):
            request.notifications.add(_(u"Услуга успешно деактивирована!"), "success")
        else:
            request.notifications.add(_(u"Конфигурация успешно изменена!"), "success")
    except:
        raise Http404
    return HttpResponseRedirect(reverse('my_inet'))


@login_required
@render_to('account_show_internet.html')
def account_show_internet(request):
    context = {}
    context['current_view_name'] = 'account_show_internet'
    context['profile_obj'] = Profile.objects.get(user=request.user)
    return context


@login_required
@render_to('account_internet_tariff_legal_entity.html')
def account_internet_legal_entity(request):
    context = {}
    context['current_view_name'] = 'account_show_internet'
    context['title'] = u'Интернет для юридических лиц'
    context['type_face'] = 'legal_entity'
    context = get_tariffs(context, [1])
    return context


@login_required
@render_to('account_internet_tariff_legal_entity.html')
def account_internet_physical(request):
    context = {}
    context['current_view_name'] = 'account_show_internet'
    context['title'] = u'Интернет для физических лиц'
    context['type_face'] = 'individual'
    context = get_tariffs(context, [2])
    return context


@login_required
@render_to('account_internet_tariff_legal_entity.html')
def account_internet_cottage_settlement(request):
    context = {}
    context['current_view_name'] = 'account_show_internet'
    context['title'] = u'Интернет для коттеджных поселков'
    context['type_face'] = 'cottage_settlement'
    context = get_tariffs(context, [3])
    return context


@login_required
def ajax_inet_configuration(request, zakaz_id):
    context = {}
    profile_obj = Profile.objects.get(user=request.user)
    bill_acc = BillserviceAccount.objects.get(id=profile_obj.billing_account_id)
    zakaz_obj = get_object_or_404(Zakazy, id=zakaz_id, bill_account=bill_acc, service_type__id=8)
    context['current_tariff'] = zakaz_obj.tariff.name
    if not zakaz_obj.date_deactivation and zakaz_obj.date_activation < datetime.datetime.now():
        context['can_change_tariff'] = True
    else:
        context['can_change_tariff'] = False
    persons_id = [i.id for i in zakaz_obj.tariff.for_person.all()]
    tariff_queryset = Tariff.objects.filter(service_type=8, for_person__id__in=persons_id, individual=False, archive=False).exclude(id=zakaz_obj.tariff.id)
    inet_tariff = []
    for tariff_obj in tariff_queryset:
        inet_tariff.append({'id': tariff_obj.id, 'name': u'%s (%s руб.)' % (tariff_obj.name, tariff_obj.price_id.cost / 1.18)})
    context['inet_tariff'] = inet_tariff
    context['zakaz_id'] = zakaz_id
    context['city'], context['street'], context['house'] = zakaz_obj.city, zakaz_obj.street, zakaz_obj.house
    if zakaz_obj.equipment:
        context['equipment'] = zakaz_obj.equipment.split(', ')
    else:
        context['equipment'] = False
    zakazy_ip_queryset = Zakazy.objects.filter(Q(main_zakaz=zakaz_obj.id) & Q(status_zakaza=2) & \
                                               (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now())))
    spis_ip = []
    tariff_obj = Tariff.objects.get(id=26)
    for zakaz_ip in zakazy_ip_queryset:
        for ip_temp in zakaz_ip.ip.all():
            if zakaz_ip.date_deactivation:
                date_deactivation = datetime.datetime.strftime(zakaz_ip.date_deactivation, "%d.%m.%Y")
            else:
                date_deactivation = ''
            spis_ip.append({'name': ip_temp.name, 'cost': u'%s руб.' % (tariff_obj.price_id.cost / 1.18), 'date_deactivation':date_deactivation})
    if spis_ip:
        context['spis_ip'] = spis_ip
        context['count_ip'] = len(spis_ip)
    else:
        context['spis_ip'] = False
        context['count_ip'] = 0
    range_ip = []
    for i in range(1, dict_profile_count_ip['%s' % profile_obj.is_juridical] + 1):
        range_ip.append({'count':i, 'count_with_cost': u'%s (%s руб.)' % (i, tariff_obj.price_id.cost * i / 1.18)})
    context['range_ip'] = range_ip
    context['permitted_count_ip'] = dict_profile_count_ip['%s' % profile_obj.is_juridical]
    return render_to_response("inet_configuration.html", context)


@login_required
@decorator_for_sign_applications()
def apply_configuration(request, zakaz_id):
    def configuration(data, spis_ip, new_ip, tariff_id):
        date_first_day_this_month = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
        date_first_day_next_month = date_first_day_this_month + relativedelta(months=1)
        if spis_ip:
            if data.has_key('spis_ip'):
                spis_ip = data['spis_ip'].split(',')
                for ip in spis_ip:
                    zakaz_ip_obj = get_object_or_404(Zakazy, main_zakaz=zakaz_id, bill_account=bill_acc, ip__name=ip)
                    zakaz_ip_obj.date_deactivation = date_first_day_next_month
                    zakaz_ip_obj.save()
                    if zakaz_ip_obj.date_deactivation == zakaz_ip_obj.date_activation:
                        zakaz_ip_obj.status_zakaza_id = 3
                        zakaz_ip_obj.save()
        if new_ip:
            if data.has_key('new_ip'):
                count_new_ip = int(data['new_ip'])
                spis_ip = IP.objects.filter(section_type=3, status_ip=1).order_by('price_id')
                if count_new_ip <= len(spis_ip):
                    tariff_obj = Tariff.objects.get(id=26)
                    i = 1
                    print spis_ip
                    for ip in spis_ip:
                        if i <= count_new_ip:
                            i += 1
                            ip_obj = IP.objects.get(name=ip)
                            if zakaz_obj.date_activation < now:
                                date_activation = now
                            else:
                                date_activation = zakaz_obj.date_activation
                            zakaz_ip = Zakazy(
                                         main_zakaz=zakaz_obj.id,
                                         bill_account=zakaz_obj.bill_account,
                                         section_type=zakaz_obj.section_type,
                                         status_zakaza_id=2,
                                         service_type_id=10,
                                         tariff=tariff_obj,
                                         date_create=now,
                                         date_activation=date_activation,
                                         date_deactivation=zakaz_obj.date_deactivation,
                                         count_ip=1,
                                         )
                            if zakaz_obj.date_deactivation:
                                zakaz_ip.date_deactivation = zakaz_obj.date_deactivation
                            zakaz_ip.save()
                            zakaz_ip.ip.add(ip_obj)
                            status_obj = Status_ip.objects.get(id=2)
                            ip_obj.status_ip = status_obj
                            ip_obj.save()
                            zakaz_ip.save()
                            cost = float(cost_dc(zakaz_ip.id))
                            zakaz_ip.cost = '%.2f' % cost
                            zakaz_ip.save()
                            if profile_obj.is_juridical:
                                findoc_sign_zakaz = FinDocSignedZakazy.objects.get(zakaz_id=zakaz_obj.id, fin_doc__findoc__slug='telematic_data_centr')
                            else:
                                findoc_sign_zakaz = FinDocSignedZakazy.objects.get(zakaz_id=zakaz_obj.id, fin_doc__findoc__slug='dogovor_oferta')
                            findoc_sign_zakaz_ip = copy.copy(findoc_sign_zakaz)
                            findoc_sign_zakaz_ip.id = None
                            findoc_sign_zakaz_ip.zakaz_id = zakaz_ip.id
                            findoc_sign_zakaz_ip.save()
                            if zakaz_obj.date_activation < now:
                                add_record_in_data_centr_payment(zakaz_ip)
                                add_record_in_priority_of_services(zakaz_ip)
                            subaccount = SubAccount.objects.filter(account=zakaz_ip.bill_account)
                            if subaccount:
                                ip_address = zakaz_ip.ip.all()[0]
                                print ip_address, type(ip_address)
                                subaccount[0].vpn_ip_address = ip_address.name
                                subaccount[0].save()
                else:
                    request.notifications.add(_(u"К сожалению мы не можем Вам выдать такое количество IP-адресов!"), "warning")
        if tariff_id:
            if data.has_key('tariff_id'):
                tariff_obj = get_object_or_404(Tariff, id=int(data['tariff_id']))
                new_zakaz_obj = copy.copy(zakaz_obj)
                new_zakaz_obj.id = None
                new_zakaz_obj.tariff = tariff_obj
                new_zakaz_obj.date_create = date_first_day_next_month
                new_zakaz_obj.date_activation = date_first_day_next_month
                new_zakaz_obj.save()
                cost = float(cost_dc(new_zakaz_obj.id))
                new_zakaz_obj.cost = '%.2f' % cost
                new_zakaz_obj.save()

                if profile_obj.is_juridical:
                    slug = 'telematic_data_centr'
                else:
                    slug = 'dogovor_oferta'
                fin_doc_zakaz = FinDocSignedZakazy.objects.get(Q(zakaz_id=zakaz_obj.id) & \
                                                               Q(fin_doc__findoc__slug=slug))
                new_fin_doc_zakaz = copy.copy(fin_doc_zakaz)
                new_fin_doc_zakaz.id = None
                new_fin_doc_zakaz.zakaz_id = new_zakaz_obj.id
                new_fin_doc_zakaz.save()

                zakazy_ip_queryset = Zakazy.objects.filter(Q(main_zakaz=zakaz_obj.id) & Q(status_zakaza=2) & \
                                                           (Q(date_deactivation=None) | Q(date_deactivation__gt=date_first_day_next_month)))
                for zakaz_obj_ip in zakazy_ip_queryset:
                    new_zakaz_obj_ip = copy.copy(zakaz_obj_ip)
                    new_zakaz_obj_ip.id = None
                    new_zakaz_obj_ip.main_zakaz = new_zakaz_obj.id
                    new_zakaz_obj_ip.date_create = date_first_day_next_month
                    new_zakaz_obj_ip.date_activation = date_first_day_next_month
                    new_zakaz_obj_ip.save()
                    new_zakaz_obj_ip.ip.add(*zakaz_obj_ip.ip.all())
                    new_zakaz_obj_ip.save()
                    zakaz_obj_ip.date_deactivation = date_first_day_next_month
                    zakaz_obj_ip.save()
                    new_fin_doc_zakaz_ip = copy.copy(fin_doc_zakaz)
                    new_fin_doc_zakaz_ip.id = None
                    new_fin_doc_zakaz_ip.zakaz_id = new_zakaz_obj_ip.id
                    new_fin_doc_zakaz_ip.save()
                zakaz_obj.date_deactivation = date_first_day_next_month
                zakaz_obj.save()
        package_obj.activate = True
        package_obj.save()
        findocsign_obj = package_obj.findoc_sign.all()[0]
        fin_doc_zakaz = FinDocSignedZakazy(
                                   fin_doc=findocsign_obj,
                                   zakaz_id=zakaz_obj.id,
                                   )
        fin_doc_zakaz.save()
    profile_obj = Profile.objects.get(user=request.user)
    bill_acc = BillserviceAccount.objects.get(id=profile_obj.billing_account_id)
    zakaz_obj = get_object_or_404(Zakazy, id=zakaz_id, bill_account=bill_acc)
    try:
        package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
    except Package_on_connection_of_service.DoesNotExist:
        if not request.GET.has_key('spis_ip') and not request.GET.has_key('new_ip') and not request.GET.has_key('tariff_id'):
            raise Http404
        request_get = {}
        for key, value in request.GET.iteritems():
            request_get[key.encode("utf-8")] = value.encode("utf-8")
        successfully_create = create_package(request.user, \
                                '/account/internet/demands/apply_configuration/%s/' % zakaz_id,
                                reverse('my_inet'),
                                '%s' % request_get,
                                ['dop_soglashenie_izmenenie_internet'],)
        if not successfully_create:
            raise Http404
        else:
            return HttpResponseRedirect('/account/internet/demands/apply_configuration/%s/' % zakaz_id)
    now = datetime.datetime.now()
    data_temp = eval(package_obj.data)
    data = data_temp
    if zakaz_obj.date_activation > now:
        configuration(data, True, True, True)
    elif (data.has_key('new_ip') and (data.has_key('spis_ip') or data.has_key('tariff_id'))):
        configuration(data, False, True, False)
        del data['new_ip']
        for key, value in data.iteritems():
            data_temp[key.encode("utf-8")] = value.encode("utf-8")
        successfully_create = create_package(request.user, \
                                '/account/internet/demands/apply_configuration/%s/' % zakaz_id, \
                                reverse('my_inet'), \
                                '%s' % data_temp,
                                ['dop_soglashenie_izmenenie_internet'],)
        if not successfully_create:
            raise Http404
        else:
            return HttpResponseRedirect('/account/internet/demands/apply_configuration/%s/' % zakaz_id)
    else:
        configuration(data, True, True, True)
    request.notifications.add(_(u"Конфигурация успешно изменена!"), "success")
    return HttpResponseRedirect(reverse("my_inet"))




@login_required
@render_to('test.html')
def test(request):
    bill_acc = BillserviceAccount.objects.get(id=30)
    sa = SubAccount.generate(account=bill_acc, commit=True)
    return {'stat': sa}


@login_required
@decorator_for_sign_applications()
def create_zakaz_free_inet(request):
    user_obj = request.user
    bill_acc = BillserviceAccount.objects.get(username=request.user.username)
    profile_obj = Profile.objects.get(user=request.user)
    try:
        package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
    except Package_on_connection_of_service.DoesNotExist:
        raise Http404

    param = package_obj.data
    if not param:
        return HttpResponseRedirect(reverse("my_inet"))
    param = eval(param)
    tariff_obj = Tariff.objects.get(id=param['tariff_id'])
    zakaz = Zakazy(
                 bill_account=bill_acc,
                 section_type=3,
                 status_zakaza_id=2,
                 service_type_id=8,
                 tariff=tariff_obj,
                 date_create=datetime.datetime.now(),
                 date_activation=datetime.datetime.now(),
                 city=Internet_city.objects.get(id=param['city']).city,
                 street=Internet_street.objects.get(id=param['street']).street,
                 house=Internet_house.objects.get(id=param['house']).house,
                 )
    zakaz.save()
    if profile_obj.is_juridical:
        findocsign_queryset = package_obj.findoc_sign.filter(findoc__slug='telematic_data_centr')
        if not findocsign_queryset:
            findocsign_obj = get_signed(user_obj, "telematic_data_centr")
        else:
            findocsign_obj = findocsign_queryset[0]
    else:
        findocsign_queryset = package_obj.findoc_sign.filter(findoc__slug='dogovor_oferta')
        if findocsign_queryset:
            findocsign_obj = findocsign_queryset[0]
    fin_doc_zakaz = FinDocSignedZakazy(
                                       fin_doc=findocsign_obj,
                                       zakaz_id=zakaz.id,
                                       )
    fin_doc_zakaz.save()

    spis_ip = IP.objects.filter(section_type=3, status_ip=1).order_by('price_id')
    tariff_obj = Tariff.objects.get(id=26)

    spis_zakaz = []
    i = 0
    ip_address = '0.0.0.0'
    for ip in spis_ip:
        if i < zakaz.count_ip:
            i += 1
            ip_obj = IP.objects.get(name=ip)
            zakaz_ip = Zakazy(
                         main_zakaz=zakaz.id,
                         bill_account=zakaz.bill_account,
                         section_type=zakaz.section_type,
                         status_zakaza_id=2,
                         service_type_id=10,
                         tariff=tariff_obj,
                         date_create=datetime.datetime.now(),
                         date_activation=datetime.datetime.now(),
                         count_ip=1,
                         )
            zakaz_ip.save()
            zakaz_ip.ip.add(ip_obj)
            status_obj = Status_ip.objects.get(id=2)
            ip_obj.status_ip = status_obj
            ip_obj.save()
            zakaz_ip.save()
            cost = float(cost_dc(zakaz_ip.id))
            zakaz_ip.cost = '%.2f' % cost
            zakaz_ip.save()
            if profile_obj.is_juridical:
                findoc_sign_zakaz = FinDocSignedZakazy.objects.get(zakaz_id=zakaz.id, fin_doc__findoc__slug='telematic_data_centr')
            else:
                findoc_sign_zakaz = FinDocSignedZakazy.objects.get(zakaz_id=zakaz.id, fin_doc__findoc__slug='dogovor_oferta')
            findoc_sign_zakaz_ip = copy.copy(findoc_sign_zakaz)
            findoc_sign_zakaz_ip.id = None
            findoc_sign_zakaz_ip.zakaz_id = zakaz_ip.id
            findoc_sign_zakaz_ip.save()
            add_record_in_data_centr_payment(zakaz_ip)
            add_record_in_priority_of_services(zakaz_ip)
            spis_zakaz.append(zakaz_ip.id)
            ip_address_obj = zakaz_ip.ip.all()[0]
            ip_address = ip_address_obj.name
    SubAccount.set_account(bill_acc, ip_address, commit=True)
    bill_acc.set_tariff(zakaz.tariff.billing_tariff, datetime.datetime.now())
    zakaz.cost = 0
    zakaz.save()
    spis_zakaz.append(zakaz.id)
    package_obj.activate = True
    package_obj.save()
    add_record_in_data_centr_payment(zakaz)
    add_record_in_priority_of_services(zakaz)
    spis_rules = Check.group_rules(profile_obj, [5, 11], 'type_check', zakaz.id)
    print 'spis_rules = %s' % spis_rules
    content_check_id = Check.create_check(request.user, spis_rules, False, spis_zakaz)
    print 'check = %s' % content_check_id
    dict_documents_for_send = add_document_in_dict_for_send({}, request.user.id, 'Check', content_check_id)
    send_mail_check(dict_documents_for_send)
    write_off_of_money(zakaz.bill_account, [zakaz.id])
    request.notifications.add(_(u'Услугу "Доступ в интеренет" успешно добавлена!'), "success")
    return HttpResponseRedirect(reverse('my_inet'))
