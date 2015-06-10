# coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import login
from lib.decorators import render_to, login_required, limit_con_service
from django.shortcuts import render_to_response
from externalnumbers.models import ExternalNumber, ExternalNumberTarif, Number800Payments
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from datetime import datetime
from findocs.views import create_package
from django.contrib.auth.models import User
from django.utils import simplejson
from findocs import get_signed
from findocs.models import FinDocSignedZakazy, Package_on_connection_of_service, FinDocSigned
from telnumbers.models import TelNumbersGroup, TelNumber
from account.models import Profile, ActionRecord
from account.forms import UserLoginForm2, UserRegistrationForm
from dateutil.relativedelta import relativedelta
from data_centr.models import Zakazy, Tariff
from data_centr.views import cost_dc
from findocs import decorator_for_sign_applications
from telnumbers.forms import SelectWithAddGroupForm, group_widget_data
from externalnumbers.consts import NUMBER800_REGION, RESERVATION_CONNECT_PRICE_ID, RESERVATION_SERVICE_TYPE, RESERVATION_TARIFF_ID, PAUSE_SERVICE_TYPE, PAUSE_TARIFF_ID, PAUSE_CONNECT_PRICE_ID, NUMBER800_PRECODE, ABON_SERVICE_TYPE
from page.models import Send_mail
from lib.mail import EmailMultiAlternatives
#import ho.pisa as pisa
from django.template.loader import get_template
from django.template import Context
from adminmail.models import Letter
from lib.xact import xact
import log
import StringIO
import random
import string
import os
from django.conf import settings

STATUS_ZAKAZA_ACTIVE = 2
STATUS_ZAKAZA_DEACTIVATED = 3
STATUS_ZAKAZA_DISABLED = 5
EXCLUDE_TARIFFS = (50, 51, 52, 53, 54, 55, 56, 57)

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html  = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode('utf-8')), result, show_error_as_pdf = True, encoding = 'UTF-8')
    if not pdf.err:
        return result.getvalue()
    return False

def number_format(number):
    return "8-" + number[1:4] + "-" + number[4:]

def doc_to_pdf(doc):
    doc_text = doc.signed_text.encode('utf-8')
    filename = os.path.join("media", "doc", "800_doc-%s" % doc.id + ".pdf")
    pdf_str = render_to_pdf('pdf_document_template.html', { 'document': doc_text, 'MEDIA_ROOT': settings.MEDIA_ROOT })
    pdf_file = open(filename, 'w')
    pdf_file.write(pdf_str)
    pdf_file.close()
    return filename

def send_docs(user, findocs, code_mail):
    profile = user.get_profile()
    if profile.mail_for_document:
        email = profile.mail_for_document
    else:
        email = profile.user.email
    files = [doc_to_pdf(doc) for doc in findocs]
    letter = Letter.objects.get(code = code_mail)
    mail = EmailMultiAlternatives(letter.subject, letter.texttemplate, settings.DEFAULT_FROM_EMAIL, [email])
    for filename in files:
        mail.attach_file(filename)
    if settings.SEND_EMAIL: mail.send()
    mail = Send_mail(
        subject = letter.subject,
        message = letter.texttemplate,
        date = datetime.now(),
        user_id = user.id,
        email = email,
        spis_file = ', '.join(files),
        status_mail = True)
    mail.save()
    return email

def bind_number(number, group = None, region = NUMBER800_REGION, account = None, free = False, reserved = False, date = None, user = False):
    number.phone_numbers_group = group
    number.region = region
    number.account = account
    number.is_free = free
    number.is_reserved = reserved
    number.assigned_at = date
    number.date_deactivation = None
    if user != False:
        number.auth_user = user
    number.save()

