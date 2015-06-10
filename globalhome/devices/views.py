# coding: utf-8
from lib.decorators import render_to, login_required
from django.conf import settings
# from tariffs.models import TelZoneGroup
from django.utils.translation import ugettext as _
from devices.models import Devices
from tariffs.forms import ChangeTelzoneGroupForm
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
import base64
import log
# from findocs import check_for_sign_applications
from django.db import connections, transaction
from account.models import Profile
from devices.models import Devices, ApplicationService, UserService
import datetime
from services.models import AvailableService, AddSPTransaction, BalanceException
from findocs.models import FinDocSignApplication, FinDoc, Check, Act, Invoice, FinDocSigned
from findocs.views import findocs_application_sign
import log, gzip, zipfile, zlib, shutil, os, calendar
from lib.decorators import render_to
from account.forms import UserRegistrationForm
from account.forms import UserLoginForm2, PasswordResetRequestForm
from account.models import *
from billing.models import *
from externalnumbers.consts import *
from django.contrib.auth import authenticate, login as _login, logout as _logout
from lib.helpers import redirect, next
from django.utils.encoding import iri_to_uri, force_unicode
from content.models import Article
from django.utils.translation import ugettext_lazy as _, ugettext
from decimal import Decimal
from page.views import panel_base_auth
from devices.forms import sum_for_check, write_off_filter_form, email_for_document
from data_centr.views import send_mail_check, add_document_in_dict_for_send
from itertools import chain
from findocs.models import Rules_of_drawing_up_documents
from payment.models import Billservice_transaction
from dateutil.relativedelta import relativedelta  # @UnresolvedImport
from django.db.models import Q


@render_to("t2.html")
def t2(request):
    context = {}
    qwe = list(Devices.objects.all())
    for i, qw in enumerate(qwe):
        qw.number = i + 1
    context["qwe"] = qwe
    context['meta_title'] = u'Аренда оборудования для телефонии. Оборудование в офис'
    context['meta_description'] = u'У нас можно взять в аренду оборудование для IP-телефонии.'
    context['meta_keywords'] = u'аренда оборудования, IP-телефония, оборудование для телефонии'
    return panel_base_auth(request, context)


# @check_for_sign_applications(["localphone_blank1", "rental_device", "cancel", "localphone_services_contract", "localphone_orderform", "localphone_detach"])
@login_required
@render_to("Service.html")
def services_list(request):
    user = request.user
    profile = user.get_profile()
    if not profile.is_juridical:
        raise Http404
    context = {}
    # выводим услуги
    cur = connections[settings.BILLING_DB].cursor()
    # cur2 = connections[settings.GLOBALHOME_DB2].cursor()

    cur.execute("SELECT * FROM billservice_addonservice;")
    servic = cur.fetchall()
    service1 = []
    for i, se in enumerate(servic):
        service1.append(se[0:6] + (round(float(se[7]) / 1.18, 2),) + se[8:])
    context["service"] = service1
    '''
    device = list(Devices.objects.all())
    context["service"] = device
    '''


    cur.execute("SELECT billservice_accountaddonservice.id, activated, name, billservice_addonservice.cost, service_id, numbers, external_numbers.id FROM billservice_accountaddonservice JOIN billservice_addonservice on(billservice_accountaddonservice.service_id = billservice_addonservice.id) LEFT JOIN external_numbers on(billservice_accountaddonservice.numbers = external_numbers.number) WHERE billservice_accountaddonservice.account_id=%s and action_status = True;", (profile.billing_account_id,))
    userservice = cur.fetchall()
    transaction.commit_unless_managed(settings.BILLING_DB)
    userservice1 = []
    for i, userse in enumerate(userservice):
        userservice1.append(userse[0:3] + (round(float(userse[3]) / 1.18, 2),) + (round((float(userse[3]) - float(userse[3]) / 1.18), 2),) + (round(float(userse[3]), 2),) + userse[4:])


    context["userservice"] = userservice1
    context["current_view_name"] = "services"
    return context

