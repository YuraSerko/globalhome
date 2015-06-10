# -*- coding=utf-8 -*-
# Create your views here.
from django.conf import settings  # @UnusedImport
from django.http import Http404
import random, os, glob, shutil
from forms import RecordTalkForm
from models import Record_talk_tariff, Record_talk_activated_tariff, Record_talk
from lib.decorators import render_to, login_required, limit_con_service
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from data_centr.models import Zakazy
from billing.models import BillserviceAccount
from data_centr.views import add_record_in_data_centr_payment, add_record_in_priority_of_services, cost_dc, send_mail_check, add_document_in_dict_for_send, write_off_of_money
import datetime
from django.db.models import Q
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from findocs.models import Rules_of_drawing_up_documents, Check, FinDocSignedZakazy
from findocs import get_signed
from lib.http import get_query_string
from django.contrib.redirects.models import Redirect
from django.db import connections, transaction
from fs.models import Queue


@login_required
@render_to('record.html')
def list_record_talk_tariff(request):
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    record_talk_tariff = []
    context["title"] = _(u"Запись разговоров: Выбор тарифа")
    context["current_view_name"] = "list_record_talk_tariff"
    profile = request.user.get_profile()
    context["change_tariff"] = True
    context["record_talk_tariff_active"] = []
    if profile:
        if profile.has_billing_account:
            if profile.billing_account.phones:
                context["have_numbers"] = True
            else:
                context["have_numbers"] = False
        try:
            record_talk_tariff_active = Record_talk_activated_tariff.objects.filter(Q(billing_account_id=profile.billing_account_id) & \
                                                                                    # Q(date_activation__lt=datetime.datetime.now()) & \
                                                                                    (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now()))\
                                                                                    )
        except Record_talk_activated_tariff.DoesNotExist, e:
            record_talk_tariff_active = None
            context["record_talk_tariff_active_true"] = False

        if record_talk_tariff_active:
            record_talk = Record_talk.objects.filter(billing_account_id=profile.billing_account_id)
            context["record_talk"] = record_talk
            context["record_talk_tariff_active_true"] = True
            context["title"] = _(u"Ваш тариф")
            context["title1"] = _(u"Ваши номера с записью разговора")
            context["record_talk_tariff_user"] = record_talk_tariff_active
            if len(record_talk_tariff_active) > 1:
                context["change_tariff"] = False

            for x in record_talk_tariff_active:
                #===============================================================
                # print "x"
                if x.date_deactivation:
                    context["not_disabled"] = True
                # print x.tariff_id
                #===============================================================
                context["record_talk_tariff_active"].append(Record_talk_tariff.objects.get(id=x.tariff_id))

            if request.POST:
                # пришли данные, надо включить/выключить некоторые ivr
                if request.POST.get("submit"):
                    for vm in record_talk:
                        if request.POST.get(str(vm.id)) == "on":
                            vm.enabled = True
                        else:
                            vm.enabled = False
                        vm.save()

    record_talk_tariff = Record_talk_tariff.objects.filter()
    context["record_talk_tariff"] = record_talk_tariff
    try:
        if request.GET['notif']:
            context["notif"] = request.GET['notif']
    except:
        pass
    return context


@login_required
@render_to('record_change.html')
def list_record_talk_tariff_change(request):
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context["record_talk_tariff"] = []
    context["title"] = _(u"Запись разговоров: Смена тарифа")
    context["current_view_name"] = "list_record_talk_tariff"
    profile = request.user.get_profile()
    if profile:
        if profile.has_billing_account:
            if profile.billing_account.phones:
                context["have_numbers"] = True
            else:
                context["have_numbers"] = False
        context["record_talk_tariff_active_true"] = False
    try:
        record_talk_tariff_active = Record_talk_activated_tariff.objects.filter(Q(billing_account_id=profile.billing_account_id) & \
                                                                                # Q(date_activation__lt=datetime.datetime.now()) & \
                                                                                (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now()))\
                                                                                )
    except Record_talk_activated_tariff.DoesNotExist, e:
        raise Http404

    active = Record_talk_tariff.objects.all()
    for x in record_talk_tariff_active:
        active = active.exclude(id=x.tariff_id)
    context["record_talk_tariff"] = active

    return context