def get_number_info(number):
    now = datetime.now()
    tariff = ExternalNumberTarif.objects.get(pk = number.tarif_group)
    payments = Number800Payments.objects.get(Q(end_date = None) | Q(end_date__gt = now),tariff = tariff, start_date__lt = now)
    return { 'tariff': tariff.name, 'number': number.number, 'abon': payments.abon, 'connect': payments.connect, 'guaranteed': payments.guaranteed }

def get_number_status(number, account, now):
    STATUS = { ABON_SERVICE_TYPE: 'abon', RESERVATION_SERVICE_TYPE: 'reservation', PAUSE_SERVICE_TYPE: 'pause' }
    zakazy = Zakazy.objects.filter(Q(date_deactivation__gte=now) | Q(date_deactivation=None), ~Q(status_zakaza_id=STATUS_ZAKAZA_DEACTIVATED), ext_numbers=number, bill_account=account, service_type_id__in=(ABON_SERVICE_TYPE, RESERVATION_SERVICE_TYPE, PAUSE_SERVICE_TYPE))
    zakaz = None
    if len(zakazy) == 1:
        zakaz = zakazy[0]
    if zakaz:
        return STATUS[zakaz.service_type_id]
    else:
        return STATUS[ABON_SERVICE_TYPE]

def package(user, data, url_sign):
    return create_package(user, url_sign, reverse('8800_list'),
        data, ['telematic_services_contract', '800_contract'])#, '800_forma'])

def create_group(profile, account):
    try:  # Берем один вн. номер у пользователя для новой группы
        internal_number = TelNumber.objects.filter(account=account).latest('id')
    except:  # Если нету вн. номеров, то добавляем номер с рандомным паролем
        next_number = TelNumber.get_next_free_number(profile.is_hostel, profile.is_juridical)
        password = ''.join(random.choice('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM') for x in range(4))
        internal_number = TelNumber.create(
            account,
            next_number=next_number,
            is_juridical=profile.is_juridical,
            password=password,
            person_name=account.username,
            internal_phone=int(next_number[0] + next_number[-3:]),  # короткий номер
        )
        internal_number.save()
    groups = TelNumbersGroup.objects.filter(account=account)
    counter = 1
    while groups.filter(name='group_%s' % string.zfill(counter, 4)):
        counter += 1
    group = TelNumbersGroup.create('group_' + string.zfill(counter, 4), account, [internal_number])
    group.save()
    return group


def create_zakaz(account, service_type, external_number, end_date = None):
    now = datetime.now()
    if service_type == ABON_SERVICE_TYPE:
        tariff = ExternalNumberTarif.objects.get(id = external_number.tarif_group)
        data_centr_price_connection = tariff.data_centr_price_connection.id
        data_centr_tariff = tariff.data_centr_tariff.id
    elif service_type == RESERVATION_SERVICE_TYPE:
        data_centr_price_connection = RESERVATION_CONNECT_PRICE_ID
        data_centr_tariff = RESERVATION_TARIFF_ID
    elif service_type == PAUSE_SERVICE_TYPE:
        data_centr_price_connection = PAUSE_CONNECT_PRICE_ID
        data_centr_tariff = PAUSE_TARIFF_ID
    zakaz = Zakazy(bill_account = account, section_type = 1, status_zakaza_id = STATUS_ZAKAZA_ACTIVE,
        service_type_id = service_type, tariff_id = data_centr_tariff, date_activation = now, 
        connection_cost_id = data_centr_price_connection, date_create = now, date_deactivation = end_date)
    zakaz.save()
    zakaz.ext_numbers.add(external_number)
    cost = float(cost_dc(zakaz.id))
    zakaz.cost = '%.2f' % cost
    zakaz.save()
    return zakaz

def deactivate_zakaz(account, service_type, external_number, date_deactivation = None):
    now = datetime.now()
    zakaz = Zakazy.objects.get(Q(date_deactivation = None) | Q(date_deactivation__gte = now), ext_numbers = external_number, bill_account = account, status_zakaza_id = STATUS_ZAKAZA_ACTIVE, service_type_id = service_type)
    if date_deactivation:
        zakaz.date_deactivation = date_deactivation
    else:
        zakaz.date_deactivation = now
        zakaz.status_zakaza_id = STATUS_ZAKAZA_DEACTIVATED
    zakaz.save()
    return zakaz