@login_required
# @check_for_sign_applications(["localphone_blank1", "rental_device", "cancel", "localphone_services_contract", "localphone_orderform", "localphone_detach"])
@render_to("service_add.html")
def service_add(request, tel_number_id):

    user = request.user
    context = {}
    profile = user.get_profile()
    if not profile.is_juridical:
        raise Http404

    cur = connections[settings.BILLING_DB].cursor()
    # cur2 = connections[settings.GLOBALHOME_DB2].cursor()

    cur.execute("SELECT ballance FROM billservice_account WHERE id=%s;", (profile.billing_account_id,))
    profile_ballance = cur.fetchone()[0]

    cur.execute("SELECT * FROM billservice_addonservice WHERE id=%s;", (tel_number_id,))
    for_service = cur.fetchone()
    transaction.commit_unless_managed(settings.BILLING_DB)
    now = datetime.datetime.now()

    # цепляем за услугой нужный договор:
    if tel_number_id == '9' or tel_number_id == '20' or tel_number_id == '10' or tel_number_id == '11' or tel_number_id == '12':
        findoc_name = "Аренда оборудования"
    else:
        findoc_name = ""


    # проверка на баланс
    if for_service[7] >= profile_ballance:
        request.notifications.add(_(u"You have insufficient funds to perform this operation!"), "error")
        return HttpResponseRedirect(reverse("services"))


    # если деньги позволяют, то:
    else:



        doc = FinDocSignApplication(
            assigned_at=now,
            findoc=FinDoc.objects.get(name=findoc_name),
            assigned_to=request.user,
            user_can_cancel=True,
            for_services=tel_number_id,
            service_for_billing="document_for_the_service_connection")
        doc.save()

        aplicationservice = ApplicationService(name=for_service[1],
        created_at=now,
        modified_at=now,
        created_by=request.user,
        service=for_service[0],
        user=profile.billing_account_id,
        fin_doc_id=doc.id)

        aplicationservice.save()




    return HttpResponseRedirect(reverse("services"))





@login_required
# @check_for_sign_applications(["localphone_blank1", "rental_device", "AV7010", "Cancel" ,"localphone_services_contract", "localphone_orderform", "localphone_detach"])
# @render_to("service_del.html")
def service_del(request, tel_number_id):
    user = request.user
    now = datetime.datetime.now()
    profile = user.get_profile()
    cur = connections[settings.BILLING_DB].cursor()
    cur.execute("SELECT service_id FROM billservice_accountaddonservice WHERE id=%s;", (tel_number_id,))
    accountservice = cur.fetchone()[0]
    cur.execute("SELECT * FROM billservice_addonservice WHERE id=%s;", (accountservice,))
    for_service = cur.fetchone()
    cur.execute("SELECT account_id, action_status, service_id FROM billservice_accountaddonservice WHERE id=%s;", (tel_number_id,))
#        if cur.fetchall()[0]:
    prowerka = cur.fetchall()[0]
    transaction.commit_unless_managed(settings.BILLING_DB)
