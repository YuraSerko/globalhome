# -*- coding=utf-8 -*-

# Create your views here.
from settings import *
from settings import BILLING_DB, MEDIA_ROOT, FREESWITCH, VOICE_ROOT
from django.http import Http404
from string import split
from models import Voice_mail
from account.forms import Voicemail
# from call_forwarding.models import Rule
from lib.decorators import render_to, login_required, render_to_response
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
# from django.forms.models import instance
import paramiko, scp
from scp import SCPClient
from lib.transliterate import transliterate
from account.models import OrderScheme, AllSchemeDraft
from externalnumbers.models import ExternalNumber

def copy_file(file_in):
    ##### Скрипт копирующий файл!!!!
    def createSSHClient(server, port, user, password):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server, port, user, password)
        return client

    print "'%s %s %s %s'" % (FREESWITCH['fs1']['SSH_HOST'], FREESWITCH['fs1']['SSH_PORT'], FREESWITCH['fs1']['SSH_USER'], FREESWITCH['fs1']['SSH_PASSWORD'])
    ssh = createSSHClient(FREESWITCH['fs1']['SSH_HOST'], FREESWITCH['fs1']['SSH_PORT'], FREESWITCH['fs1']['SSH_USER'], FREESWITCH['fs1']['SSH_PASSWORD'])
    scp = SCPClient(ssh.get_transport())
    scp.put(file_in + '.wav', "/usr/local/sounds/all_files/voicemail")
    ##### Конец скрипта