def join_zakaz_and_docs(package, zakaz, user):
    # findocsign_queryset = package.findoc_sign.filter(findoc__slug = '800_forma')
    # findocsign_obj = findocsign_queryset[0]
    # fin_doc_zakaz = FinDocSignedZakazy(fin_doc = findocsign_obj, zakaz_id = zakaz.id)
    # fin_doc_zakaz.save()
    findocsign_queryset = package.findoc_sign.filter(findoc__slug = '800_contract')
    if findocsign_queryset:
        findocsign_obj = findocsign_queryset[0]
    else:
        findocsign_obj = get_signed(user, "800_contract")
    fin_doc_zakaz = FinDocSignedZakazy(fin_doc = findocsign_obj, zakaz_id = zakaz.id,)
    fin_doc_zakaz.save()

@login_required
@render_to("number800_list.html")
def list(request):
    if request.POST.has_key('add'):
        return HttpResponseRedirect(reverse('8800_add'))
    profile = request.user.get_profile()
    account = profile.billing_account
    context = {}
    context['is_juridical'] = profile.is_juridical
    if profile.is_juridical:
        now = datetime.now()
        start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        numbers = ExternalNumber.objects.filter(account=account, region=NUMBER800_REGION, is_free=False)
        context['numbers'] = []
        for number in numbers:
            zakaz = Zakazy.objects.filter(Q(date_deactivation__gte=now) | Q(date_deactivation=None), ~Q(status_zakaza_id=STATUS_ZAKAZA_DEACTIVATED), ~Q(status_zakaza_id=STATUS_ZAKAZA_DISABLED), ext_numbers=number, bill_account=account)
            if not zakaz: continue
            tariff = ExternalNumberTarif.objects.get(pk=number.tarif_group)
            context['numbers'].append({
                'id': number.id,
                'number': number.number,
                'group': number.phone_numbers_group.name,
                'tariff': tariff.name,
                'state': get_number_status(number, account, now),
                'date_deactivation': zakaz[0].date_deactivation.strftime("%d.%m.%Y") if zakaz[0].date_deactivation else None,
                })
    return context

@login_required
@render_to("number800_group.html")
def edit(request, number_id):
    if request.POST.has_key('cancel'):
        return HttpResponseRedirect(reverse("8800_list"))
    profile = request.user.get_profile()
    account = profile.billing_account
    try:
        external_number = ExternalNumber.objects.get(pk=number_id, account=account)
    except ExternalNumber.DoesNotExist:
        request.notifications.add(_(u"Произошла непредвиденная ошибка, обратитесь в техподдержку!"), "warning")
        return HttpResponseRedirect(reverse("8800_list"))
    context = {}
    context['number'] = external_number.number
    group = external_number.phone_numbers_group
    groups = account.telnumbersgroup_set.all()
    context['group'] = groups
    choices, settings = group_widget_data(groups, group.id)
    if request.POST.has_key('submit'):
        form = SelectWithAddGroupForm(request.POST.copy(), choices = choices, settings = settings)
        if form.is_valid():
            group_id = form.cleaned_data.get("user_groups")
            try:
                group = TelNumbersGroup.objects.get(id=group_id)
            except:
                request.notifications.add(u'Не удалось изменить группу, обратитесь в техподдержку!', 'warning')
            else:
                external_number.phone_numbers_group = group
                external_number.save(no_assigned_at_save = True)
                request.notifications.add(_(u"Changes have been successfully applied"), "success")
            return HttpResponseRedirect(reverse("8800_list"))
    form = SelectWithAddGroupForm(choices=choices, settings=settings)
    context['form'] = form
    return context