@login_required
@render_to('record_deactivate.html')
def deactivate_tariff(request):
    def deactivate_record_queue(billing_account_id):  # выключает запись на очередях
        try:
            queues = Queue.objects.db_manager(settings.BILLING_DB).filter(Q(billing_account_id=billing_account_id) & Q(record_enabled=True)) or []
            for queue in queues:
                queue.record_enabled = False
                queue.save(using=settings.BILLING_DB)
        except Exception, e:
            print 'deactivate_tariff.deactivate_record_queue Exception:', e

    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    record_talk_tariff = []
    context["title"] = _(u"Запись разговоров: Отключение услуги")
    context["current_view_name"] = "list_record_talk_tariff"
    profile = request.user.get_profile()
    if profile:
        if request.POST:
            if request.POST.get("submit"):
                record_talk_tariff_active = None
                try:
                    record_talk_tariff_active = Record_talk_activated_tariff.objects.filter(Q(billing_account_id=profile.billing_account_id) & \
                                                                                            (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now()))\
                                                                                            )
                except Record_talk_activated_tariff.DoesNotExist, e:
                    raise Http404
                if record_talk_tariff_active:
                    for x in record_talk_tariff_active:
                        if x.tariff_id == 2:
                            now = datetime.datetime.now()
                            date_next_start_month_temp = now + relativedelta(months=1)
                            date_next_start_month = datetime.datetime(date_next_start_month_temp.year, date_next_start_month_temp.month, 1, 0, 0, 0)
                            x.date_deactivation = date_next_start_month
                            x.save()
                            try:
                                zakaz_obj = Zakazy.objects.get(bill_account__id=profile.billing_account_id, service_type=9, date_deactivation=None)
                                zakaz_obj.date_deactivation = date_next_start_month
                                zakaz_obj.save()
                            except Zakazy.DoesNotExist:
                                pass


                        else:
                            x.date_deactivation = datetime.datetime.now()
                            x.save()
                    deactivate_record_queue(profile.billing_account_id)  # выключение записи в очередях
                context["record_talk_tariff_active_true"] = False
            return HttpResponseRedirect("/account/record_talk/list_record_tariff/")
    return context


@login_required
@limit_con_service([9], 'telephony')
@render_to('record.html')
def activation_tariff(request, tariff_id):
    if request.user.get_profile().is_card:
        raise Http404
    profile = request.user.get_profile()
    user_obj = User.objects.get(username=request.user.username)
    context = {}
    context["title"] = _(u"Запись разговоров: Активация тарифа")
    context["current_view_name"] = "list_record_talk_tariff"
    # ukey = ""

    if profile:
        if profile.has_billing_account:
            if profile.billing_account.phones:
                context["have_numbers"] = True
            else:
                context["have_numbers"] = False
        try:
            record_talk_tariff_active = Record_talk_activated_tariff.objects.get(Q(billing_account_id=profile.billing_account_id) & \
                                                                                Q(date_activation__lt=datetime.datetime.now()) & \
                                                                                (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now()))\
                                                                                )
            if record_talk_tariff_active:
                # print "akakakakaak"
                request.notifications.add(_(u'У вас уже подключен тариф'), 'success')
                return HttpResponseRedirect("/account/record_talk/list_record_tariff/")
        except Record_talk_activated_tariff.DoesNotExist, e:
            pass

        record_talk_tariff = Record_talk_tariff(id=tariff_id)
        record_talk_tariff_active = Record_talk_activated_tariff()
        record_talk_tariff_active.billing_account_id = profile.billing_account_id
        record_talk_tariff_active.tariff_id = record_talk_tariff.id
        record_talk_tariff_active.date_create = datetime.datetime.now()
        record_talk_tariff_active.date_activation = datetime.datetime.now()
#        for i in xrange(12):
#            ukey = ukey + random.choice('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1237894560')
        if not os.path.exists(settings.REC_URL + '/%s' % (profile.billing_account_id)):
            os.makedirs(settings.REC_URL + '/%s' % (profile.billing_account_id))