def save_file(file_url, filename, file):
    destination = open(file_url % filename, 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()

def get_number_by_scheme_id(scheme_id):
    print "get_number_by_scheme_id"
    try:
        order = OrderScheme.objects.get(id_next_scheme_id=scheme_id)
        sch_id = order.id_scheme_id
        src_num_by_scheme_id, num_id = get_number_by_scheme_id(sch_id)
    except OrderScheme.DoesNotExist, e:
        try:
            number = ExternalNumber.objects.get(id_scheme_id = scheme_id)
        except ExternalNumber.DoesNotExist, e:
            print e
            try:
                num = AllSchemeDraft.objects.get(id_scheme_id = scheme_id)
            except AllSchemeDraft.DoesNotExist, e:
                print e
                raise Http404
            try:
                number = ExternalNumber.objects.get(id = num.id_external_number)
            except ExternalNumber.DoesNotExist, e:
                print 'ttt %s' % e
                raise Http404
        src_num_by_scheme_id = number.number
        num_id = number.id
        return src_num_by_scheme_id, num_id
    return src_num_by_scheme_id, num_id

@login_required
@render_to('list_vm.html')
def list_vm(request):
    context = {}
    context["title"] = _(u"Голосовая почта")
    profile = request.user.get_profile()
    if profile:
        if profile.has_billing_account:
            if profile.billing_account.phones:
                context["have_numbers"] = True
            else:
                context["have_numbers"] = False
            print profile.billing_account_id
            vms = Voice_mail.objects.filter(billing_account_id=profile.billing_account_id)
            for vm in vms:
                order = OrderScheme.objects.filter(type='voice_mail', id_element=vm.id)
                if order:
                    vm.external_number, vm.external_number_id = get_number_by_scheme_id(order[0].id_scheme_id)
            if request.POST:
                if request.POST.get("submit"):
                    for vm in vms:
                        if request.POST.get(str(vm.id)) == "on":
                            vm.enabled = True
                        else:
                            vm.enabled = False
                        vm.save()
                else:
                    return HttpResponseRedirect("/account/voice_mail/list_vm/")
            context["vms"] = vms
    context['current_view_name'] = 'list_vm'
    return context

@login_required
@render_to('create_vm.html')
def create_vm(request, vm_id=0):
    """
        Создание и редактирование
    """
    if request.user.get_profile().is_card:
        raise Http404

    context = {}
    if vm_id > 0:
        context["title"] = u'Редактирование голосовой почты'
    else:
        context["title"] = u'Добавление голосовой почты'
    context['current_view_name'] = 'list_vm'
    profile = request.user.get_profile()
    context["red_vm"] = []
    if vm_id:
        context["red_vm"] = Voice_mail.objects.get(id=vm_id)
    numbers = profile.billing_account.phones
    context["choices"] = []
    model = Voice_mail()
    try:
        model = Voice_mail.objects.get(id=vm_id)
    except:
        pass
    for number in numbers:
        tns = number.tel_number
        if number.person_name:
            tns += " (" + number.person_name + ")"
        context["choices"].append((tns))
    if not request.POST:
        if vm_id:
            form = Voicemail(model = model, profile = profile, request = request)
            if not model.file_hello.split("/")[-1] == "all_voicemail.wav":
                context['file'] = model.file_hello.split("/")[-1]
            #form = Voicemail(instance=Voice_mail.objects.get(id=vm_id))
        else:
            context['file'] = None
            form = Voicemail()
        context['form'] = form
        return context
    else:
        if request.POST:
            # Пришли данные в POST-запросе.
            if request.POST.get("save"):
                if vm_id:
                    voice_too = Voice_mail.objects.filter(number=request.POST.get("number")[:7], enabled=True).exclude(id=vm_id)
                else:
                    voice_too = Voice_mail.objects.filter(number=request.POST.get("number")[:7], enabled=True)
                if voice_too:
                    request.notifications.add(_(u'На данном номере уже существует голосовая почта'), 'error')
                    context["red_vm"] = request.POST
                    context['form'] = Voicemail(model = model, data = request.POST, profile = profile, request = request)
                    return context
                form = Voicemail(model = model, data = request.POST, profile = profile, request = request)
                if not form.is_valid():
                    context["red_vm"] = request.POST
                    context['form'] = form
                    return context
                if vm_id > 0:
                    url = "/account/voice_mail/edit_vm/%s/" % vm_id
                    msg = u'Голосовая почта успешно отредактирована'
                    #model = Voice_mail.objects.using(BILLING_DB).get(id=vm_id)
                else:
                    url = "/account/voice_mail/create_vm/"
                    msg = u'Голосовая почта успешно добавлена'
                    #model = Voice_mail()
                    model.enabled = True
                try:
                    if request.FILES['file_hello']:
                        filename = transliterate(str(request.FILES['file_hello']))
                        if filename.split('.')[-1] != "wav":
                            request.notifications.add(_(u'Wrong format media file'), 'error')
                            return HttpResponseRedirect(url)
                        model.file_hello = VOICE_ROOT % filename
                        try:
                            save_file(VOICE_ROOT, filename, request.FILES['file_hello'])
                            os.system("""sox %s -r 8000 -b 16 -c 1 %s.wav""" % (VOICE_ROOT % filename, VOICE_ROOT % filename))  # конвертация
                            copy_file(VOICE_ROOT % filename);
                        except Exception, e:
                            print "Error in voicemail:%s" % e
                            # send_mail('Subject', 'Ivr do not save because: %s' % e, DEFAULT_FROM_EMAIL, ADMIN_MAILS)
                            request.notifications.add(_(u'Что-то пошло не так обратитесь к администрации!!!'), 'error')
                            return HttpResponseRedirect("/account/voice_mail/list_vm")
                except Exception, e:
                    print "Error2 in voicemail:%s" % e
                    pass
                model.number = request.POST.get("number")[:7]
                model.email = form.cleaned_data.get("email")
                model.reason = form.cleaned_data.get("flags")
                model.billing_account_id = profile.billing_account_id
                if form.cleaned_data.get("wait_time"):
                    model.wait_time = int(form.cleaned_data.get("wait_time"))*1000
                model.save()
                request.notifications.add(_(msg), 'success')
                return HttpResponseRedirect("/account/voice_mail/list_vm/")
    return context


@login_required
@render_to('delete_vm.html')
def delete_vm(request, vm_id):  # OK!
    """
        Удаляем vm
    """
    if request.user.get_profile().is_card:
        raise Http404

    context = {}
    context["title"] = _(u"Удаление")
    context['current_view_name'] = 'list_vm'
    profile = request.user.get_profile()
    model = None

    try:
        model = Voice_mail.objects.using(BILLING_DB).get(id=vm_id)
    except:
        pass

    context["vm"] = model
    if model:
        if model.billing_account_id != profile.billing_account_id:
            return HttpResponseNotFound()
    else:
        return HttpResponseNotFound()
    if request.POST:
        if request.POST.get("submit"):  # если нажали Submit а не Cancel
            if model:
                if model.billing_account_id != profile.billing_account_id:
                    return HttpResponseNotFound()
                model.delete()
                request.notifications.add(_(u"Голосовая почта удалена"), "success")
        return HttpResponseRedirect("/account/voice_mail/list_vm/")
    return context