@render_to("number800_add.html")
def add(request):
    def step_connect(numbers, user, group):#, connect = True):
        number_list = []
        for number_id in numbers:
            external_number = ExternalNumber.objects.get(id = int(number_id))
            bind_number(external_number, reserved = True, date = datetime.now(), user = user.id)
            number_list.append(external_number.number)
        url = reverse('8800_connect')# if connect else reverse('8800_reservation')
        param = {
            'redirect_after_reg': url,
            'numbers': number_list,
            'number800': 'connect'
        }
        if group: param['group_id'] = group
        data = simplejson.dumps(param)
        successfully_create = package(user, data, url)
        return data, successfully_create

    def step_registration_or_authorization(numbers, action, registration):
        number_list = []
        now = datetime.now()
        for number_id in numbers:
            external_number = ExternalNumber.objects.get(id = number_id)
            bind_number(external_number, reserved = True, date = now)
            number_list.append(external_number.number)
        param = { 'numbers': number_list, 'action': action }
        data = simplejson.dumps(param)
        form = { 'form_reg': UserRegistrationForm() } if registration else { 'form_login': UserLoginForm2() }
        url = 'number800_reg.html' if registration else 'number800_auth.html'
        return form, data, url

    if request.POST.has_key('cancel'):
        return HttpResponseRedirect(reverse('8800_list'))
    context = { 'user': None }
    try:
        profile = request.user.get_profile()
        account = profile.billing_account
        context['not_juridical'] = not profile.is_juridical
        context['user'] = request.user.username
    except:
        account = None
    if request.POST.has_key('next_step'):
        step = request.POST.get('next_step')
        numbers = filter(None , request.POST.get('numbers', '').split(','))
        if numbers:
            if step in ('connect',):
                data, successfully_create = step_connect(numbers, request.user, request.POST.get('group', None))#, connect = step == 'connect')
                context['data'] = data
                if successfully_create:
                    return render_to_response("s8.html", context)
            elif step == 'reservation':
                now = datetime.now()
                for number_id in numbers:
                    external_number = ExternalNumber.objects.get(id = int(number_id))
                    if request.POST.has_key('group'):
                        group = TelNumbersGroup.objects.get(id = request.POST.get('group'))
                    else:
                        group = create_group(profile, account)
                    bind_number(external_number, reserved = True, group = group, account = account, date = now)
                    create_zakaz(account, RESERVATION_SERVICE_TYPE, external_number, end_date = datetime.now() + relativedelta(days = 10))
                return render_to_response("s8.html", { 'page': '8800/' })
            elif step in ('registration', 'authorization'):
                form, data, url = step_registration_or_authorization(numbers, request.POST.get('action'), step == 'registration')
                context.update(form)
                context['data'] = data
                return render_to_response(url, context)
        else:
            context['not_numbers'] = True
    if account:
        context['groups'] = TelNumbersGroup.objects.filter(account=account)
    tariffs = ExternalNumberTarif.objects.filter(precode=NUMBER800_PRECODE).exclude(id__in=EXCLUDE_TARIFFS)
    tariff_list = []
    for tariff in tariffs:
        numbers = [{
            'id': n.id,
            'number': n.number
        } for n in ExternalNumber.objects.filter(Q(tarif_group = tariff.id) & Q(is_free = True))]
        tariff_payments = Number800Payments.objects.filter(Q(tariff = tariff) & Q(start_date__lt = datetime.now())).latest('start_date')
        guaranteed_cost = tariff_payments.guaranteed
        category_cost = tariff_payments.category
        abon_cost = tariff_payments.abon
        connect_cost = tariff_payments.connect
        tariff_list.append({
            'id': tariff.id,
            'name': tariff.name,
            'numbers': numbers,
            'connect_payment': connect_cost,
            'category_payment': category_cost,
            'abon_payment': abon_cost,
            'guaranteed_payment': guaranteed_cost,
        })
    tariff_list = sorted(tariff_list, key=lambda x: (-x['abon_payment'], x['guaranteed_payment']))
    context['tariffs'] = tariff_list
    return context