#        record_talk_tariff_active.user_key = ukey
        record_talk_tariff_active.save()
        if tariff_id == "2":
            print "no limit"
            bill_acc = BillserviceAccount.objects.get(id=profile.billing_account_id)
            zakaz = Zakazy(
                             section_type=1,
                             service_type_id=9,
                             tariff_id=19,
                             bill_account=bill_acc,
                             status_zakaza_id=2,
                             date_create=datetime.datetime.now(),
                             date_activation=datetime.datetime.now(),
                             connection_cost_id=1,
                             )
            zakaz.save()
            cost = float(cost_dc(zakaz.id))
            zakaz.cost = '%.2f' % cost
            zakaz.save()
            add_record_in_data_centr_payment(zakaz)
            add_record_in_priority_of_services(zakaz)
            findocsign_obj = get_signed(profile.user, "telematic_services_contract")
            fin_doc_zakaz = FinDocSignedZakazy(
                                               fin_doc=findocsign_obj,
                                               zakaz_id=zakaz.id,
                                               )
            fin_doc_zakaz.save()
            spis_rules = Check.group_rules(profile, [9], 'type_check', zakaz.id)
            content_check_id = Check.create_check(request.user, spis_rules, False, [zakaz.id])
            dict_documents_for_send = add_document_in_dict_for_send({}, request.user.id, 'Check', content_check_id)
            send_mail_check(dict_documents_for_send)
            if bill_acc.auto_paid:
                write_off_of_money(bill_acc, [zakaz.id])

        # context["record_talk_tariff_active_true"] = True
        # request.notifications.add(_(u'Тариф успешно подключен'), 'success')
        return HttpResponseRedirect("/account/record_talk/list_record_tariff/?notif=%s" % 'Тариф успешно подключен')
    return context