#        else:
#            request.notifications.add(_(u"Do not attempt to remove the service, Cator you do not!"), "error")
#            return HttpResponseRedirect(reverse("services"))
    if prowerka[2] == 9 or prowerka[2] == 10 or prowerka[2] == 11:
        request.notifications.add(_(u"Невозможно открепить услугу, обратитесь к администрации!"), "error")
        return HttpResponseRedirect(reverse("services"))
    if prowerka[0] == profile.billing_account_id and prowerka[1] == True and prowerka[2] != 3:

        if FinDoc.objects.filter(name=for_service[1], slug="cancel"):

            doc = FinDocSignApplication(
                assigned_at=now,
                findoc=FinDoc.objects.get(name=for_service[1], slug="cancel"),
                assigned_to=request.user,
                user_can_cancel=True,
                for_services=tel_number_id,
                service_for_billing="document_to_deactivate")
            doc.save()

            aplicationservice = ApplicationService(name=for_service[1],
            created_at=now,
            modified_at=now,
            created_by=request.user,
            service=for_service[0],
            text="Заявка на онключение услуги",
            user=profile.billing_account_id)

            aplicationservice.save()

            return HttpResponseRedirect(reverse("services"))
        else:



            ''' ДОДЕЛАТЬ!!!! (ДОКУМЕНТ НА ОТКЛЮЧЕНЕ УСЛУГИ!!!)
            if service.cancel_document:
                doc = FinDocSignApplication(for_cancel = True,
                        assigned_at = now,
                        findoc = FinDoc.objects.get(id = service.cancel_document.id),
                        assigned_to = request.user,
                        user_can_cancel = True,
                        for_services = del_user_service.id)
                doc.save()
                if del_user_service.created_by.id == request.user.id:
                    return HttpResponseRedirect(reverse("services"))
                else:
                    request.notifications.add(_(u"Do not attempt to remove the service, Cator you do not!"), "error")
                return HttpResponseRedirect(reverse("services"))
            '''
            try:

                    cur.execute("UPDATE billservice_accountaddonservice SET action_status=%s, deactivated=%s WHERE id=%s;", (False, now, tel_number_id,))
                    transaction.commit_unless_managed(settings.BILLING_DB)
                    request.notifications.add(_(u"Service successfully removed!"), "success")

            except UserService.DoesNotExist:
                raise Http404
            return HttpResponseRedirect(reverse("services"))
    else:
        raise Http404
    return HttpResponseRedirect(reverse("services"))


@login_required
@render_to("check_user_view.html")
def check_user_view(request, type_document, number_id):
    context = {}
    dict_type = {'check':'Check', 'act':'Act', 'invoice':'Invoice'}
    try:
        try:
            if type_document in ('check', 'act', 'invoice'):
                model_class = dict_type[type_document]
                document = eval('%s.objects.get(id = number_id)' % (model_class))
                if document.created_by != request.user:
                    request.notifications.add(u'Вы попытались просмотреть не существующий у Вас документ', 'error')
            else:
                raise Http404
        except:
            raise Http404

        context["document"] = document
    except:
        raise Http404
    return context