@login_required
@limit_con_service([3], 'telephony')
@decorator_for_sign_applications()
def connect(request, param={}):
    user = request.user
    profile = user.get_profile()
    package = Package_on_connection_of_service.objects.get(user = user, activate = False, deactivate = False)
    if not param:
        param = package.data
    if not param:
        request.notifications.add(_(u"Произошла непредвиденная ошибка, обратитесь в техподдержку!"), "warning")
        return HttpResponseRedirect(reverse("8800_list"))
    param = eval(param)
    account = profile.billing_account
    now = datetime.now()
    try:
        with xact():
            with xact(using = settings.BILLING_DB):
                if param.has_key('group_id'): # Получаем группу
                    group = TelNumbersGroup.objects.get(pk = param['group_id'])
                else:
                    group = create_group(profile, account)
                for number in param['numbers']:
                    external_number = ExternalNumber.objects.get(number = number)
                    bind_number(external_number, group = group, region = NUMBER800_REGION, account = account, date = now)
                    tariff =  ExternalNumberTarif.objects.get(id = external_number.tarif_group)
                    zakaz = create_zakaz(account, ABON_SERVICE_TYPE, external_number)
                    join_zakaz_and_docs(package, zakaz, profile.user)
                findocs = [FinDocSigned.objects.filter(findoc__slug = '800_contract', signed_by = user).order_by('-id')[0]]
                send_to = send_docs(user, findocs, 'INSTRUCTION_800')
                package.activate = True
                package.save()
                request.notifications.add(u'На %s отправлено письмо с дальнейшими инструкциями для подключения номера!' % send_to, "success")
    except Exception, e:
        package.deactivate = True
        package.save()
        log.add("number800.py connect Exception: %s" % e)
        request.notifications.add(_(u"Произошла непредвиденная ошибка, обратитесь в техподдержку!"), "warning")
    return HttpResponseRedirect(reverse("8800_list"))

def authorization(request):
    context = {}
    param = simplejson.loads((str(request.GET['data'])).strip('/'))
    form = UserLoginForm2(request.GET)
    context['data'] = simplejson.dumps(param)
    context['form_login'] = form
    if form.is_valid():
        action = param.get('action', '')
        user = form.user
        profile = Profile.objects.get(user = user)
        if user and user.is_active and profile.is_juridical:
            login(request, user)
            user = User.objects.get(username = user)
            if action == "connect":
                number_list = []
                for number in param['numbers']:
                    external_number = ExternalNumber.objects.get(number = number)
                    bind_number(external_number, reserved = True, date = datetime.now(), user = user.id)
                    number_list.append(external_number.number)
                param = {
                    'redirect_after_reg': reverse('8800_connect'),
                    'numbers': number_list,
                    'number800': action,
                }
                context['data'] = simplejson.dumps(param)
                successfully_create = package(request.user, context['data'], reverse('8800_connect'))
            elif action == "reservation":
                account = profile.billing_account
                now = datetime.now()
                for number in param['numbers']:
                    external_number = ExternalNumber.objects.get(number = number)
                    group = create_group(profile, account)
                    bind_number(external_number, reserved = True, group = group, account = account, date = now)
                    create_zakaz(account, RESERVATION_SERVICE_TYPE, external_number, end_date = datetime.now() + relativedelta(days = 10))
                return render_to_response("s8.html", { 'page': '8800/' })
            if not successfully_create:
                raise Http404
            return render_to_response("s8.html", context)
        else:
            context['errors'] = { 'error_auth': True, 'error_juridical': not profile.is_juridical if user else False }
            return render_to_response("number800_auth.html", context)
    else:
        context['errors'] = { 'error_auth': True, 'error_juridical': False }
        return render_to_response("number800_auth.html", context)