@login_required
@render_to('record.html')
def change_activation_tariff(request, tariff_id):
    if request.user.get_profile().is_card:
        raise Http404
    profile = request.user.get_profile()
    user_obj = User.objects.get(username=request.user.username)
    context = {}
    context["title"] = _(u"Запись разговоров: Смена тарифа")
    context["current_view_name"] = "list_record_talk_tariff"

    if profile:
        if profile.has_billing_account:
            if profile.billing_account.phones:
                context["have_numbers"] = True
            else:
                context["have_numbers"] = False

        try:
            record_talk_tariff_active = Record_talk_activated_tariff.objects.get(Q(billing_account_id=profile.billing_account_id) & \
                                                                                 Q(tariff=tariff_id) & \
                                                                                 (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now()))\
                                                                                 )

            if record_talk_tariff_active.date_deactivation:
                if record_talk_tariff_active.date_deactivation > datetime.datetime.now():
                    # request.notifications.add(_(u'У вас уже подключен такой тариф'), 'success')
                    return HttpResponseRedirect('/account/record_talk/list_record_tariff/?notif=%s' % 'У вас уже подключен такой тариф')
            if not record_talk_tariff_active.date_deactivation:
                if record_talk_tariff_active.date_activation > datetime.datetime.now():
                    # request.notifications.add(_(u'Вы уже меняли тариф'), 'success')
                    return HttpResponseRedirect('/account/record_talk/list_record_tariff/?notif=%s' % 'Вы уже меняли тариф')

                if record_talk_tariff_active.date_activation < datetime.datetime.now():
                    # request.notifications.add(_(u'У вас уже подключен такой тариф'), 'success')
                    return HttpResponseRedirect('/account/record_talk/list_record_tariff/?notif=%s' % 'У вас уже подключен такой тариф')

        except Record_talk_activated_tariff.DoesNotExist, e:
            pass

        record_talk_tariff = Record_talk_tariff(id=tariff_id)

        if tariff_id == "2":
            record_talk_tariff_active = None
            try:
                record_talk_tariff_active = Record_talk_activated_tariff.objects.get(Q(billing_account_id=profile.billing_account_id) & \
                                                                                     Q(date_activation__lt=datetime.datetime.now()) & \
                                                                                     (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now())))
            except Exception, e:
                print e

            if record_talk_tariff_active:
                record_talk_tariff_active.date_deactivation = datetime.datetime.now()
            else:
                raise Http404

            record_talk_tariff_active_new = Record_talk_activated_tariff()
            record_talk_tariff_active_new.billing_account_id = profile.billing_account_id
            record_talk_tariff_active_new.tariff_id = record_talk_tariff.id
            record_talk_tariff_active_new.date_create = datetime.datetime.now()
            record_talk_tariff_active_new.date_activation = datetime.datetime.now()

            # record_talk_tariff_active_new.user_key = record_talk_tariff_active.user_key
            record_talk_tariff_active_new.save()
            record_talk_tariff_active.save()

            print "no limit"
            bill_acc = BillserviceAccount.objects.get(id=profile.billing_account_id)
            zakaz = Zakazy(
                             section_type=1,
                             service_type_id=9,
                             tariff_id=19,
                             bill_account=bill_acc,
                             status_zakaza_id=2,
                             date_create=datetime.datetime.now(),
                             date_activation=datetime.datetime.now(),
                             connection_cost_id=1,
                             )
            zakaz.save()
            cost = float(cost_dc(zakaz.id))
            zakaz.cost = '%.2f' % cost
            zakaz.save()
            add_record_in_data_centr_payment(zakaz)
            add_record_in_priority_of_services(zakaz)
            rule_obj = Rules_of_drawing_up_documents.objects.get(id=9)
            spis_rules = Check.group_rules(profile, [rule_obj.id], 'type_check', zakaz.id)
            content_check_id = Check.create_check(request.user, spis_rules, False, [zakaz.id])
            dict_documents_for_send = add_document_in_dict_for_send({}, request.user.id, 'Check', content_check_id)
            send_mail_check(dict_documents_for_send)
            if bill_acc.auto_paid:
                write_off_of_money(bill_acc, [zakaz.id])

        else:
            if tariff_id == "1":
                print "tariff Minytnii"
                record_talk_tariff_active = None
                try:
                    record_talk_tariff_active = Record_talk_activated_tariff.objects.get(Q(billing_account_id=profile.billing_account_id) & \
                                                                                         Q(date_activation__lt=datetime.datetime.now()) & \
                                                                                         (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now())))
                except Record_talk_activated_tariff.DoesNotExist, e:
                    raise Http404

                now = datetime.datetime.now()
                date_next_start_month_temp = now + relativedelta(months=1)
                date_next_start_month = datetime.datetime(date_next_start_month_temp.year, date_next_start_month_temp.month, 1, 0, 0, 0)
                record_talk_tariff_active.date_deactivation = date_next_start_month  # pervoe 4islo sled mes9ca

                try:
                    zakaz_obj = Zakazy.objects.get(bill_account__id=profile.billing_account_id, service_type=9, date_deactivation=None)
                    zakaz_obj.date_deactivation = date_next_start_month
                    zakaz_obj.save()
                except Zakazy.DoesNotExist:
                    pass

                record_talk_tariff_active_new = Record_talk_activated_tariff()
                record_talk_tariff_active_new.billing_account_id = profile.billing_account_id
                record_talk_tariff_active_new.tariff_id = record_talk_tariff.id
                record_talk_tariff_active_new.date_create = datetime.datetime.now()
                record_talk_tariff_active_new.date_activation = date_next_start_month
                # record_talk_tariff_active_new.user_key = record_talk_tariff_active.user_key
                record_talk_tariff_active_new.save()
                record_talk_tariff_active.save()
        context["record_talk_tariff_active_true"] = True
        # request.notifications.add(_(u'Тариф успешно изменен'), 'success')
        return HttpResponseRedirect("/account/record_talk/list_record_tariff/?notif=%s" % 'Тариф успешно изменен')
    return context


