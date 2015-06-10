# -*- coding=utf-8 -*-
# Create your views here.
# from globalhome.settings import *

from django.conf import settings
import paramiko, scp
from call_forwarding.models import Rule
from django.core.mail import send_mail
from scp import SCPClient
from django.http import Http404
# from string import split
from models import create_myivr_temp, create_myivr, fax_numbers
from lib.decorators import render_to, login_required
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from lib.mail import send_email
from telnumbers.models import TelNumber
from externalnumbers.models import ExternalNumber
from account.models import OrderScheme
from voice_mail import get_number_by_scheme_id

# FREESWITCH = {
#    'fs1': {
#        'SSH_HOST': '192.168.20.12',
#        'SSH_USER': 'freeswitch',
#        'SSH_PORT': 22,
#        'SSH_PASSWORD': 'ahbcdbx!@',
#        'ESL_HOST': '192.168.20.12',
#        'ESL_PORT': '8021',
#        'ESL_PASSWORD': 'ClueCon'
#    },
#
# }

def scp_file(file_in, bill_acc):
    ##### Скрипт копирующий файл!!!!
    # from socket import timeout as SocketTimeout
    def createSSHClient(server, port, user, password):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server, port, user, password)
        return client

    # for x in FREESWITCH:
    print "'%s %s %s %s'" % (settings.FREESWITCH['fs1']['SSH_HOST'], settings.FREESWITCH['fs1']['SSH_PORT'], settings.FREESWITCH['fs1']['SSH_USER'], settings.FREESWITCH['fs1']['SSH_PASSWORD'])
    ssh = createSSHClient(settings.FREESWITCH['fs1']['SSH_HOST'], settings.FREESWITCH['fs1']['SSH_PORT'], settings.FREESWITCH['fs1']['SSH_USER'], settings.FREESWITCH['fs1']['SSH_PASSWORD'])
    scp = SCPClient(ssh.get_transport())
    str3 = file_in + '.wav'
    scp.put(str3, "/usr/local/sounds/all_files/myivr/%s" % (str(bill_acc)))
    ##### Конец скрипта

def convert_file(request, filename, bill_acc):
    import os
    print "CONVERT FILE %s!!!" % filename
    file_in = settings.OBZVON_URL
    file_in = file_in.replace('\\', '/')
    file_in = file_in + '/' + str(filename)
    print "file_in:%s" % file_in
    os.system("""sox '%s' -r 16000 -b 16 -c 1 '%s.wav'""" % (file_in, file_in))
    return file_in