def registration(request):
    context = {}
    param = simplejson.loads((str(request.GET['data'])).strip('/'))
    param['redirect_after_reg'] = reverse('8800_connect')
    context['data'] = simplejson.dumps(param)
    form = UserRegistrationForm(request.GET)
    context['form_reg'] = form
    if form.is_valid():
        action = param.get('action', '')
        if form.cleaned_data['profile'] == 2:
            user = form.save()
            if action == "connect":
                number_list = []
                for number in param['numbers']:
                    external_number = ExternalNumber.objects.get(number = number)
                    bind_number(external_number, reserved = True, date = datetime.now(), user = user.id)
                    number_list.append(external_number.number)
                param = {
                    'redirect_after_reg': reverse('8800_connect'),
                    'numbers': number_list,
                    'number800': action,
                }
                context['data'] = simplejson.dumps(param)
                ActionRecord.registrations.create_inactive_user_key(
                    new_user = user,
                    row_password = form.get_row_password(),
                    send_email = True,
                )
                successfully_create = package(user, context['data'], reverse('8800_connect'))
            elif action == "reservation":
                account = profile.billing_account
                now = datetime.now()
                for number in param['numbers']:
                    external_number = ExternalNumber.objects.get(number = number)
                    group = create_group(profile, account)
                    bind_number(external_number, reserved = True, group = group, account = account, date = now)
                    create_zakaz(account, RESERVATION_SERVICE_TYPE, external_number, end_date = datetime.now() + relativedelta(days = 10))
                return render_to_response("s8.html", { 'page': '8800/' })
            if not successfully_create:
                raise Http404
            return render_to_response("s8_reg.html", context)
        context['errors'] = { 'error_jur' : True }
        return render_to_response("number800_reg.html", context)
    else:
        context['errors'] = { 'error_auth' : True }
        return render_to_response("number800_reg.html", context)

@login_required
def number_action(request, number_id):
    profile = request.user.get_profile()
    account = profile.billing_account
    try:
        external_number = ExternalNumber.objects.get(pk=number_id, account=account)
    except ExternalNumber.DoesNotExist:
        request.notifications.add(_(u"Произошла непредвиденная ошибка, обратитесь в техподдержку!"), "warning")
        return HttpResponseRedirect(reverse("8800_list"))
    action = request.GET['action']
    if action == 'reserved_connect':
        url = reverse('8800_reserved_connect')
        data = simplejson.dumps({
            'redirect_after_reg': url,
            'numbers': [external_number.number],
            'number800': action
        })
        package(request.user, data, url)
    elif action == 'reserved_free':
        url = reverse('8800_reserved_free')
    elif action == 'delete':
        url = reverse('8800_delete')
    elif action == 'pause':
        url = reverse('8800_pause')
    elif action == 'pause_connect':
        url = reverse('8800_pause_connect')
    elif action == 'pause_delete':
        url = reverse('8800_pause_delete')
    return HttpResponseRedirect(url)

@login_required
@render_to("number800_manage.html")
@decorator_for_sign_applications()
def reserved_connect(request):
    user = request.user
    package = Package_on_connection_of_service.objects.get(user = user, activate = False, deactivate = False)
    param = eval(package.data)
    profile = user.get_profile()
    account = profile.billing_account
    try:
        with xact():
            with xact(using = settings.BILLING_DB):
                external_number = ExternalNumber.objects.get(number = param['numbers'][0])
                deactivate_zakaz(account, RESERVATION_SERVICE_TYPE, external_number)
                external_number.is_reserved = False
                external_number.save()
                zakaz = create_zakaz(account, ABON_SERVICE_TYPE, external_number)
                findocs = [FinDocSigned.objects.filter(findoc__slug = '800_contract', signed_by = user).order_by('-id')[0]]
                send_to = send_docs(user, findocs, 'INSTRUCTION_RESERVATION_CONNECT_800')
                package.activate = True
                package.save()
                request.notifications.add(u'На %s отправлено письмо с дальнейшими инструкциями для подключения номера!' % send_to, "success")
    except Exception, e:
        package.deactivate = True
        package.save()
        log.add("number800.py connect Exception: %s" % e)
        request.notifications.add(_(u"Произошла непредвиденная ошибка, обратитесь в техподдержку!"), "warning")
    return HttpResponseRedirect(reverse("8800_list"))

