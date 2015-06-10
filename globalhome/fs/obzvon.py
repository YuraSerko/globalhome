# -*- coding=utf-8 -*-
# Create your views here.
import os, sys
import copy
import json
from lib.decorators import render_to, login_required
from settings import *
from settings import BILLING_DB, MEDIA_ROOT, FREESWITCH, OBZVON_URL, SCRIPT_ROOT
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponse
from forms import Obzvon, ArticleForm
from models import ObzvonModel, ObzvonNumber, create_myivr_temp, create_myivr
from billing.models import BillserviceAccount
from telnumbers.models import TelNumber
import subprocess
#from django.utils.functional import curry
from django.forms.formsets import formset_factory
#from my_ivr import handle_uploaded_image, convert_file
#from lib.mail import send_email
import paramiko
import codecs
import time
from datetime import datetime
#from celery.schedules import crontab
try:
    from crontab import CronTab
    from tasks import delayed_function
    from celery.task.control import revoke
except:
    pass

def getLength(filename):
    result = subprocess.Popen(["ffprobe", filename],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return [x for x in result.stdout.readlines() if "Duration" in x]

def download_file(f):
    destination = open(OBZVON_URL + "\\obzvon\\doc" % f, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

def createSSHClient(server, port, user, password):
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server, port, user, password)
        return client
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print "Exception in createSSHClient: file:%s line:%s" % (fname, exc_tb.tb_lineno)

def list_preold(profile, stat, type):
    list_id = []
    try:
        if type == '':
            if stat == 1 or stat == 3 or stat == 4:
                model_obzvon = ObzvonModel.objects.filter(billing_account_id=profile.billing_account_id, status=stat)
        elif type == 'one':
            model_obzvon = ObzvonModel.objects.filter(billing_account_id=profile.billing_account_id, status=stat, one_times = True)
        elif type == 'many':
            model_obzvon = ObzvonModel.objects.filter(billing_account_id=profile.billing_account_id, status=stat, many_times = True)
    except ObzvonModel.DoesNotExist:
        raise Http404
    for model in model_obzvon:
        list_number = []
        model_number = ObzvonNumber.objects.filter(billing_account_id=profile.billing_account_id, id_obzvon=model.id)
        for numb in model_number:
            list_number.append(numb.number)
        list_id.append({'from_number':model.from_number, 'file':str(model.file).split("/")[-1], 'id':model.id, 'mynewkey':','.join(list_number), 'date_start':model.date_start, 'status':model.status})
    return list_id

@login_required
@render_to('obzvon.html')
def obzvon(request):
    """
        Обзвон
    """
    if request.user.get_profile().is_card:
        raise Http404

    context = {}
    context["title"] = _(u"Текущие обзвоны")
    context["title2"] = _(u"Завершенные обзвоны")
    context["title3"] = _(u"Отложенные обзвоны")
    context["title4"] = _(u"Повторяющиеся обзвоны")
    profile = request.user.get_profile()
    if profile:
        if profile.has_billing_account:
            if profile.billing_account.phones:
                context["have_numbers"] = True
            else:
                context["have_numbers"] = False

    context["model_obzvon_preold"] = list_preold(profile, 3, '')
    context["model_obzvon_preold"] += list_preold(profile, 4, '')
    context["model_obzvon_old"] = list_preold(profile, 1, '')
    context["model_obzvon_one_times"] = list_preold(profile, 0, 'one')
    context["model_obzvon_many_times"] = list_preold(profile, 0, 'many')
    context['current_view_name'] = 'obzvon'
    return context

def save_model_number(id, number, add, profile, duration, from_file):
    try:
        model_number = ObzvonNumber(
        billing_account_id=profile.billing_account_id,
        number=number,
        add_number=add,
        id_obzvon_id=id,
        duration=duration,
        number_from_file=from_file,)
        model_number.save()
    except Exception, e:
        import log
        log.add("Exception in save_model_number: '%s'" % e)
        exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        log.add("Exception in save_model_number: file:%s line:%s" % (fname, exc_tb.tb_lineno))

def save_model_number_ivr(id, number, nabor, profile):
    model_ivr = create_myivr()
    model_ivr.billing_account_id = profile.billing_account_id
    model_ivr.nabor = nabor
    model_ivr.call = number
    model_ivr.id_ivr_id = id
    model_ivr.save()  # Сохранить ее в базе

def get_duration(file_url):
    import wave
    import contextlib
    with contextlib.closing(wave.open(file_url, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
    return duration


@login_required
@render_to('obzvon_edit.html')
def obzvon_edit(request, id_edit):
    """
        Обзвон edit
    """
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context["title"] = _(u"Edit обзвон")
    profile = request.user.get_profile()
    try:
        model = ObzvonModel.objects.get(id=id_edit)
    except ObzvonModel.DoesNotExist, e:
        raise Http404
    model_number = ObzvonNumber.objects.filter(id_obzvon=model.id, number_from_file=False)
    pub_date_list = []
    for x in model_number:
        pub_date_list.append({'pub_date':x.number, 'pub_date_add':x.add_number})

    #ivr_list = []
    ArticleFormSet = formset_factory(ArticleForm, extra=0)
    bac = []
    bac.append(profile.billing_account)
    numbers = []
    for ww in BillserviceAccount.objects.filter(assigned_to=profile.billing_account_id):
        bac.append(ww)
    for ba in bac:
        numbers += TelNumber.objects.filter(account=ba)

    ivrs = create_myivr_temp.objects.filter(billing_account_id_temp=profile.billing_account_id)
    if ivrs:
        context["ivrs"] = ivrs
        if model.obzvon_ivr.all():
            context["select_ivr"] = model.obzvon_ivr.all()[0].id

    xString = ''
    if profile.billing_account.phones:
        context["have_numbers"] = True
    else:
        context["have_numbers"] = False
    if not request.POST:
        context['day_of_week'] = model.day_of_week
        context['day_of_month'] = model.day_of_month
        formset = ArticleFormSet(initial=pub_date_list)
        form = Obzvon(model=model, profile=profile, request=request)
    else:
        # проверяем на валидность
        one_field = False
        pre_one_times = model.one_times
        pre_many_times = model.many_times
        task_obzvon_id = model.id
#        pre_from_number = model.from_number
#        formset_ivr = NumberIvr(request.POST, prefix='number')
        formset = ArticleFormSet(request.POST)
        form = Obzvon(model=model, data=request.POST, profile=profile, request=request)
        if form.is_valid():  # если форма верная
            if formset.is_valid():
                for form_set in formset.forms:
                    if not form_set.has_changed() and len(formset) > 1:
                        request.notifications.add(_(u"Не заполнены поля 'На номер'"), "error")
                        context['formset'] = formset
                        #context['formset_ivr'] = formset_ivr
                        context['form'] = form
                        return context
                    elif not form_set.has_changed():
                        if not form.cleaned_data['file_text']:
                            request.notifications.add(_(u"Не заполнено поле 'На номер'"), "error")
                            context['formset'] = formset
                            #context['formset_ivr'] = formset_ivr
                            context['form'] = form
                            return context
                        else:
                            one_field = True

                if not one_field:
                    for form_set in formset.forms:
                        if str(form_set.cleaned_data['pub_date'])[:4]=='8800' or str(form_set.cleaned_data['pub_date'])[:4]=='7800':
                            request.notifications.add(_(u"Запрещено запускать обзвон на номера 8(800) и 7(800)"), "error")
                            context['formset'] = formset
                            context['form'] = form
                            return context

                model = form.ok_model

                if model:
                    model_copy = copy.copy(model)
                    model_copy.id = None
                    model_copy.billing_account_id = profile.billing_account_id
                    model_copy.status = 0
                    if form.cleaned_data['many_times'] == 'True':
                        if form.cleaned_data['obzvon_day_enabled'] == 'True':
                            model_copy.day_of_week = request.POST.get('all_check_day_of_week')
                            model_copy.day_of_month = ''
                        else:
                            if form.cleaned_data['obzvon_concretic_day_enabled'] == 'True':
                                model_copy.day_of_month = request.POST.get('all_check_day')
                                model_copy.day_of_week = ''
                    else:
                        model_copy.day_of_week = ''
                        model_copy.day_of_month = ''

                    try:
                        model_copy.save()
                        model.delete()
                    except Exception, e:
                        print e

#                    id_ivr = "0"
                    #new_file = True
                    if form.cleaned_data['answer_ivr']:
                        for ivr in ivrs:
                            if request.POST.get(str(ivr.id)) == "on":
                                model_copy.obzvon_ivr.add(ivr.id)
                                #ivr_on = True
                                duration = get_duration(ivr.file_wav)
#                                filename = ivr.file_wav
#                                id_ivr = str(ivr.id)
                    else:
                        duration = get_duration(model_copy.file)
#                        filename = model_copy.file

                    # # проверка файла со списком номеров
                    if form.cleaned_data['file_text']:
                        try:
                            xfile = codecs.open("files/sounds/all_files/" + str(model_copy.file_text), encoding='UTF-8')
                            xString = xfile.read()
                            cifri = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', ',']
                            for i in xString:
                                if i not in cifri:
                                    raise
                        except Exception, e:
                            request.notifications.add(_(u"Не правильно заполнен файл со списком номеров для обзвона"), "error")
                            context['formset'] = formset
                            # context['formset_ivr'] = formset_ivr
                            context['form'] = form
                            print e
                            return context

                    if not one_field:
                        for form_set in formset.forms:
                            if form_set.cleaned_data['pub_date_add']:
                                save_model_number(model_copy.id, form_set.cleaned_data['pub_date'], form_set.cleaned_data['pub_date_add'], profile, duration, False)
                            else:
                                save_model_number(model_copy.id, form_set.cleaned_data['pub_date'], "", profile, duration, False)


                    if xString != '':
                        for num in xString.split(","):
                            if num[:4]!='8800' and num[:4]!='7800':
                                if "-" in num:
                                    save_model_number(model_copy.id, num.split("-")[0], num.split("-")[1], profile, duration, True)
                                else:
                                    save_model_number(model_copy.id, num, "", profile, duration, True)
                            else:
                                request.notifications.add(_(u"Запрещено запускать обзвон на номера 8(800) и 7(800)"), "error")
                                context['formset'] = formset
                                context['form'] = form
                                return context

                    cron = CronTab('www-data')
                    if pre_one_times:
                        revoke(task_obzvon_id, terminate=True)
                    if pre_many_times:
                        #cron = CronTab('root')
                        print 'cd %s/fs/ && /home/sites/gh/venv/bin/python test.py %s' % (os.path.abspath(os.curdir), task_obzvon_id)
                        cron.remove_all('cd %s/fs/ && /home/sites/gh/venv/bin/python test.py %s' % (os.path.abspath(os.curdir), task_obzvon_id))
                        cron.write()

                    if form.cleaned_data['one_times'] == 'True':
                        today = datetime.combine(form.cleaned_data['date_to'], form.cleaned_data['obzvon_time_for_one'])
                        #revoke(task_obzvon_id, terminate=True)
                        delayed_function.apply_async((model_copy.id, 'post'), task_id=str(model_copy.id), eta=today)
                    else:
                        if form.cleaned_data['many_times'] == 'True':
                            job = cron.new(command="""cd %s/fs/ && /home/sites/gh/venv/bin/python test.py %s repeat %s >> /dev/null &""" % (os.path.abspath(os.curdir), model_copy.id, SCRIPT_ROOT))
                            not_time = False
                            if form.cleaned_data['obzvon_time_enabled'] == 'True':
                                job.minute.on(form.cleaned_data['obzvon_time'].minute)
                                job.hour.on(form.cleaned_data['obzvon_time'].hour)
                            else:
                                not_time = True
                            if form.cleaned_data['obzvon_day_enabled'] == 'True':
                                job.dow.on(*request.POST.get('all_check_day_of_week').strip(',').split(','))
                                if not_time:
                                    job.minute.on('00')
                                    job.hour.on('00')
                            else:
                                if form.cleaned_data['obzvon_concretic_day_enabled'] == 'True':
                                    job.dom.on(*request.POST.get('all_check_day').strip(',').split(','))
                                    if not_time:
                                        job.minute.on('00')
                                        job.hour.on('00')
                                else:
                                    if not_time:
                                        request.notifications.add(_(u"Выберите хотя бы один параметр в повторяющемся обзвоне"), "error")
                                        context['formset'] = formset
                                        context['form'] = form
                                        return context
                            cron.write()
                            print cron.render()

                    request.notifications.add(_(u"Обзвон изменен."), "success")
                    return HttpResponseRedirect("/account/obzvon/")  # перейти на страницу со списком правил
                else:
                    context['formset'] = formset
                    context['form'] = form
                    return context
            else:
                request.notifications.add(_(u"Не правильно заполнены поля на номер"), "error")
                context['formset'] = formset
                context['form'] = form
                return context
        # else:
        #    return HttpResponseRedirect("/account/obzvon/")
    context['form'] = form
    context['formset'] = formset
    context['current_view_name'] = 'obzvon'
    return context


@login_required
@render_to('obzvon_new.html')
def obzvon_repeat(request, id_repeat):
    """
        Обзвон repeat
    """
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context["title"] = _(u"Повторить обзвон")
    profile = request.user.get_profile()
    try:
        model = ObzvonModel.objects.get(id=id_repeat)
    except ObzvonModel.DoesNotExist, e:
        raise Http404
    model_number = ObzvonNumber.objects.filter(id_obzvon=model.id, number_from_file=False)
    pub_date_list = []
    for x in model_number:
        pub_date_list.append({'pub_date':x.number, 'pub_date_add':x.add_number})

    #ivr_list = []
    ArticleFormSet = formset_factory(ArticleForm, extra=0)
    bac = []
    bac.append(profile.billing_account)
    numbers = []
    for ww in BillserviceAccount.objects.filter(assigned_to=profile.billing_account_id):
        bac.append(ww)
    for ba in bac:
        numbers += TelNumber.objects.filter(account=ba)

    ivrs = create_myivr_temp.objects.filter(billing_account_id_temp=profile.billing_account_id)
    if ivrs:
        context["ivrs"] = ivrs
        if model.obzvon_ivr.all():
            context["select_ivr"] = model.obzvon_ivr.all()[0].id

    xString = ''
    if profile.billing_account.phones:
        context["have_numbers"] = True
    else:
        context["have_numbers"] = False
    if not request.POST:
        context['day_of_week'] = model.day_of_week
        context['day_of_month'] = model.day_of_month
        formset = ArticleFormSet(initial=pub_date_list)
        form = Obzvon(model=model, profile=profile, request=request)
    else:
        # проверяем на валидность
        one_field = False
#        formset_ivr = NumberIvr(request.POST, prefix='number')
        formset = ArticleFormSet(request.POST)
        form = Obzvon(model=model, data=request.POST, profile=profile, request=request)
        if form.is_valid():  # если форма верная
            if formset.is_valid():
                for form_set in formset.forms:
                    if not form_set.has_changed() and len(formset) > 1:
                        request.notifications.add(_(u"Не заполнены поля 'На номер'"), "error")
                        context['formset'] = formset
                        context['form'] = form
                        return context
                    elif not form_set.has_changed():
                        if not form.cleaned_data['file_text']:
                            request.notifications.add(_(u"Не заполнено поле 'На номер'"), "error")
                            context['formset'] = formset
                            context['form'] = form
                            return context
                        else:
                            one_field = True

                if not one_field:
                    for form_set in formset.forms:
                        if str(form_set.cleaned_data['pub_date'])[:4]=='8800' or str(form_set.cleaned_data['pub_date'])[:4]=='7800':
                            request.notifications.add(_(u"Запрещено запускать обзвон на номера 8(800) и 7(800)"), "error")
                            context['formset'] = formset
                            context['form'] = form
                            return context

                model = form.ok_model

                if model:
                    model_copy = copy.copy(model)
                    model_copy.id = None
                    model_copy.billing_account_id = profile.billing_account_id
                    model_copy.status = 0
                    try:
                        model_copy.save()
                    except Exception, e:
                        print e

                    #id_ivr = "0"
                    #new_file = True
                    duration = 0
                    if form.cleaned_data['answer_ivr']:
                        for ivr in ivrs:
                            if request.POST.get(str(ivr.id)) == "on":
                                model_copy.obzvon_ivr.add(ivr.id)
                                #ivr_on = True
                                duration = get_duration(ivr.file_wav)
                                #filename = ivr.file_wav
                                #id_ivr = str(ivr.id)
                    else:
                        duration = get_duration(model_copy.file)
                        #filename = model_copy.file

                    # # проверка файла со списком номеров
                    if form.cleaned_data['file_text']:
                        try:
                            xfile = codecs.open("files/sounds/all_files/" + str(model_copy.file_text), encoding='UTF-8')
                            xString = xfile.read()
                            cifri = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', ',']
                            for i in xString:
                                if i not in cifri:
                                    raise
                        except Exception, e:
                            request.notifications.add(_(u"Не правильно заполнен файл со списком номеров для обзвона"), "error")
                            context['formset'] = formset
                            # context['formset_ivr'] = formset_ivr
                            context['form'] = form
                            print e
                            return context

                    if not one_field:
                        for form_set in formset.forms:
                            if form_set.cleaned_data['pub_date_add']:
                                save_model_number(model_copy.id, form_set.cleaned_data['pub_date'], form_set.cleaned_data['pub_date_add'], profile, duration, False)
                            else:
                                save_model_number(model_copy.id, form_set.cleaned_data['pub_date'], "", profile, duration, False)


                    if xString != '':
                        for num in xString.split(","):
                            if num[:4]!='8800' and num[:4]!='7800':
                                if "-" in num:
                                    save_model_number(model_copy.id, num.split("-")[0], num.split("-")[1], profile, duration, True)
                                else:
                                    save_model_number(model_copy.id, num, "", profile, duration, True)
                            else:
                                request.notifications.add(_(u"Запрещено запускать обзвон на номера 8(800) и 7(800)"), "error")
                                context['formset'] = formset
                                context['form'] = form
                                return context


                    if form.cleaned_data['one_times'] == 'True':
                        print "TYT TIME !!!"
                        print os.path.abspath(os.curdir)
                        today = datetime.combine(form.cleaned_data['date_to'], form.cleaned_data['obzvon_time_for_one'])
                        delayed_function.apply_async((model_copy.id, 'repeat'), task_id=str(model_copy.id), eta=today)
                        #delayed_function.apply_async((model.from_number, model.id, filename, model.answer_dtmf, model.dtmf_wait_time, model.count_call, id_ivr, 'post'), task_id=model_copy.id, eta=today)
                    else:
                        if form.cleaned_data['many_times'] == 'True':
                            cron = CronTab('www-data')
                            not_time = False
                            #cron.remove_all('python')
                            job = cron.new(command="""cd %s/fs/ && /home/sites/gh/venv/bin/python test.py %s repeat %s >> /dev/null &""" % (os.path.abspath(os.curdir), model.id, SCRIPT_ROOT))
                            if form.cleaned_data['obzvon_time_enabled'] == 'True':
                                job.minute.on(form.cleaned_data['obzvon_time'].minute)
                                job.hour.on(form.cleaned_data['obzvon_time'].hour)
                            else:
                                not_time = True
                            if form.cleaned_data['obzvon_day_enabled'] == 'True':
                                print "many_times2"
                                job.dow.on(*request.POST.get('all_check_day_of_week').strip(',').split(','))
                                if not_time:
                                    job.minute.on('00')
                                    job.hour.on('00')
                            else:
                                if form.cleaned_data['obzvon_concretic_day_enabled'] == 'True':
                                    print "many_times3"
                                    job.dom.on(*request.POST.get('all_check_day').strip(',').split(','))
                                    if not_time:
                                        job.minute.on('00')
                                        job.hour.on('00')
                                else:
                                    if not_time:
                                        request.notifications.add(_(u"Выберите хотя бы один параметр в повторяющемся обзвоне"), "error")
                                        context['formset'] = formset
                                        context['form'] = form
                                        return context
                            cron.write()
                            print cron.render()
                        else:
                            try:
#                                ssh = createSSHClient(FREESWITCH['fs1']['SSH_HOST'], FREESWITCH['fs1']['SSH_PORT'], FREESWITCH['fs1']['SSH_USER'], FREESWITCH['fs1']['SSH_PASSWORD'])
#                                command = """/usr/local/freeswitch/python/potok_for_obzvon.py %s repeat > /dev/null &""" % (model.id)
#                                print command
#                                stdin, stdout, stderr = ssh.exec_command(command)
                                #os.system("""%s/potok_for_obzvon.py %s repeat""" % (SCRIPT_ROOT, model.id))
                                subprocess.Popen("""/home/sites/gh/venv/bin/python %s/potok_for_obzvon.py %s repeat >> /dev/null &""" % (SCRIPT_ROOT, model.id), shell=True, stdout=subprocess.PIPE)
                                print """/home/sites/gh/venv/bin/python %s/potok_for_obzvon.py %s repeat >> /dev/null &""" % (SCRIPT_ROOT, model.id)
                            except Exception, e:
                                print e

                    request.notifications.add(_(u"Обзвон запущен. Вы можете посмотреть процесс его выполнения во вкладке 'Текущие обзвоны'"), "success")
                    return HttpResponseRedirect("/account/obzvon/")  # перейти на страницу со списком правил
                else:
                    context['formset'] = formset
                    context['form'] = form
                    return context
            else:
                request.notifications.add(_(u"Не правильно заполнены поля на номер"), "error")
                context['formset'] = formset
                context['form'] = form
                return context
        # else:
        #    return HttpResponseRedirect("/account/obzvon/")
    context['form'] = form
    context['formset'] = formset
    context['current_view_name'] = 'obzvon'
    return context


@login_required
@render_to('obzvon_new.html')
def obzvon_new(request):
    """
        Новый Обзвон
    """
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context["title"] = _(u"Запуск нового обзвона")
    profile = request.user.get_profile()
    bac = []
    bac.append(profile.billing_account)
    numbers = []
    for ww in BillserviceAccount.objects.filter(assigned_to=profile.billing_account_id):
        bac.append(ww)
    for ba in bac:
        for qq in TelNumber.objects.filter(account=ba):
            numbers.append(qq)
    model = ObzvonModel()
    ArticleFormSet = formset_factory(ArticleForm)
    xString = ''
    if profile:
        if profile.has_billing_account:
            if profile.billing_account.phones:
                context["have_numbers"] = True
            else:
                context["have_numbers"] = False

    ivrs = create_myivr_temp.objects.filter(billing_account_id_temp=profile.billing_account_id)
    context["ivrs"] = ivrs

    if not request.POST:
        # formset_ivr = NumberIvr(prefix='number')
        formset = ArticleFormSet()
        form = Obzvon(model=model, profile=profile, request=request)
    else:
        # проверяем на валидность
        one_field = False
        formset = ArticleFormSet(request.POST)
        form = Obzvon(model=model, data=request.POST, profile=profile, request=request)

        if form.is_valid():  # если форма верная
            if formset.is_valid():
                for form_set in formset.forms:
                    print type(form_set.cleaned_data['pub_date'])
                    print form_set.cleaned_data['pub_date']
#                    if str(form_set.cleaned_data['pub_date'])[:4]!='8800':
#                        print "aaaa"
                    if str(form_set.cleaned_data['pub_date'])[:4]!='8800' and str(form_set.cleaned_data['pub_date'])[:4]!='7800':
                        if form_set.cleaned_data['pub_date_add']:
                            save_model_number(model.id, form_set.cleaned_data['pub_date'], form_set.cleaned_data['pub_date_add'], profile, 0, False)
                        else:
                            save_model_number(model.id, form_set.cleaned_data['pub_date'], "", profile, 0, False)
                    else:
                        request.notifications.add(_(u"Запрещено запускать обзвон на номера 8(800) и 7(800)"), "error")
                        context['formset'] = formset
                        context['form'] = form
                        return context
                for form_set in formset.forms:
                    if not form_set.has_changed() and len(formset) > 1:
                        request.notifications.add(_(u"Не заполнены поля 'На номер'"), "error")
                        context['formset'] = formset
                        context['form'] = form
                        return context
                    elif not form_set.has_changed():
                        if not form.cleaned_data['file_text']:
                            request.notifications.add(_(u"Не заполнено поле 'На номер'"), "error")
                            context['formset'] = formset
                            context['form'] = form
                            return context
                        elif not form_set.has_changed():
                            if not form.cleaned_data['file_text']:
                                request.notifications.add(_(u"Не заполнено поле 'На номер'"), "error")
                                context['formset'] = formset
                                context['form'] = form
                                return context
                            else:
                                one_field = True

                if not one_field:
                    for form_set in formset.forms:
                        if str(form_set.cleaned_data['pub_date'])[:4]=='8800' or str(form_set.cleaned_data['pub_date'])[:4]=='7800':
                            request.notifications.add(_(u"Запрещено запускать обзвон на номера 8(800) и 7(800)"), "error")
                            context['formset'] = formset
                            context['form'] = form
                            return context

                model = form.ok_model
                if model:

                    model.billing_account_id = profile.billing_account_id
                    if form.cleaned_data['many_times'] == 'True':
                        if form.cleaned_data['obzvon_day_enabled'] == 'True':
                            model.day_of_week = request.POST.get('all_check_day_of_week')
                        else:
                            if form.cleaned_data['obzvon_concretic_day_enabled'] == 'True':
                                model.day_of_month = request.POST.get('all_check_day')
                    try:
                        model.save()
                    except Exception, e:
                        print e

                    #id_ivr = "0"
                    duration = 0
                    if form.cleaned_data['answer_ivr']:
                        for ivr in ivrs:
                            if request.POST.get(str(ivr.id)) == "on":
                                model.obzvon_ivr.add(ivr.id)
                                print "ivr.file_wav"
                                print ivr.file_wav
                                duration = get_duration(ivr.file_wav)
                                #filename = ivr.file_wav
                                #id_ivr = str(ivr.id)
                    else:
                        duration = get_duration(model.file)
                        #filename = model.file
                    # # проверка файла со списком номеров
                    if form.cleaned_data['file_text']:
                        try:
                            xfile = codecs.open("files/sounds/all_files/obzvon/" + str(profile.billing_account_id) + "/doc/" + str(request.FILES['file_text']), encoding='UTF-8')
                            xString = xfile.read()
                            cifri = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', ',']
                            for i in xString:
                                if i not in cifri:
                                    raise
                        except Exception, e:
                            request.notifications.add(_(u"Не правильно заполнен файл со списком номеров для обзвона"), "error")
                            context['formset'] = formset
                            # context['formset_ivr'] = formset_ivr
                            context['form'] = form
                            return context

                    if not one_field:
                        for form_set in formset.forms:
                            if form_set.cleaned_data['pub_date_add']:
                                save_model_number(model.id, form_set.cleaned_data['pub_date'], form_set.cleaned_data['pub_date_add'], profile, duration, False)
                            else:
                                save_model_number(model.id, form_set.cleaned_data['pub_date'], "", profile, duration, False)


                    if xString != '':
                        for num in xString.split(","):
                            if num[:4]!='8800' and num[:4]!='7800':
                                if "-" in num:
                                    save_model_number(model.id, num.split("-")[0], num.split("-")[1], profile, duration, True)
                                else:
                                    save_model_number(model.id, num, "", profile, duration, True)
                            else:
                                request.notifications.add(_(u"Запрещено запускать обзвон на номера 8(800) и 7(800)"), "error")
                                context['formset'] = formset
                                context['form'] = form
                                return context

                    if form.cleaned_data['one_times'] == 'True':
                        print "TYT TIME !!!"
                        print os.path.abspath(os.curdir)
                        today = datetime.combine(form.cleaned_data['date_to'], form.cleaned_data['obzvon_time_for_one'])
                        delayed_function.apply_async((model.id, 'post'), task_id=str(model.id), eta=today)
                    else:
                        if form.cleaned_data['many_times'] == 'True':
                            cron = CronTab('www-data')
                            not_time = False
                            #cron.remove_all('python')
                            job = cron.new(command="""cd %s/fs/ && /home/sites/gh/venv/bin/python test.py %s repeat %s >> /dev/null &""" % (os.path.abspath(os.curdir), model.id, SCRIPT_ROOT))
                            if form.cleaned_data['obzvon_time_enabled'] == 'True':
                                job.minute.on(form.cleaned_data['obzvon_time'].minute)
                                job.hour.on(form.cleaned_data['obzvon_time'].hour)
                                print form.cleaned_data['obzvon_time'].minute
                                print type(form.cleaned_data['obzvon_time'].minute)
                            else:
                                not_time = True
                            if form.cleaned_data['obzvon_day_enabled'] == 'True':
                                job.dow.on(*request.POST.get('all_check_day_of_week').strip(',').split(','))
                                if not_time:
                                    job.minute.on('00')
                                    job.hour.on('00')
                            else:
                                if form.cleaned_data['obzvon_concretic_day_enabled'] == 'True':
                                    job.dom.on(*request.POST.get('all_check_day').strip(',').split(','))
                                    if not_time:
                                        job.minute.on('00')
                                        job.hour.on('00')
                                else:
                                    if not_time:
                                        request.notifications.add(_(u"Выберите хотя бы один параметр в повторяющемся обзвоне"), "error")
                                        context['formset'] = formset
                                        context['form'] = form
                                        return context
                            cron.write()
                            print cron.render()
                        else:
#                            try:
#                                ssh = createSSHClient(FREESWITCH['fs1']['SSH_HOST'], FREESWITCH['fs1']['SSH_PORT'], FREESWITCH['fs1']['SSH_USER'], FREESWITCH['fs1']['SSH_PASSWORD'])
#                                command = """/usr/local/freeswitch/python/potok_for_obzvon.py %s normal > /dev/null &""" % (model.id)
#                                print command
#                                stdin, stdout, stderr = ssh.exec_command(command)
#                            except Exception, e:
#                                print e

                            print SCRIPT_ROOT
                            #os.system("""%s/potok_for_obzvon.py %s normal >> /dev/null &""" % (SCRIPT_ROOT, model.id))
                            subprocess.Popen("""/home/sites/gh/venv/bin/python %s/potok_for_obzvon.py %s normal >> /dev/null &""" % (SCRIPT_ROOT, model.id), shell=True, stdout=subprocess.PIPE)
                    request.notifications.add(_(u"Обзвон запущен. Вы можете посмотреть процесс его выполнения во таблице 'Текущие обзвоны'"), "success")
                    return HttpResponseRedirect("/account/obzvon/")  # перейти на страницу со списком правил
                else:
                    context['formset'] = formset
                    # context['formset_ivr'] = formset_ivr
                    context['form'] = form
                    return context
            else:
                request.notifications.add(_(u"Не правильно заполнены поля на номер"), "error")
                context['formset'] = formset
                # context['formset_ivr'] = formset_ivr
                context['form'] = form
                return context
    context['form'] = form
    context['formset'] = formset
    # context['formset_ivr'] = formset_ivr
    context['current_view_name'] = 'obzvon'
    return context

@login_required
@render_to('obzvon_list_preold_detach.html')
def obzvon_preold(request, id_obzvon):
    """
        Текущий обзвон детально
    """
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context["title"] = _(u"Просмотр обзвона: Детально")
    profile = request.user.get_profile()
    statistics = {}
    all_digits = []
    all = []
    model_obzvon = ObzvonModel.objects.get(billing_account_id=profile.billing_account_id, id=id_obzvon)
    try:
        model_number = ObzvonNumber.objects.filter(billing_account_id=profile.billing_account_id, id_obzvon=id_obzvon)
    except ObzvonNumber.DoesNotExist:
        raise Http404
    for model in model_number:
        all.append(str(model.id))
        all_digits.append(model.digits)
    if model_obzvon.status == 1:
        for one in all_digits:
            statistics[one] = all_digits.count(one)
        context["statistics"] = statistics

    if request.POST:
        if request.POST.get("submit_pause"): # если нажали Submit а не Cancel
            model_obzvon.status = 4
            model_obzvon.save()
            request.notifications.add(_(u"Обзвон поставлен на паузу"), "success")
        elif request.POST.get("submit_start"):
            try:
#                ssh = createSSHClient(FREESWITCH['fs1']['SSH_HOST'], FREESWITCH['fs1']['SSH_PORT'], FREESWITCH['fs1']['SSH_USER'], FREESWITCH['fs1']['SSH_PASSWORD'])
#                command = """/usr/local/freeswitch/python/potok_for_obzvon.py %s normal > /usr/local/freeswitch/python/log.log &""" % (id_obzvon)
#                print command
#                stdin, stdout, stderr = ssh.exec_command(command)
                #os.system("""%s/potok_for_obzvon.py %s normal""" % (SCRIPT_ROOT, model.id))
                subprocess.Popen("""/home/sites/gh/venv/bin/python %s/potok_for_obzvon.py %s normal >> /dev/null &""" % (SCRIPT_ROOT, model.id), shell=True, stdout=subprocess.PIPE)
            except Exception, e:
                print e
            return HttpResponseRedirect("/account/obzvon/")

#        context["file"] = str(model.id_obzvon.file).split("/")[-1]
#        context["all_number_id"] = "_".join(all)
#        context["model_number"] = model_number
#        context["interactive"] = model_obzvon.answer_dtmf
#        context["date_start"] = model_obzvon.date_start
#        context["status"] = model_obzvon.status
#        context["id_obzvon"] = id_obzvon
        return HttpResponseRedirect("/account/obzvon/preold/%s/" % (id_obzvon,))

    context["file"] = str(model.id_obzvon.file).split("/")[-1]
    context["all_number_id"] = "_".join(all)
    context["model_number"] = model_number
    context["interactive"] = model_obzvon.answer_dtmf
    context["date_start"] = model_obzvon.date_start
    context["status"] = model_obzvon.status
    context["id_obzvon"] = id_obzvon
    return context


@login_required
@render_to('obzvon_delete.html')
def obzvon_delete(request, id_obzvon):
    """
        Удаление
    """
    if request.user.get_profile().is_card:
        raise Http404

    context = {}
    context["title"] = _(u"Удаление обзвона")
    profile = request.user.get_profile()
    model = None

    try:
        model = ObzvonModel.objects.using(BILLING_DB).get(id=id_obzvon)
    except ObzvonModel.DoesNotExist:
        raise Http404

    if model.billing_account_id != profile.billing_account_id:
        raise Http404
    context["obzvon"] = model

    list_number = []
    model_number = ObzvonNumber.objects.filter(billing_account_id=profile.billing_account_id, id_obzvon=model.id)
    for numb in model_number:
        list_number.append(numb.number)
    context["obzvon_n"] = ','.join(list_number)

    if request.POST:
        if request.POST.get("submit"): # если нажали Submit а не Cancel
            model.delete()
            request.notifications.add(_(u"Обзвон успешно удален"), "success")
        return HttpResponseRedirect("/account/obzvon/")
    context['current_view_name'] = 'obzvon'
    return context


def obzvon_preold_ajax(request):
    """
        AJAX FOR STAtus obzvon
    """
    profile = request.user.get_profile()
    try:
        val = request.GET['val']
    except Exception, e:
        raise Http404
    all_id = val.split("_")
    print "AJAX FOR STAtus obzvon"
    all_status = []
    try:
        for id_s in all_id:
            try:
                model_number = ObzvonNumber.objects.get(billing_account_id=profile.billing_account_id, id=id_s)
            except ObzvonNumber.DoesNotExist:
                raise Http404
            percent = round(model_number.answer_time * 100 / model_number.duration)
            if percent > 100:
                percent = 100
            all_status.append({'status':model_number.status, 'id':model_number.id, 'answer':model_number.answer_time, 'percent':percent, 'digits':model_number.digits})
    except Exception, e:
        print e
    return HttpResponse(json.dumps(all_status))