@login_required
@render_to('create_record_talk.html')
def create_record_talk(request):
    if request.user.get_profile().is_card:
        raise Http404
    profile = request.user.get_profile()
    model = Record_talk()
    model_tariff_active = Record_talk_activated_tariff.objects.get(Q(billing_account_id=profile.billing_account_id) & \
                                                                    Q(date_activation__lt=datetime.datetime.now()) & \
                                                                    (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now())))
    context = {}
    context["title"] = _(u"Запись разговоров: Выбор параметров записи")
    if profile:
        if profile.has_billing_account:
            if profile.billing_account.phones:
                context["have_numbers"] = True
            else:
                context["have_numbers"] = False
    if not request.POST:
        # Первый вызов. Просто отобразить пустую форму.
        form = RecordTalkForm(model=model, profile=profile, request=request)
    else:
        if request.POST.get("submit"):
            form = RecordTalkForm(model=model, data=request.POST, profile=profile, request=request)
            if form.is_valid():  # если форма верная
                model = form.ok_model
                if model:
                    if profile:
                        if profile.has_billing_account:
                            model.billing_account_id = profile.billing_account_id
                            model.tariff_id = model_tariff_active.tariff_id
                            if not os.path.exists(settings.REC_URL + '/%s/%s' % (model.billing_account_id, model.number)):
                                os.makedirs(settings.REC_URL + '/%s/%s' % (model.billing_account_id, model.number))
                            model.save()  # Сохранить ее в базе
                            request.notifications.add(_(u'Запись разговоров номера "%s" активирована' % model.number), 'success')
                            return HttpResponseRedirect("/account/record_talk/list_record_tariff/")
        else:
            return HttpResponseRedirect("/account/record_talk/list_record_tariff/")
    context["current_view_name"] = "list_record_talk_tariff"
    context["form"] = form
    return context


@login_required
@render_to('delete_record_talk.html')
def delete_record_talk(request, record_id):
    """Удаление"""
    profile = request.user.get_profile()
    if not profile:
        raise Http404
    if profile.is_card:
        raise Http404

    context = {}
    context["title"] = _(u"Деактивация записи разговоров")
    model = None

    try:
        model = Record_talk.objects.get(id=record_id)
    except Record_talk.DoesNotExist:
        raise Http404

    context["record"] = model

    if model.billing_account_id != profile.billing_account_id:
        raise Http404
    if request.POST:
        if request.POST.get("submit"):  # если нажали Submit а не Cancel
            if model.billing_account_id != profile.billing_account_id:
                return HttpResponseNotFound()
            if request.POST.get("delete_all") == "on":
                try:
                    conn = connections[settings.BILLING_DB]
                    cur = conn.cursor()
                    model_with_user_key = Record_talk_activated_tariff.objects.get(Q(billing_account_id=profile.billing_account_id) & \
                                                                                    Q(date_activation__lt=datetime.datetime.now()) & \
                                                                                    (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now())))
                except Record_talk_activated_tariff.DoesNotExist:
                    raise Http404
                if model_with_user_key:
                    try:
                        cur.execute("UPDATE billservice_recordtransaction SET file = DEFAULT WHERE answer_user = '%s' AND file IS NOT NULL" % model.number)
                        cur.execute("UPDATE billservice_phonetransaction SET file = DEFAULT WHERE answer_number = '%s' AND file IS NOT NULL" % model.number)
                        transaction.commit_unless_managed(using=settings.BILLING_DB)
                        x = settings.REC_URL + "\\%s\\%s" % (str(model.billing_account_id), model.number,)
                        shutil.rmtree(x.replace("\\", "/"))
                    except Exception, e:
                        print e
            model.delete()
            request.notifications.add(_(u"Запись разговоров номера %s успешно деактивирована" % model.number), "success")
        return HttpResponseRedirect("/account/record_talk/list_record_tariff/")
    context["current_view_name"] = "list_record_talk_tariff"
    return context