@login_required
@render_to("number800_manage.html")
@decorator_for_sign_applications()
def reserved_free(request):
    user = request.user
    package = Package_on_connection_of_service.objects.get(user = user, activate = False, deactivate = False)
    param = eval(package.data)
    profile = user.get_profile()
    account = profile.billing_account
    try:
        with xact():
            with xact(using = settings.BILLING_DB):
                external_number = ExternalNumber.objects.get(number = param['numbers'][0])
                next_month = (datetime.now() + relativedelta(months = 1)).replace(day = 1, hour = 0, minute = 0, second = 0, microsecond = 0)
                deactivate_zakaz(account, RESERVATION_SERVICE_TYPE, external_number, date_deactivation = next_month)
                findocs = [FinDocSigned.objects.filter(findoc__slug = '800_forma', signed_by = user).order_by('-id')[0]]
                send_to = send_docs(user, findocs, 'INSTRUCTION_DISCONNECT_800')
                package.activate = True
                package.save()
                request.notifications.add(u'На %s отправлено письмо с дальнейшими инструкциями для отключения номера!' % send_to, "success")
    except Exception, e:
        package.deactivate = True
        package.save()
        log.add("number800.py connect Exception: %s" % e)
        request.notifications.add(_(u"Произошла непредвиденная ошибка, обратитесь в техподдержку!"), "warning")
    return HttpResponseRedirect(reverse("8800_list"))

@login_required
@render_to('number800_manage.html')
@decorator_for_sign_applications()
def delete(request):
    user = request.user
    package = Package_on_connection_of_service.objects.get(user = user, activate = False, deactivate = False)
    param = eval(package.data)
    profile = user.get_profile()
    account = profile.billing_account
    try:
        with xact():
            with xact(using = settings.BILLING_DB):
                external_number = ExternalNumber.objects.get(number = param['numbers'][0])
                next_month = (datetime.now() + relativedelta(months = 1)).replace(day = 1, hour = 0, minute = 0, second = 0, microsecond = 0)
                deactivate_zakaz(account, ABON_SERVICE_TYPE, external_number, date_deactivation = next_month)
                package.activate = True
                package.save()
                findocs = [FinDocSigned.objects.filter(findoc__slug = '800_forma', signed_by = user).order_by('-id')[0]]
                send_to = send_docs(user, findocs, 'INSTRUCTION_DISCONNECT_800')
                request.notifications.add(u'На %s отправлено письмо с дальнейшими инструкциями для отключения номера!' % send_to, "success")
    except Exception, e:
        package.deactivate = True
        package.save()
        log.add("number800.py connect Exception: %s" % e)
        request.notifications.add(_(u"Произошла непредвиденная ошибка, обратитесь в техподдержку!"), "warning")
    return HttpResponseRedirect(reverse("8800_list"))

@login_required
@render_to('number800_manage.html')
@decorator_for_sign_applications()
def pause(request):
    user = request.user
    package = Package_on_connection_of_service.objects.get(user = user, activate = False, deactivate = False)
    param = eval(package.data)
    profile = user.get_profile()
    account = profile.billing_account
    try:
        with xact():
            with xact(using = settings.BILLING_DB):
                external_number = ExternalNumber.objects.get(number = param['numbers'][0])
                old_zakaz = deactivate_zakaz(account, ABON_SERVICE_TYPE, external_number)
                zakaz = create_zakaz(account, PAUSE_SERVICE_TYPE, external_number)
                external_number.is_reserved = True
                external_number.save()
                package.activate = True
                package.save()
                findocs = [FinDocSigned.objects.filter(findoc__slug = '800_forma', signed_by = user).order_by('-id')[0]]
                send_to = send_docs(user, findocs, 'INSTRUCTION_PAUSE_800')
                request.notifications.add(u'На %s отправлено письмо с дальнейшими инструкциями для приостановки обслуживания номера!' % send_to, "success")
    except Exception, e:
        package.deactivate = True
        package.save()
        log.add("number800.py connect Exception: %s" % e)
        request.notifications.add(_(u"Произошла непредвиденная ошибка, обратитесь в техподдержку!"), "warning")
    return HttpResponseRedirect(reverse("8800_list"))