@login_required
@render_to("invoices_and_payment.html")
def invoices_and_payment(request):
    user = request.user
    profile = user.get_profile()
    if profile.is_card:
        raise Http404
    context = {}
    context["current_view_name"] = "account_show_tariffs"
    checks = Check.objects.filter(created_by=user, valid=True).order_by('-year', '-month', '-number')
    acts = Act.objects.filter(created_by=user).order_by('-year', '-month', '-number')
    invoices = Invoice.objects.filter(created_by=user).order_by('-year', '-month', '-number')
    checks_year = Check.objects.filter(created_by=user, valid=True).order_by('year').distinct().values('year')
    act_year = Act.objects.filter(created_by=user).order_by('year').distinct().values('year')
    invoice_year = Invoice.objects.filter(created_by=user).order_by('year').distinct().values('year')
    spis_check_year = [i["year"] for i in checks_year]
    spis_check_year = sorted(spis_check_year, reverse=True)
    spis_act_year = [i["year"] for i in act_year]
    spis_act_year = sorted(spis_act_year, reverse=True)
    spis_invoice_year = [i["year"] for i in invoice_year]
    spis_invoice_year = sorted(spis_invoice_year, reverse=True)
    context["checks"] = checks
    context["acts"] = acts
    context["invoices"] = invoices
    context["check_year"] = spis_check_year
    context["act_year"] = spis_act_year
    context["invoice_year"] = spis_invoice_year
    if checks or acts or invoices:
        context['document'] = True
    else:
        context['document'] = False
    print request.POST
    if request.POST.get('add_mail'):
        form = email_for_document(request.POST)
        if form.is_valid():
            profile.mail_for_document = form.cleaned_data["email_for_document"]
            profile.save()
            context['mail'] = profile.mail_for_document
            request.notifications.add(u'E-mail адрес для получения документов успешно изменен', 'success')
        else:
            context['form'] = form
    else:
        if request.POST.get('edit_mail'):
            form = email_for_document()
            context['form'] = form
        else:
            if profile.mail_for_document:
                context['mail'] = profile.mail_for_document
            else:
                context['mail'] = user.email
    if request.GET:
        if request.GET.get('type_document') and request.GET.get('id_document'):
            if not request.GET['type_document'] in ('Check', 'Act', 'Invoice') and not request.GET['id_document']:
                raise Http404
            else:
                try:
                    document = eval('%s.objects.get(id = %s)' % (request.GET['type_document'], request.GET['id_document']))
                    if document.created_by != request.user:
                        request.notifications.add(u'Вы попытались скачать не существующий у Вас документ', 'error')
                    else:
                        fname = "document_" + str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")) + "_%s" % user.id
                        link = "/media/billed_calls_files/%s.zip" % fname
                        check_file = open(fname + ".doc", "w")
                        check_file.write(document.text.encode('utf-8'))
                        check_file.close()
                        zip = zipfile.ZipFile(fname + ".zip", 'w', 8)
                        zip.write(check_file.name)
                        zip.close()
                        shutil.move(fname + ".zip", 'media/billed_calls_files/%s.zip' % fname)
                        os.remove("%s.doc" % fname)
                        return HttpResponseRedirect(link)
                except:
                    request.notifications.add(u'Произошла непредвиденная ошибка, пожалуйста, обратитесь в администрацию!', 'error')

        else:
            request.notifications.add(u'Вы попытались скачать не существующий у Вас документ', 'error')

#    cur.execute("SELECT bill, created, summ FROM billservice_transaction WHERE account_id = '%s' ORDER BY created DESC;", (profile.billing_account_id,))
#    pay = cur.fetchall()
#    end_pay = []
#    new_pay = {'list_pay': [], 'summ_pay': 0}
#    new_pay_end = []
#    k = 0
#    for paym in pay:
#        sobr = []
#        sobr.append(paym[0])
#        sobr.append(paym[1])
#        sobr.append(abs(float(paym[2])))
#        end_pay.append(sobr)
#    for list_pay in end_pay:
#        new_pay['list_pay'].append(list_pay)
#        new_pay['summ_pay'] += float(list_pay[2])
#        try:
#            if not list_pay[1].date().month == end_pay[k + 1][1].date().month:
#                new_pay_end.append(new_pay)
#                new_pay = {'list_pay': [], 'summ_pay': 0}
#        except:
#            new_pay_end.append(new_pay)
#        k = k + 1
#    context["pay"] = new_pay_end
#    context["current_view_name"] = "account_show_tariffs"
#    cur.execute("""SELECT billservice_addonservicetransaction.created, billservice_addonservicetransaction.summ, billservice_addonservice.name, billservice_accountaddonservice.numbers
#        FROM billservice_addonservicetransaction
#        JOIN billservice_addonservice on(billservice_addonservicetransaction.service_id = billservice_addonservice.id)
#        JOIN billservice_accountaddonservice on(billservice_addonservicetransaction.accountaddonservice_id = billservice_accountaddonservice.id)
#        WHERE billservice_addonservicetransaction.account_id = '%s' ORDER BY billservice_addonservicetransaction.created DESC;""", (profile.billing_account_id,))
#    debiting = cur.fetchall()
#    i = 0
#    all_summ = 0
#    new_list = {'list': [], 'summ': 0}
#    new_list_end = []
#    for list in debiting:
#        new_list['list'].append(list)
#        new_list['summ'] += float(list[1])
#        try:
#            if not list[0].date().month == debiting[i + 1][0].date().month:
#                new_list_end.append(new_list)
#                new_list = {'list': [], 'summ': 0}
#
#
#        except:
#            new_list_end.append(new_list)
#        i = i + 1
#    context["debiting"] = new_list_end
#    except:
#        raise Http404
    return context