def handle_uploaded_image(f):
    destination = open('files/sounds/all_files/myivr/%s' % f, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

def get_count(request):
    if request.POST.get("count_pod") != "":
        count_pod = int(request.POST.get("count_pod")) + 1
    else:
        count_pod = 0
    if request.POST.get("count_or") != "":
        count_or = int(request.POST.get("count_or")) + 1
    else:
        count_or = 1
    if request.POST.get("count_last") != "":
        count_last = int(request.POST.get("count_last"))
    else:
        count_last = 1

    print "Count_or:%s" % count_or
    print "Count_pod:%s" % count_pod
    print "Count_last:%s" % count_last
    return count_pod, count_or, count_last

def check_nabor(request, count_or):
    for i in range(1, count_or + 1):
        if (request.POST.get('name_nabor' + str(i)) != None):
            if (request.POST.get(u'name_nabor' + str(i)) == ""):
                return False
        else:
            pass
    return True

def get_last_call(request, count_last):
    stroka_last = ""
    for k in range(1, count_last + 1):
        try:
            stroka_last = stroka_last + request.POST.get("last_call" + str(k)).split(" ")[0]
            if (request.POST.get("last_call" + str(k)) != ""):
                stroka_last = stroka_last + ','
        except:
            pass
    print "stroka_last:%s" % stroka_last
    return stroka_last.strip(',')

def rec_model(request, count_or, count_pod, model_temp_id, profile):
    stroka = ""
    print "Count_or:%s" % count_or
    for i in range(0, count_or + 1):
        try:
            model_ivr = create_myivr()
            model_ivr.billing_account_id = profile.billing_account_id
            model_ivr.nabor = request.POST.get("name_nabor" + str(i))
            stroka = request.POST.get("name_call" + str(i)).split(" ")[0]
            stroka = stroka + ','
            for j in range(1, count_pod):
                try:
                    stroka = stroka + request.POST.get("name_call" + str(i) + "_" + str(j)).split(" ")[0]
                    if (request.POST.get("name_call" + str(i) + "_" + str(j)) != ""):
                        stroka = stroka + ','
                except:
                    pass
            print "END %s" % stroka
            model_ivr.call = stroka.strip(',')
            model_ivr.id_ivr_id = model_temp_id
            model_ivr.save()  # Сохранить ее в базе
            stroka = ""
        except Exception, e:
            print e


@login_required
@render_to('ivr_list.html')
def list_ivr(request):
    """
        Отображает список ivr
    """
    if request.user.get_profile().is_card:
        raise Http404

    context = {}
    context["title"] = _(u"List ivr")
    profile = request.user.get_profile()

    if profile:
        if profile.has_billing_account:
            if profile.billing_account.phones:
                context["have_numbers"] = True
            else:
                context["have_numbers"] = False

            if len(profile.billing_account.phones) == 1:
                context["have_one_numbers"] = True
            else:
                context["have_one_numbers"] = False

            ivrs = create_myivr_temp.objects.filter(billing_account_id_temp=profile.billing_account_id)
            print 'asdasd'
            for ivr in ivrs:
                order = OrderScheme.objects.filter(type='voice_menu', id_element=ivr.id)
                if order:
                    ivr.external_number, ivr.external_number_id = get_number_by_scheme_id(order[0].id_scheme_id)
            print 'asdasd11'
            if request.POST:
                # пришли данные, надо включить/выключить некоторые ivr
                if request.POST.get("submit"):
                    for ivr in ivrs:
                        if request.POST.get(str(ivr.id)) == "on":
                            try:
                                forward = Rule.objects.get(from_number = ivr.number.all()[0], enabled = True)
                            except:
                                forward = None
                            if forward != None:
                                request.notifications.add(_(u"On this issue of the diversion"), "warning")
                                return HttpResponseRedirect("/account/myivr/")

                            try:
                                getfax = fax_numbers.objects.get(number = ivr.number.all()[0], enabled = True)
                            except:
                                getfax = None
                            if getfax != None:
                                request.notifications.add(_(u"On this issue of the fax function"), "warning")
                                return HttpResponseRedirect("/account/myivr/")

                            if ivr.number.all():
                                temp_ivr = create_myivr_temp.objects.filter(billing_account_id_temp=profile.billing_account_id, number__tel_number=ivr.number.all()[0], enabled=True).exclude(id=ivr.id)
                                if temp_ivr:
                                    request.notifications.add(_(u"Ivr on this number already exists"), "warning")
                                    return HttpResponseRedirect("/account/myivr/")
                            ivr.enabled = True
                        else:
                            ivr.enabled = False
                        ivr.save()
                else:
                    return HttpResponseRedirect("/account/myivr/")

            context["ivrs"] = ivrs
    context['current_view_name'] = 'list_ivr'
    return context

@login_required
@render_to('ivr_delete.html')
def ivr_delete(request, ivr_id):  # OK!
    """
        Удаляем ivr
    """
    if request.user.get_profile().is_card:
        raise Http404

    context = {}
    context["title"] = _(u"Deleting ivr")
    profile = request.user.get_profile()
    model = None

    try:
        model = create_myivr_temp.objects.using(settings.BILLING_DB).get(id=ivr_id)
    except:
        return HttpResponseNotFound()

    if model:
        if model.billing_account_id_temp != profile.billing_account_id:
            return HttpResponseNotFound()
    else:
        return HttpResponseNotFound()

    context["ivr"] = model
    if request.POST:
        if request.POST.get("submit"):  # если нажали Submit а не Cancel
            model.delete()
            request.notifications.add(_(u"Ivr was succesfuly deleted."), "success")
        return HttpResponseRedirect("/account/myivr/")
    context['current_view_name'] = 'list_ivr'
    return context

@login_required
@render_to('ivr_edit.html')
def ivr_edit(request, ivr_id):  # OK!
    """
        Редактируем ivr
    """
    if request.user.get_profile().is_card:
        raise Http404

    context = {}
    context["title"] = _(u"Editing ivr")
    context["ivr_id"] = ivr_id

    model = None
    modelka = None
    try:
        model = create_myivr_temp.objects.using(settings.BILLING_DB).get(id=ivr_id)
        modelka = create_myivr.objects.using(settings.BILLING_DB).filter(id_ivr=ivr_id)
    except Exception, e:
        raise Http404
    profile = request.user.get_profile()  # получаем профиль текущего пользователя
    calli = []
    html = ""
    last_html = ""
    if model:
        if model.billing_account_id_temp != profile.billing_account_id:
            raise Http404
    else:
        raise Http404

    context["model"] = model
    if model.number.all():
        context["number_ivr"] = model.number.all()[0].tel_number
    numbers = profile.billing_account.phones
    context["choices"] = []
    context["choicesint"] = []
    my = []
    for number in numbers:
        tns = number.tel_number
        if number.person_name:
            tns += " (" + number.person_name + ")"
        context["choices"].append(tns)
        my.append(tns)

    for number in numbers:
        tns = number.tel_number
        context["choicesint"].append(tns)

    strm = ""
    last_strm = ""
    last_calli = model.last_call.split(",")
    i = 1
    for last in last_calli:
        last_html = last_html + """<li>"""
        for m in my:
            if m.split(" ")[0] == last:
                last_strm = last_strm + """<option  value="%s" selected>%s</option>""" % (m, m)
            else:
                last_strm = last_strm + """<option  value="%s">%s</option>""" % (m, m)

        last_html = last_html + """<select name="last_call%s" style="width:200px">%s</select>""" % (i, last_strm)
        last_html = last_html + """<img id="part_row" class="img" src=\"/media/images/sprite_delete.png\" title=\"%s\">""" % u'Удалить поле'
        last_html = last_html + """</li>"""
        last_strm = ""
        i = i + 1;
    context["len_last"] = len(last_calli)

    i = 1
    context["len_pod_or"] = 0
    context["len_or_or"] = len(modelka)


    for cal in modelka:
        html = html + """<div>"""
        if i != 1:
            html = html + """<br>"""
        html = html + """<li class="iform-item">"""
        if i == 1:
            html = html + """<label>"""
            html = html + """<span class="label">"""
            html = html + """%s""" % u'Набор'
            html = html + """<span class="tooltip">"""
            html = html + """<i></i>"""
            html = html + """<span class="tooltip-i">%s</span>""" % u'Укажите цифру быстрого набора номера для переключение на сотрудника. Например: "0"'
            html = html + """</span>"""
            html = html + """</span>"""
        html = html + """<input type="text" name="orname_nabor%s" required value="%s" />""" % (i, cal.nabor)
        if i == 1:
            html = html + """</label>"""
        html = html + """</li>"""
        calli = cal.call.split(",")
        for m in my:
            if m.split(" ")[0] == calli[0]:
                strm = strm + """<option  value="%s" selected>%s</option>""" % (m, m)
            else:
                strm = strm + """<option  value="%s">%s</option>""" % (m, m)

        html = html + """<li class="iform-item">"""
        if i == 1:
            html = html + """<span class="label">"""
            html = html + """%s""" % u'Номер'
            html = html + """<span class="tooltip">"""
            html = html + """<i></i>"""
            html = html + """<span class="tooltip-i">%s</span>""" % u'Укажите внутренний номер сотрудника, на который будет переключен вызов при нажатии указанного набора'
            html = html + """</span>"""
            html = html + """</span>"""
        html = html + """<select name="orname_call%s" style="width:200px">%s</select>""" % (i, strm)
        strm = ""
        if i != 1:
            html = html + """<img id="hole_row" class="img" src=\"/media/images/sprite_delete.png\" title=\"%s\">""" % u'Удалить поле'
        html = html + """<ul class="fl" id="orpod%s">""" % i

        if context["len_pod_or"] < len(calli):
            context["len_pod_or"] = len(calli)

        for k in range(1, len(calli)):
            html = html + """<li>"""
            for m in my:
                if calli[k] == m.split(" ")[0]:
                    strm = strm + """<option  value="%s" selected>%s</option>""" % (m, m)
                else:
                    strm = strm + """<option  value="%s">%s</option>""" % (m, m)
            html = html + """<select name="orname_call%s_%s" style="width:200px">%s</select>""" % (i, k, strm)
            html = html + """<img id="part_row" class="img" src=\"/media/images/sprite_delete.png\" title=\"%s\">""" % u'Удалить поле'
            html = html + """</li>"""
            strm = ""
        html = html + """</ul>"""
        html = html + """<a href="javascript:void(0);" onClick="tyt_orig('%s');" class="link-add">+</a>""" % (i,)
        html = html + """</li>"""
        html = html + """</div>"""
        i = i + 1;
    context["last_html"] = last_html
    context["html"] = html
    context["dtmf_wait"] = model.dtmf_ivr_wait_time/1000
    if model.billing_account_id_temp != profile.billing_account_id:
        return HttpResponseNotFound()
    if request.POST:
        if request.POST.get("submit"):  # если нажали Submit а не Cancel

            model_ivr = create_myivr()
            model_temp = create_myivr_temp()

            count_pod, count_or, count_last = get_count(request)

            bool = check_nabor(request, count_or)
            if bool == False:
                request.notifications.add(_(u'Complete all fields!!!'), 'error')
                return HttpResponseRedirect("/account/myivr/edit_ivr/%s/" % ivr_id)

            #model_temp.number_ivr = request.POST.get("ivr_number").split(" ")[0]
            model_temp.billing_account_id_temp = profile.billing_account_id
            model_temp.dtmf_ivr_wait_time = int(request.POST.get("dtmf_wait"))*1000
            model_temp.last_call = get_last_call(request, count_last)

            true_file = 0
            try:
                model_temp.file_wav = request.FILES['file_wav']
                print "request2"
                print str(request.FILES['file_wav'])
                print "model_temp.file_wav %s" % str(model_temp.file_wav)
                file_check = str(model_temp.file_wav)
                if file_check.split('.')[-1] != "wav":
                    request.notifications.add(_(u'Wrong format media file'), 'error')
                    return HttpResponseRedirect("/account/myivr/edit_ivr/%s/" % ivr_id)
                true_file = 1
            except:
                model_temp.file_wav = model.file_wav

            model_temp.enabled = model.enabled
            model.delete()

            int_numbers = ""
            if request.POST.get("int_enabled") != None:
                model_temp.int_enabled = True
                int_numbers = request.POST.get("int_numb")
                print "NUMBERs:%s" % int_numbers
                model_temp.int_numbers = int_numbers.strip(",")
            else:
                model_temp.int_enabled = False

            model_temp.save()
            if true_file == 1:
                try:
                    # handle_uploaded_image(request.FILES['file_wav'])
                    file_in = convert_file(request, model_temp.file_wav, profile.billing_account_id)  # конвертация
                    # копирование на freeswitch
                    # scp_file(file_in);
                except Exception, e:
                    send_email('Subject', 'Ivr do not save because: %s' % e, settings.DEFAULT_FROM_EMAIL, settings.ADMIN_MAILS, request.user.id)
                    request.notifications.add(_(u'Что-то пошло не так обратитесь к администрации!!!'), 'error')
                    return HttpResponseRedirect("/account/myivr/")

            if request.POST.get("ivr_number") != u'Выберите номер':
                model_temp.number.add(TelNumber.objects.get(tel_number=request.POST.get("ivr_number").split(" ")[0]).id)

            rec_model(request, count_or, count_pod, model_temp.id, profile)

            count_pod_or = int(request.POST.get("count_pod_or")) + 1
            count_or_or = int(request.POST.get("count_or_or")) + 1
            for i in range(1, count_or_or):
                try:
                    model_ivr = create_myivr()
                    model_ivr.billing_account_id = profile.billing_account_id
                    model_ivr.nabor = request.POST.get("orname_nabor" + str(i))
                    stroka = request.POST.get("orname_call" + str(i)).split(" ")[0]
                    stroka = stroka + ','
                    for j in range(1, count_pod_or):
                        try:
                            print stroka
                            stroka = stroka + request.POST.get("orname_call" + str(i) + "_" + str(j)).split(" ")[0]
                            if (request.POST.get("orname_call" + str(i) + "_" + str(j)) != ""):
                                stroka = stroka + ','
                        except:
                            pass
                    print "END %s" % stroka
                    model_ivr.call = stroka.strip(',')
                    model_ivr.id_ivr_id = model_temp.id
                    model_ivr.save()  # Сохранить ее в базе
                    stroka = ""
                except Exception, e:
                    print e


            request.notifications.add(_(u'Ivr successfully changed'), 'success')
            return HttpResponseRedirect("/account/myivr/")  # перейти на страницу со списком ивр
        else:
            return HttpResponseRedirect("/account/myivr/")
    context['current_view_name'] = 'list_ivr'
    return context

@login_required
@render_to('ivr.html')
def create_ivr(request):
    context = {}
    context["title"] = _(u"Connecting ivr")
    profile = request.user.get_profile()
    model_temp = create_myivr_temp()
    numbers = profile.billing_account.phones
    context["choices"] = []
    try:
        context["obzvon"] = request.GET["obzvon"]
    except:
        context["obzvon"] = ''
    for number in numbers:
        tns = number.tel_number
        if number.person_name:
            tns += " (" + number.person_name + ")"
        context["choices"].append((tns))
    if request.POST:
        # Пришли данные в POST-запросе.
        if request.POST.get("submit"):
            count_pod, count_or, count_last = get_count(request)

            if not context["obzvon"]:
                if request.POST.get("ivr_number") != u'Выберите номер':
                    try:
                        temp_ivr = create_myivr_temp.objects.get(billing_account_id_temp=profile.billing_account_id, enabled=True, number__tel_number=request.POST.get("ivr_number").split(" ")[0])
                    except create_myivr_temp.DoesNotExist:
                        temp_ivr = None
                    if temp_ivr != None:
                        request.notifications.add(_(u"Ivr on this number already exists"), "warning")
                        return HttpResponseRedirect("/account/myivr/create_ivr/")

                    try:
                        forward = Rule.objects.get(from_number=request.POST.get("ivr_number").split(" ")[0], enabled=True)
                    except:
                        forward = None
                    if forward != None:
                        request.notifications.add(_(u"On this issue of the diversion"), "warning")
                        return HttpResponseRedirect("/account/myivr/create_ivr/")

                    try:
                        getfax = fax_numbers.objects.get(number=request.POST.get("ivr_number").split(" ")[0], enabled=True)
                    except:
                        getfax = None
                    if getfax != None:
                        request.notifications.add(_(u"On this issue of the fax function"), "warning")
                        return HttpResponseRedirect("/account/myivr/create_ivr/")

            bool = check_nabor(request, count_or)
            if bool == False:
                request.notifications.add(_(u'Complete all fields!!!'), 'error')
                return HttpResponseRedirect("/account/myivr/create_ivr/")

            model_temp.billing_account_id_temp = profile.billing_account_id
            # model_temp.last_call = request.POST.get("last_call")
            try:
                model_temp.file_wav = request.FILES['file_wav']
                print "request"
                print str(request.FILES['file_wav'])
            except:
                request.notifications.add(_(u'Выберите медиа файл!'), 'error')
                return HttpResponseRedirect("/account/myivr/create_ivr/")

            print model_temp.file_wav
            file_check = str(model_temp.file_wav)
            try:
                if file_check.split('.')[-1] != "wav":
                    raise Exception
            except:
                request.notifications.add(_(u'Wrong format media file'), 'error')
                return HttpResponseRedirect("/account/myivr/create_ivr/")

            model_temp.dtmf_ivr_wait_time = int(request.POST.get("dtmf_wait"))*1000
            model_temp.last_call = get_last_call(request, count_last)

            int_numbers = ""
            if request.POST.get("int_enabled") != None:
                int_numbers = request.POST.get("int_numb")
                print "NUMBERs:%s" % int_numbers
                if int_numbers != "":
                    model_temp.int_enabled = True
                    model_temp.int_numbers = int_numbers.strip(",")
                else:
                    model_temp.int_enabled = False
                    model_temp.int_numbers = ""
            else:
                model_temp.int_enabled = False

            model_temp.save()


            try:
                # handle_uploaded_image(request.FILES['file_wav'])
                print "model_temp.file_wav"
                print model_temp.file_wav
                file_in = convert_file(request, model_temp.file_wav, profile.billing_account_id)  # конвертация
                # копирование на freeswitch
                # scp_file(file_in);
            except Exception, e:
                print e
#                send_email('Subject', 'Ivr do not save because: %s' % e, DEFAULT_FROM_EMAIL, ADMIN_MAILS, request.user.id)
                request.notifications.add(_(u'Что-то пошло не так, обратитесь к администрации!!!'), 'error')
                return HttpResponseRedirect("/account/myivr/")


            if not context["obzvon"]:
                if request.POST.get("ivr_number") != u'Выберите номер':
                    model_temp.number.add(TelNumber.objects.get(tel_number=request.POST.get("ivr_number").split(" ")[0]).id)

            rec_model(request, count_or, count_pod, model_temp.id, profile)

            request.notifications.add(_(u'Ivr successfully added ;)'), 'success')
            return HttpResponseRedirect("/account/myivr/")  # перейти на страницу со списком ивр
    context['current_view_name'] = 'list_ivr'
    return context

def ajax_check_ivr(request):
    print "ajax_check_ivr"
    try:
        if request.GET['number_fax'] == u'Выберите номер':
            return HttpResponse("nonumber")
    except Exception, e:
        return HttpResponse("nonumber")

    number_fax = request.GET['number_fax'][:7]

    try:
        ivr = create_myivr_temp.objects.get(number__tel_number=number_fax, enabled=True)
    except Exception, e:
        ivr = None
    if ivr != None:
        return HttpResponse("ivr_gra4")

    try:
        forward = Rule.objects.get(from_number=number_fax, enabled=True)
    except:
        forward = None
    if forward != None:
        return HttpResponse("gra4")

    try:
        getfax = fax_numbers.objects.get(number=number_fax, enabled=True)
    except:
        getfax = None
    if getfax != None:
        return HttpResponse("getfax_gra4")

    return HttpResponse("ok")