@login_required
@render_to('number800_manage.html')
@decorator_for_sign_applications()
def pause_delete(request):
    user = request.user
    package = Package_on_connection_of_service.objects.get(user = user, activate = False, deactivate = False)
    param = eval(package.data)
    profile = user.get_profile()
    account = profile.billing_account
    try:
        with xact():
            with xact(using = settings.BILLING_DB):
                external_number = ExternalNumber.objects.get(number = param['numbers'][0])
                next_month = (now + relativedelta(months = 1)).replace(day = 1, hour = 0, minute = 0, second = 0, microsecond = 0)
                deactivate_zakaz(account, PAUSE_SERVICE_TYPE, external_number, date_deactivation = next_month)
                package.activate = True
                package.save()
                findocs = [FinDocSigned.objects.filter(findoc__slug = '800_forma', signed_by = user).order_by('-id')[0]]
                send_to = send_docs(user, findocs, 'INSTRUCTION_DISCONNECT_800')
                request.notifications.add(u'На %s отправлено письмо с дальнейшими инструкциями для отключения номера!' % send_to, "success")
    except Exception, e:
        package.deactivate = True
        package.save()
        log.add("number800.py connect Exception: %s" % e)
        request.notifications.add(_(u"Произошла непредвиденная ошибка, обратитесь в техподдержку!"), "warning")
    return HttpResponseRedirect(reverse("8800_list"))

@login_required
@render_to('number800_manage.html')
@decorator_for_sign_applications()
def pause_connect(request):
    user = request.user
    package = Package_on_connection_of_service.objects.get(user = user, activate = False, deactivate = False)
    param = eval(package.data)
    profile = user.get_profile()
    account = profile.billing_account
    try:
        with xact():
            with xact(using = settings.BILLING_DB):
                external_number = ExternalNumber.objects.get(number = param['numbers'][0])
                old_zakaz = deactivate_zakaz(account, PAUSE_SERVICE_TYPE, external_number)
                zakaz = Zakazy.objects.get(ext_numbers = external_number, bill_account = account, status_zakaza_id = STATUS_ZAKAZA_DEACTIVATED, service_type_id = ABON_SERVICE_TYPE)
                zakaz.date_deactivation = None
                zakaz.status_zakaza_id = STATUS_ZAKAZA_ACTIVE
                zakaz.save()
                cost = float(cost_dc(zakaz.id))
                zakaz.cost = '%.2f' % cost
                zakaz.save()
                external_number.is_reserved = False
                external_number.save()
                package.activate = True
                package.save()
                findocs = [FinDocSigned.objects.filter(findoc__slug = '800_forma', signed_by = user).order_by('-id')[0]]
                send_to = send_docs(user, findocs, 'INSTRUCTION_PAUSE_CONNECT_800')
                request.notifications.add(u'На %s отправлено письмо с дальнейшими инструкциями для восстановления обслуживания номера!' % send_to, "success")
    except Exception, e:
        package.deactivate = True
        package.save()
        log.add("number800.py connect Exception: %s" % e)
        request.notifications.add(_(u"Произошла непредвиденная ошибка, обратитесь в техподдержку!"), "warning")
    return HttpResponseRedirect(reverse("8800_list"))