@login_required
@render_to('create_record_talk.html')
def edit_record_talk(request, record_id):  # OK!
    """Редактируем"""
    profile = request.user.get_profile()  # получаем профиль текущего пользователя
    if not profile:
        raise Http404
    if profile.is_card:
        raise Http404

    context = {}
    context["title"] = _(u"Редактирование записи")
    context["record_id"] = record_id

    model = None

    try:
        model = Record_talk.objects.get(id=record_id)
    except Record_talk.DoesNotExist:
        raise Http404

    if model.billing_account_id != profile.billing_account_id:
        return HttpResponseNotFound()

    if not request.POST:
        # Первый вызов. Просто отобразить форму.
        form = RecordTalkForm(model=model, profile=profile, request=request)
    else:
        if model.billing_account_id != profile.billing_account_id:
            return HttpResponseNotFound()

        if request.POST.get("submit"):  # если нажали Submit а не Cancel
            # получаем форму из запроса
            form = RecordTalkForm(model=model, data=request.POST, profile=profile, request=request)
            # проверяем на валидность
            if form.is_valid():  # если форма верная
                model = form.ok_model
                if model:
                    model.save()  # Сохранить ее в базе
                    request.notifications.add(_(u"Параметры записи разговоров номера %s успешно изменены" % model.number), "success")
                    return HttpResponseRedirect("/account/record_talk/list_record_tariff/")  # перейти на страницу со списком правил
        else:
            return HttpResponseRedirect("/account/record_talk/list_record_tariff/")

    context["form"] = form
    context["current_view_name"] = "list_record_talk_tariff"
    return context

@login_required
def listen_file_archive(request, filename):
    profile = request.user.get_profile()
    if not profile:
        raise Http404
    if profile.is_card:
        raise Http404

    try:
        fsock = open(settings.REC_URL + '/%s/%s/%s' % (str(profile.billing_account_id), request.GET['id'], filename), 'rb')
        response = HttpResponse(fsock, mimetype='audio/mpeg')
        response['Content-Disposition'] = "attachment; filename='%s" % filename
        response['Content-Length'] = os.stat(settings.REC_URL + '/%s/%s/%s' % (str(profile.billing_account_id), request.GET['id'], filename)).st_size
    except Exception, e:
        print e
        raise Http404

    return response

@login_required
def listen_file(request, filename):
    profile = request.user.get_profile()
    if not profile:
        raise Http404
    if profile.is_card:
        raise Http404

#    try:
#        model_tariff = Record_talk_activated_tariff.objects.get(Q(billing_account_id=profile.billing_account_id) & \
#                                                                Q(date_activation__lt=datetime.datetime.now()) & \
#                                                                (Q(date_deactivation = None) | Q(date_deactivation__gt=datetime.datetime.now())))
#    except Record_talk_activated_tariff.DoesNotExist:
#        raise Http404

    try:
        model_record_talk = Record_talk.objects.get(id=request.GET['id'])
    except Record_talk.DoesNotExist:
        raise Http404

    try:
#        from django.core.servers.basehttp import FileWrapper
#        class FixedFileWrapper(FileWrapper):
#            def __iter__(self):
#                self.filelike.seek(0)
#                return self
#            def __len__(self):
#                return 1500000
#                if 'Content-Length' in self._headers:
#                    return int(self._headers.get('Content-Length', len(self._container)))
#
#        filename2 = REC_URL + '/%s/%s/%s' % (str(profile.billing_account_id), model_record_talk.number, filename)  # Select your file here.
#        wrapper = FileWrapper(file(filename2))
#        response = HttpResponse(wrapper, content_type='text/plain')
#        response['Content-Length'] = os.path.getsize(filename2)
#        response['Content-Disposition'] = "attachment; filename='%s" % filename
#        response.streaming = True
#        return response
#
#


        fsock = open(settings.REC_URL + '/%s/%s/%s' % (str(profile.billing_account_id), model_record_talk.number, filename), 'rb')
        response = HttpResponse(fsock, mimetype='audio/mpeg')
        response['Content-Disposition'] = "attachment; filename='%s" % filename
        response['Content-Length'] = os.stat(settings.REC_URL + '/%s/%s/%s' % (str(profile.billing_account_id), model_record_talk.number, filename)).st_size
        # response['Accept-Ranges'] = 'bytes'
        # response['Content-Length'] = 1024000

    except Exception, e:
        raise Http404

    return response