@login_required
@render_to("write_offs_and_account_replenishment.html")
def write_offs_and_account_replenishment(request):
    context = {}
    now = datetime.datetime.now()
    print now
    profile = request.user.get_profile()
    bill_acc = BillserviceAccount.objects.get(id=profile.billing_account_id)
    last_month = now - relativedelta(months=1)
    first_day_last_month = datetime.datetime(last_month.year, last_month.month, 1, 0, 0, 0)
    dict_month = {1:'январь', 2:'февраль', 3:'март', 4:'апрель', \
                  5:'май', 6:'июнь', 7:'июль', 8:'август', 9:'сентябрь', \
                  10:'октябрь', 11:'ноябрь', 12:'декабрь'}
    if 'filter' in request.GET:
        form = write_off_filter_form(request.GET)
    else:
        form = write_off_filter_form()
    if form.is_valid():
        date_from = form.cleaned_data["date_from"]
        date_to = form.cleaned_data["date_to"]
    else:
        date_from = first_day_last_month
        date_to = now
    all_transaction_queryset = Billservice_transaction.objects.filter(Q(account=bill_acc) & \
                                                                      (Q(created__gte=date_from) & Q(created__lte=date_to)))\
                                                                      .exclude(type_id__in=['MANUAL_TRANSACTION', 'END_PS_MONEY_RESET', 'HOTSPOT_CARD'])\
                                                                      .order_by('-created', 'summ')  # created__gte = first_day_last_month)
    all_transaction, transaction_write_off, transaction_replenishment = [], [], []
    spis_all_transaction_years, spis_transaction_replenishment_years, spis_transaction_write_off_years = [], [], []

    dict_year_and_month_all = {}
    dict_year_and_month_repl = {}
    dict_year_and_month_write_off = {}

    if all_transaction_queryset:
        context['transaction'] = True
        for transaction_obj in all_transaction_queryset:
            if transaction_obj.summ > 0:
                type = u'Пополнение'
                transaction_replenishment.append({'year':(transaction_obj.created).year, 'month': dict_month[(transaction_obj.created).month], 'date':transaction_obj.created, 'about':transaction_obj.bill, \
                                    'summ':'%.2f' % abs(transaction_obj.summ)})
            elif transaction_obj.summ < 0:
                type = u'Списание'
                transaction_write_off.append({'year':(transaction_obj.created).year, 'month': dict_month[(transaction_obj.created).month], 'date':transaction_obj.created, 'about':transaction_obj.bill, \
                                    'summ':'%.2f' % abs(transaction_obj.summ)})
            else:
                continue
            # add date
            all_transaction.append({'year':(transaction_obj.created).year, 'month': dict_month[(transaction_obj.created).month], 'date':transaction_obj.created, 'about':transaction_obj.bill, \
                                    'summ':'%.2f' % abs(transaction_obj.summ), 'type': type})

        # в списке всех годов для всех транзакций пользователя могут появиться лишние года которых нет в  all_transaction_queryset  !!!!???? потому добавим фильтр exc MANUAL_TRANSACTION', 'END_PS_MONEY_RESET', 'HOTSPOT_CARD
        all_transaction_date = Billservice_transaction.objects.filter(Q(account=bill_acc) & \
                                                                      (Q(created__gte=date_from) & Q(created__lte=date_to)))\
                                                                      .exclude(type_id__in=['MANUAL_TRANSACTION', 'END_PS_MONEY_RESET', 'HOTSPOT_CARD'])\
                                                                      .order_by('created').distinct().values('created')
        spis_all_transaction_years = [i['created'].year for i in all_transaction_date]
        spis_all_transaction_years = sorted(set(spis_all_transaction_years), reverse=True)
        # save months for all transactions
        # create dict year and month
        for year_value in spis_all_transaction_years:
            spis_all_transaction_months_in_the_year = []
            spis_all_transaction_months_in_the_year_lit = []
            # key for dictionary (contains year)
            all_transaction_date_year_value = Billservice_transaction.objects.filter(Q(account=bill_acc) & Q(created__year=year_value) & \
                                                                      (Q(created__gte=date_from) & Q(created__lte=date_to)))\
                                                                      .exclude(type_id__in=['MANUAL_TRANSACTION', 'END_PS_MONEY_RESET', 'HOTSPOT_CARD'])\
                                                                      .order_by('created').distinct().values('created')  # created__gte = first_day_last_month)
            spis_all_transaction_months_in_the_year = [i['created'].month for i in  all_transaction_date_year_value]
            spis_all_transaction_months_in_the_year = sorted(set(spis_all_transaction_months_in_the_year), reverse=True)
            # create new list for literal month
            for m in spis_all_transaction_months_in_the_year:
                spis_all_transaction_months_in_the_year_lit.append(dict_month[m])
            dict_year_and_month_all[year_value] = spis_all_transaction_months_in_the_year_lit
        # end of creating year and month  all transactions


        if transaction_replenishment:
            transaction_replenishment_date = Billservice_transaction.objects.filter(Q(account=bill_acc) & \
                                                              (Q(created__gte=date_from) & Q(created__lte=date_to)) & \
                                                              Q(summ__gt=0)).exclude(type_id__in=['MANUAL_TRANSACTION', 'END_PS_MONEY_RESET', 'HOTSPOT_CARD']).order_by('created').distinct().values('created')
            transaction_replenishment_date = [i['created'].year for i in transaction_replenishment_date]
            spis_transaction_replenishment_years = sorted(set(transaction_replenishment_date), reverse=True)
        # save months for repl transactions
        # create dict year and month for repl
        for year_value in spis_transaction_replenishment_years:
            spis_repl_transaction_months_in_the_year = []
            spis_repl_transaction_months_in_the_year_lit = []
            # key for dictionary (contains year)
            repl_transaction_date_year_value = Billservice_transaction.objects.filter(Q(account=bill_acc) & Q(created__year=year_value) & \
                                                              (Q(created__gte=date_from) & Q(created__lte=date_to)) & \
                                                              Q(summ__gt=0)).exclude(type_id__in=['MANUAL_TRANSACTION', 'END_PS_MONEY_RESET', 'HOTSPOT_CARD']).order_by('created').distinct().values('created')
            spis_repl_transaction_months_in_the_year = [i['created'].month for i in  repl_transaction_date_year_value]
            spis_repl_transaction_months_in_the_year = sorted(set(spis_repl_transaction_months_in_the_year), reverse=True)
            # create new list for literal month
            for m in spis_repl_transaction_months_in_the_year:
                spis_repl_transaction_months_in_the_year_lit.append(dict_month[m])
            dict_year_and_month_repl[year_value] = spis_repl_transaction_months_in_the_year_lit
        # end of creating year and month  for repl


        if transaction_write_off:
            transaction_write_off_date = Billservice_transaction.objects.filter(Q(account=bill_acc) & \
                                                  (Q(created__gte=date_from) & Q(created__lte=date_to)) & \
                                                  Q(summ__lt=0)).exclude(type_id__in=['MANUAL_TRANSACTION', 'END_PS_MONEY_RESET', 'HOTSPOT_CARD']).order_by('created').distinct().values('created')
            transaction_write_off_date = [i['created'].year for i in transaction_write_off_date]
            spis_transaction_write_off_years = sorted(set(transaction_write_off_date), reverse=True)
        # save months for write_off transactions
        # create dict year and month for write_off
        for year_value in spis_transaction_write_off_years:
            spis_write_off_transaction_months_in_the_year = []
            spis_write_off_transaction_months_in_the_year_lit = []
            # key for dictionary (contains year)
            write_off_transaction_date_year_value = Billservice_transaction.objects.filter(Q(account=bill_acc) & Q(created__year=year_value) & \
                                                              (Q(created__gte=date_from) & Q(created__lte=date_to)) & \
                                                              Q(summ__lt=0)).exclude(type_id__in=['MANUAL_TRANSACTION', 'END_PS_MONEY_RESET', 'HOTSPOT_CARD']).order_by('created').distinct().values('created')
            spis_write_off_transaction_months_in_the_year = [i['created'].month for i in  write_off_transaction_date_year_value]
            spis_write_off_transaction_months_in_the_year = sorted(set(spis_write_off_transaction_months_in_the_year), reverse=True)
            # create new list for literal month
            for m in spis_write_off_transaction_months_in_the_year:
                spis_write_off_transaction_months_in_the_year_lit.append(dict_month[m])
            dict_year_and_month_write_off[year_value] = spis_write_off_transaction_months_in_the_year_lit
        # end of creating year and month for write_off

    else:
        context['transaction'] = False
    context['form'] = form
    context['all_transaction'] = all_transaction
    context['transaction_write_off'] = transaction_write_off
    context['transaction_replenishment'] = transaction_replenishment
    context['all_transaction_years'] = spis_all_transaction_years
    context['transaction_replenishment_years'] = spis_transaction_replenishment_years
    context['transaction_write_off_years'] = spis_transaction_write_off_years
    # dict for year and month in all tranactions
    context['dict_year_and_month_all'] = dict_year_and_month_all
    # dict for year and mont in repl transactions
    context['dict_year_and_month_repl'] = dict_year_and_month_repl
    # dict for year and month in write off transactions
    context['dict_year_and_month_write_off'] = dict_year_and_month_write_off
    context['devices_page'] = True
    return context