def listen_file_transaction(request, number, filename):
    profile = request.user.get_profile()
#     print "FILENAME  = ", filename
#     print "PATH = ", os.path.join(REC_URL, str(profile.billing_account_id), number, filename)
    if not profile:
        raise Http404
    try:
        fsock = open(os.path.join(settings.REC_URL, str(profile.billing_account_id), number, filename), 'rb')
        response = HttpResponse(fsock, mimetype='audio/mpeg')
        response['Content-Disposition'] = "attachment; filename='%s" % filename
        response['Content-Length'] = os.stat(os.path.join(settings.REC_URL, str(profile.billing_account_id), number, filename)).st_size
    except Exception, e:
        print "Exception in fs.record_talk.listen_file_transaction = ", e
        raise Http404
    return response

@login_required
def delete_file_archive(request, filename):
    profile = request.user.get_profile()
    if not profile:
        raise Http404
    if profile.is_card:
        raise Http404

    try:
        conn = connections[settings.BILLING_DB]
        cur = conn.cursor()
        cur.execute("UPDATE billservice_recordtransaction SET file = DEFAULT WHERE file = '%s'" % filename)
        cur.execute("UPDATE billservice_phonetransaction SET file = DEFAULT WHERE file = '%s'" % filename)
        transaction.commit_unless_managed(using=settings.BILLING_DB)
        os.remove(settings.REC_URL + '/%s/%s/%s' % (str(profile.billing_account_id), request.GET['id'], filename))
    except Exception, e:
        print "Exception:%s" % e
        raise Http404

    return HttpResponseRedirect("/account/record_talk/myarchive/%s" % request.GET['id'])


@login_required
def delete_file(request, filename):
    profile = request.user.get_profile()
    if not profile:
        raise Http404
    if profile.is_card:
        raise Http404

#    try:
#        model_tariff = Record_talk_activated_tariff.objects.get(Q(billing_account_id=profile.billing_account_id) & \
#                                                                Q(date_activation__lt=datetime.datetime.now()) & \
#                                                                (Q(date_deactivation = None) | Q(date_deactivation__gt=datetime.datetime.now())))
#    except Record_talk_activated_tariff.DoesNotExist:
#        raise Http404

    try:
        model_record_talk = Record_talk.objects.get(id=request.GET['id'])
    except Record_talk.DoesNotExist:
        raise Http404
    try:
        conn = connections[settings.BILLING_DB]
        cur = conn.cursor()
    except Exception:
        raise Http404

    try:
        os.remove(settings.REC_URL + '/%s/%s/%s' % (str(profile.billing_account_id), model_record_talk.number, filename))
        cur.execute("UPDATE billservice_recordtransaction SET file = DEFAULT WHERE file = '%s'" % filename)
        cur.execute("UPDATE billservice_phonetransaction SET file = DEFAULT WHERE file = '%s'" % filename)
        transaction.commit_unless_managed(using=settings.BILLING_DB)
    except Exception, e:
        print "Exception:%s" % e
        raise Http404

    return HttpResponseRedirect("/account/record_talk/listen/%s/" % request.GET['id'])


@login_required
@render_to('listen_record_talk.html')
def listen_record_talk(request, record_id):  # OK!
    from lib.paginator import SimplePaginator
    """Прослушиваем"""

    if request.user.get_profile().is_card:
        raise Http404

    context = {}
    context["title"] = _(u"Прослушивание записей")
    context["record_id"] = record_id


    profile = request.user.get_profile()
    model = None

    try:
        model = Record_talk.objects.get(id=record_id)
    except Record_talk.DoesNotExist:
        raise Http404

    try:
        model_tariff = Record_talk_activated_tariff.objects.get(Q(billing_account_id=profile.billing_account_id) & \
                                                                Q(date_activation__lt=datetime.datetime.now()) & \
                                                                (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now())))
    except Record_talk_activated_tariff.DoesNotExist:
        raise Http404

    try:
        all_users_files = glob.glob(settings.REC_URL + '/%s/%s/*.*' % (profile.billing_account_id, model.number))
        print settings.REC_URL + '/%s/%s/*.*' % (profile.billing_account_id, model.number)
    except:
        pass
    for i, one in enumerate(all_users_files):
        one = one.split('\\')[-1]
        all_users_files[i] = one

    kort = []
    for file in all_users_files:
        file_not_mp3 = file.strip(".mp3").split("/")[-1]
        print file_not_mp3
        kort.append(dict(name=file.split("/")[-1], date=file_not_mp3.split("_")[-3], called=file_not_mp3.split("_")[-2], caller=file_not_mp3.split("_")[-1]))
    # context["record"] = model
    try:
        if request.GET['sort'] == 'DOWN':
            kort = sorted(kort, key=lambda k: k[request.GET['id']], reverse=True)
        elif request.GET['sort'] == 'UP':
            kort = sorted(kort, key=lambda k: k[request.GET['id']], reverse=False)
    except:
        kort = sorted(kort, key=lambda k: k['date'])
    context["all_users_files"] = kort

    query = get_query_string(request, exclude=("page",))
    paginator = SimplePaginator(kort, 10, "?page=%%s&%s" % query)
    paginator.set_page(request.GET.get("page", 1))
    context['all_users_files2'] = paginator.get_page()
    context["paginator"] = paginator
    # context["url"] ='/media/fs_sounds/records_talk/%s-%s/%s/' % (profile.billing_account_id, model_tariff.user_key, model.number)
    if model:
        if model.billing_account_id != profile.billing_account_id:
            raise Http404
    else:
        raise Http404

    context["current_view_name"] = "list_record_talk_tariff"
    return context


@login_required
@render_to('myarchive.html')
def myarchive(request, numb=None):  # OK!
    from lib.paginator import SimplePaginator
    """Прослушиваем архив"""

    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context["title"] = _(u"Архив записей")
    str = ""
    profile = request.user.get_profile()
    model = None
    all_users_files = []
    all_number = []
    all_users_number = []
    try:
        all_user_number = os.listdir(settings.REC_URL + '/%s' % (profile.billing_account_id))
    except Exception, e:
        request.notifications.add(_(u"У Вас не было подключено услуги 'Запись разговора'. Архив пуст"), "error")
        return HttpResponseRedirect("/account/record_talk/list_record_tariff/")  # перейти на страницу со списком правил
    # for model in all_user_number:
    if numb:
        try:
            all_users_files.append(glob.glob(settings.REC_URL + '/%s/%s/*.*' % (profile.billing_account_id, numb)))
            # all_number.append(model)
        except Exception, e:
            print e
            raise Http404

        for x in all_users_files:
            for i, one in enumerate(x):
                one = one.split('\\')[-1]
                x[i] = one

        kort = []

        for x in all_users_files:
            for file in x:
                file_not_mp3 = file.strip(".mp3").split("/")[-1]
                kort.append(dict(name=file.split("/")[-1], date=file_not_mp3.split("_")[-3], called=file_not_mp3.split("_")[-2], caller=file_not_mp3.split("_")[-1]))

        try:
            if request.GET['sort'] == 'DOWN':
                kort = sorted(kort, key=lambda k: k[request.GET['id']], reverse=True)
            elif request.GET['sort'] == 'UP':
                kort = sorted(kort, key=lambda k: k[request.GET['id']], reverse=False)
        except:
            kort = sorted(kort, key=lambda k: k['date'])
        context["all_users_files"] = kort
        query = get_query_string(request, exclude=("page",))
        paginator = SimplePaginator(kort, 10, "?page=%%s&%s" % query)
        paginator.set_page(request.GET.get("page", 1))
        context['all_users_files2'] = paginator.get_page()
        context["paginator"] = paginator
        context["current_view_name"] = "list_record_talk_tariff"
        context["num"] = numb
        return context

    for number in all_user_number:
        str += """<h1 class="title"><a href="/account/record_talk/myarchive/%s/">%s &#9834</a></h1>""" % (number, number,)
    context["all_number"] = str
    context["current_view_name"] = "list_record_talk_tariff"
    return context