@login_required
@render_to("advance_invoice.html")
def advance_invoice(request):
    user = request.user
    profile = user.get_profile()
    if not profile.is_juridical or not profile.create_invoice:
        raise Http404
    if profile.is_card:
        raise Http404
    context = {}
    context['title'] = u'Выставление авансового счета'
    context["current_view_name"] = "account_show_tariffs"
    spis_findoc = ['telematic_data_centr', 'telematic_services_contract']
    findocs_queryset = FinDocSigned.objects.filter(signed_by=user, findoc__slug__in=spis_findoc, cancellation_date=None)
    if findocs_queryset:
        choices = []
        for f in findocs_queryset:
            choices.append((f.id, f.findoc.name))
        form = sum_for_check(None, choices)
        if request.POST.get('submit'):
            form = sum_for_check(request.POST.copy(), choices)
            if form.is_valid():
                advance_sum = form.cleaned_data["sum"]
                findoc_sign_id = form.cleaned_data["findoc"]
                findoc_sign_obj = FinDocSigned.objects.get(id=findoc_sign_id)
                findoc_id = findoc_sign_obj.findoc.id
                if profile.is_juridical:
                    rule_obj = Rules_of_drawing_up_documents.objects.filter(id__in=[6, 7, 8], findoc_juridical__id=findoc_id)[0]
                else:
                    rule_obj = Rules_of_drawing_up_documents.objects.filter(id__in=[6, 7, 8], findoc_juridical__id=findoc_id)[0]
                spis_rules = Check.group_rules(profile, [rule_obj.id], 'type_check')
                content_check_id = Check.create_check(request.user, spis_rules, False, 0 , advance_sum)
                dict_documents_for_send = add_document_in_dict_for_send({}, request.user.id, 'Check', content_check_id)
                send_mail_check(dict_documents_for_send)
                request.notifications.add(u"Авансовый счет успешно выставлен!", "success")
            else:
                request.notifications.add(u"Неправильно заполнено поле сумма!", "error")
        context['form'] = form
    else:
        request.notifications.add(u"У вас нет подписанных договоров", "info")
        context['no_findoc'] = True
    return context




