# coding: utf-8
# $Id: views.py 253 2010-12-10 16:09:08Z site $

#############################
from lib.decorators import render_to, login_required
from django.utils.translation import ugettext_lazy as _, ugettext
from fs.models import Record_talk_activated_tariff, Voice_mail, TelNumbersList, create_myivr_temp, create_myivr, fax_numbers, GatewayModel, TelNumbersListDetailNumbers, TelNumbersListExtNumbers, TelNumbersListNumbers, TelNumbersListGroups, Queue, Agent
from fs.forms import GroupDynForm, NumberDynForm, ExtNumberDynForm, ListNumberForm, ListNumberDynForm, QueueForm
from call_forwarding.forms import RuleEditForm, RulesListForm
from call_forwarding.models import Rule
from django.shortcuts import render
from django.template import Template, RequestContext, loader, Context
from fs.gateway import recursive
from account.forms import Voicemail, CallTimeRangeForm, CallNumberForm
from account.models import CallTimeRange, CallNumber, AllSchemeDraft, AllScheme, OrderScheme
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
import json
from billing.models import BillserviceAccount
from django.db.models import Q
from telnumbers.models import TelNumber, TelNumbersGroup
from externalnumbers.models import ExternalNumber
from fs.list_number import ret_context, get_query, get_notifications, check_for_error_new, create_group_number_extnumber, save_model_list_number
from fs.my_ivr import rec_model, check_nabor, get_count, get_last_call
from fs.models import NumberTemplateRule, NumberTemplates
from fs.forms import NumberTemplate
from django.forms.formsets import formset_factory
from django.utils.functional import curry
from django.utils import simplejson
from django import shortcuts
from django.conf import settings
from django.core.urlresolvers import reverse
import datetime
from django.http import Http404

def vsepomestam(all):
    s_w = 0
    for x in all:
        if x.id_next_scheme_id:
            ddd = vsepomestam(OrderScheme.objects.filter(id_scheme_id = x.id_next_scheme_id))
            s_w += ddd
            x.level_width = ddd
        else:
            s_w += 1
            x.level_width = 1
        x.save()
    return s_w

def createDraft(request):
    context = {}
    profile = request.user.get_profile()
    if not profile or profile.is_card:
        raise Http404
    number_id = request.POST.get('number_id')
    try:
        number = ExternalNumber.objects.get(id = number_id, account = profile.billing_account_id)
    except ExternalNumber.DoesNotExist, e:
        raise Http404
    scheme_draft = AllSchemeDraft()
    new_scheme = AllScheme()
    new_scheme.save()
    try:
        scheme_draft.id_external_number = number.id
        scheme_draft.id_scheme = new_scheme
    except Exception, e:
        print e
    scheme_draft.info = 'Create Draft'
    scheme_draft.save()

#    try:
#        scheme_draft = AllSchemeDraft.objects.filter(id_scheme = number.id_scheme_id)
#    except AllSchemeDraft.DoesNotExist, e:
#        return context

    return HttpResponse('1')

def convert_file(request, filename, bill_acc):
    import os
    print "CONVERT FILE %s!!!" % filename
    file_in = settings.OBZVON_URL
    file_in = file_in.replace('\\', '/')
    file_in = file_in + '/' + str(filename)
    print "file_in:%s" % file_in
    os.system("""sox '%s' -r 16000 -b 16 -c 1 '%s.wav'""" % (file_in, file_in))
    return file_in

def getform(request):
    import datetime
    context = {}
    profile = request.user.get_profile()
    if not profile or profile.is_card:
        raise Http404

    element_id = request.POST.get('element_id')
    if element_id == 'tab1':
        try:
            return call_number(request)
        except Exception, e:
            print e
    elif element_id == 'tab2':
        try:
            return call_list(request, 0)
        except Exception, e:
            print e
    elif element_id == 'tab3':
        try:
            return waiting_list(request, 0)
        except Exception, e:
            print e
    elif element_id == 'tab4':
        try:
            return fax_create_getfax(request, 0)
        except Exception, e:
            print e
    elif element_id == 'tab5':
        try:
            funct = voicemail_create_vm(request, 0, request.POST.get('number_id'), request.POST.get('newelement'), request.POST.get('parent_newelement'))
            return funct
        except Exception, e:
            print e
    elif element_id == 'tab7':
        try:
            funct = create_ivr(request, 0, request.POST.get('number_id'), request.POST.get('newelement'), request.POST.get('parent_newelement'))
            return funct
        except Exception, e:
            print e
    elif element_id == 'tab8':
        try:
            return number_list(request, 0)
        except Exception, e:
            print e
    elif element_id == 'tab9':
        try:
            return time_range(request, 0, request.POST.get('number_id'), request.POST.get('newelement'), request.POST.get('parent_newelement'))
        except Exception, e:
            print e
    return HttpResponse(templ.render(context))


def checkvoicemail(request, voicemail_id):
    context = {}
    profile = request.user.get_profile()
    if not profile or profile.is_card:
        raise Http404

    if int(voicemail_id) > 0:
        try:
            model = Voice_mail.objects.get(billing_account_id=profile.billing_account_id, id=voicemail_id)
        except Voice_mail.DoesNotExist, e:
            raise Http404
    elif int(voicemail_id) == 0:
        model = Voice_mail()
    form = Voicemail(model = model, profile = profile, request = request)
    if not model.file_hello.split("/")[-1] == "all_voicemail.wav":
        context['file'] = model.file_hello.split("/")[-1]
    context['form'] = form
    try:
        templ = Template("""{% load i18n form_tags lib_tags %}

                                  <div class="form-section form-section2 form_voice_vm">
                                {% form_field form.name block %}
                            </div>
                            <hr>
                            <div class="form-section form-section2 form_django">
                                {% form_field form.flags block %}
                                <div id="busy_conditions">
                                      {% form_field form.wait_time block %}
                                </div>
                                <div class="hint"><i></i>Условие, при котором будет включен режим голосовой почты</div>
                            </div>
                            <hr>
                            <div class="form-section form-section2 form_voice_vm">
                               {% form_field form.email block %}
                               <div class="hint"><i></i>Email адрес, на который выслать оповещение о новом сообщении</div>
                            </div>
                            <hr>
                            <div class="form-section form-section2 form_django">
                                {% if file %}
                                <span class="label">Ваше текущее приветствие:  {{ file }}</span>
                                {% endif %}
                                <span class="label">Ваше приветствие</span>
                                <input id="file_hello" name="file_hello" type="file" accept="audio/wav"/>
                                <div class="hint"><i></i>Вы можете выбрать файл приветствия, который будет проигрываться перед записью сообщения</div>
                            </div>
        """)
        context = Context(context)
    except Exception, e:
        print e
    return HttpResponse(templ.render(context))

@login_required
@render_to('account/create_vm.html')
def voicemail_create_vm(request, vm_id, number_id=0, newelement=0, parent_newelement=0):
    """
        Создание и редактирование голосовой почты
    """
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context['newelement'] = newelement
    context['parent_newelement'] = parent_newelement
    context["number_id"] = number_id
    profile = request.user.get_profile()
    context["red_vm"] = []
#    vm_id = None
#    if request.POST.get("number"):
#        vm_id = request.POST.get("number")
    context["choices"] = {}
    model = Voice_mail()
    if vm_id and int(vm_id) > 0:
        model = Voice_mail.objects.get(pk = vm_id)
        context["red_vm"] = model
        if model.billing_account_id != profile.billing_account_id:
            raise Http404
    else:
        vm_id = None
#    try:
#        model = Voice_mail.objects.get(id=vm_id)
#        context["red_vm"] = model
#    except:
#        pass
    allv = Voice_mail.objects.filter(billing_account_id = profile.billing_account_id)
    for x in allv:
        context["choices"][x.id]=x.name
    if request.POST:
        # Пришли данные в POST-запросе.
        if request.POST.get("save"):
            form = Voicemail(model = model, data = request.POST, profile = profile, request = request)
            if not form.is_valid():
                context["red_vm"] = request.POST
                context['form'] = form
                return context
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
                        return context
            except Exception, e:
                print "Error2 in voicemail:%s" % e
                pass
            model.name = request.POST.get("name")
            model.email = form.cleaned_data.get("email")
            model.reason = form.cleaned_data.get("flags")
            model.billing_account_id = profile.billing_account_id
            if form.cleaned_data.get("wait_time"):
                model.wait_time = int(form.cleaned_data.get("wait_time"))*1000
            model.save()
            return HttpResponse('createnewelement_%s' % (model.id,))
        else:
            if vm_id:
                form = Voicemail(model = model, profile = profile, request = request)
                if not model.file_hello.split("/")[-1] == "all_voicemail.wav":
                    context['file'] = model.file_hello.split("/")[-1]
            else:
                context['file'] = None
                try:
                    form = Voicemail()
                except Exception, e:
                    print e
            context['form'] = form
            return context
    return context

def checkfax(request, fax_id):
    context = {}
    profile = request.user.get_profile()
    if not profile or profile.is_card:
        raise Http404

    if int(fax_id) > 0:
        try:
            model = fax_numbers.objects.get(billing_account_id=profile.billing_account_id, id=fax_id)
        except fax_numbers.DoesNotExist, e:
            raise Http404
    elif int(fax_id) == 0:
        model = fax_numbers()

    emaili = model.email.split(",")
    m = 1
    html = ""
    for em in emaili:
        if m == 1:
            html += """<li>"""
            html += """<input name="email_adress%s" type="text" onkeyup="lol(this, %s)" autocomplete="off" width="30" id="validate%s" value="%s"/>""" % (m, m, m, em, )
            html += """<span id="validEmail%s" class="validEmail"></span>""" % (m, )
            html += """</li>"""
        else:
            html += """<li>"""
            html += """<input name="email_adress%s" type="text" onkeyup="lol(this, %s)" autocomplete="off" width="30" id="validate%s" value="%s"/>""" % (m, m, m, em, )
            html += """<span id="validEmail%s" class="validEmail"></span>""" % (m, )
            html += u"""<img id="part_row" src=\"/media/images/sprite_delete.png\" style="margin-top: 3px;" title=\"Удалить поле\">"""
            html += """</li>"""
        m = m + 1
    context["len_email"] = len(emaili)
    context["html"] = html
    context["name"] = model.name
    try:
        templ = Template("""
              <div class="form-section form_getfax" id="emails">
              <span class="label">Название факса</span>
                   <input id="id_name" name="name" type="text" value="{{name}}">
                   </br></br>
                <span class="label">
                            Email адрес:
                        </span>
                        <ul id="email_list">
                            {% if html %}
                                {{ html|safe }}
                            {% else %}
                            <li><input name="email_adress1" onkeyup="lol(this, 1)" type="text" autocomplete="off" id="validate1" width="30" {% if email %} value="{{ email }}"{% endif %}><span id="validEmail1" class="validEmail"></span></li>
                            {% endif %}
                        </ul>
                        <a href="javascript:void(0);" class="link-add" id="addNewEmail">+</a>
                    <div class="hint"><i></i>Адрес электронной почты, на который будет отправлен факс.</div>

                </div>
        """)
        context = Context(context)
    except Exception, e:
        print e
    return HttpResponse(templ.render(context))

@login_required
@render_to('account/create_getfax.html')
def fax_create_getfax(request, getfax_id=0, number_id=0, newelement=0, parent_newelement=0, draft_flag=0):
    """
        Создание и редактирование
    """
    print "fax_create_getfax1"
    profile = request.user.get_profile()
    if profile.is_card:
        raise Http404
    context = {}
    context["title"] = _(u"Receive fax")
    context['newelement'] = newelement
    context['parent_newelement'] = parent_newelement
    context["number_id"] = number_id
    context["draft_flag"] = draft_flag
    #context["red_fax"] = []
    context["choices"] = {}
    faxs = fax_numbers.objects.filter(billing_account_id = profile.billing_account_id)
    for fax in faxs:
        context["choices"][fax.id]=fax.name
    try:
        if request.POST:
            # Пришли данные в POST-запросе.
            if request.POST.get("submit"):
                model = fax_numbers()
                if getfax_id and int(getfax_id) > 0:
                    model = fax_numbers.objects.get(pk = getfax_id)
                    if model.billing_account_id != profile.billing_account_id:
                        raise Http404
                model.name = request.POST.get("name")
                emailik = ""
                count = int(request.POST.get("count_email"))
                for i in range(1, count+1):
                    emailik = emailik + request.POST.get("email_adress" + str(i))
                    emailik = emailik + ','
                model.email = emailik.strip(',')
                model.billing_account_id = profile.billing_account_id
                model.save()
                print "sozdano dadada"
                print 'createnewelement_%s' % (model.id,)
                return HttpResponse('createnewelement_%s' % (model.id,))
            else:
                return context
    except Exception, e:
        print e
    context['current_view_name'] = 'list_getfax'
    return context


def get_context(**kwargs):
    context = {}
    for key in kwargs:
        context[key] = kwargs[key]
    return context


def check_waiting_list(request, list_id):
    try:
        context = {}
        bac = request.user.get_profile().billing_account
        try:
            queue = Queue.objects.get(pk = list_id)
            if queue.billing_account_id != bac.id:
                print 'queue_edit queue.billing_account_id != billing_account_id'
                raise Http404
        except Queue.DoesNotExist, e:
            raise Http404 # не нашли очередь с таким id => 404
        form = QueueForm(bac = bac, instance = queue)
        templ = loader.get_template("account/queue_ajax_form.html")
        context["form"] = form
        context = Context(context)
    except Exception, e:
        print e
    return HttpResponse(templ.render(context))

@login_required
@render_to('account/queue_form.html')
def waiting_list(request, queue_id=0, number_id=0, newelement=0, parent_newelement=0, draft_flag=False):
    context = {}
    bac = request.user.get_profile().billing_account
    list_queue = Queue.objects.filter(billing_account_id=bac.id)
    dict = {}
    for list_n in list_queue:
        dict[list_n.id] = list_n.name
    queue = None
    if queue_id and int(queue_id) > 0:
        queue = Queue.objects.get(pk = queue_id)
        if queue.billing_account_id != bac.id:
            print 'queue_edit queue.billing_account_id != billing_account_id'
            raise Http404

    if request.POST:
        if request.POST.get('submit'):
            form = QueueForm(request.POST, request.FILES, bac = bac, queue = queue)
            if form.is_valid():
                queue = form.save(request = request)
                return HttpResponse('createnewelement_%s' % (queue.id,))
        else:
            form = QueueForm(bac = bac)
            return get_context(form = form, choices=dict, draft_flag=draft_flag, newelement=newelement, parent_newelement=parent_newelement, number_id=number_id, title = u'Подключение очереди', button = u'Создать')
    else:
        form = QueueForm(bac = bac)
    return get_context(form = form, choices=dict, draft_flag=draft_flag, newelement=newelement, parent_newelement=parent_newelement, number_id=number_id, title = u'Подключение очереди', button = u'Создать')

@login_required
@render_to('account/time_range.html')
def time_range(request, time_id=0, number_id=0, newelement=0, parent_newelement=0):
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    print "timeid"
    print time_id
    context['newelement'] = newelement
    context['parent_newelement'] = parent_newelement
    context["number_id"] = number_id
    context["time_id"] = time_id
    profile = request.user.get_profile()
    model = CallTimeRange()
    if time_id and int(time_id) > 0:
        model = CallTimeRange.objects.get(pk = time_id)
        if model.billing_account_id != profile.billing_account_id:
            print 'CallTimeRange.billing_account_id != billing_account_id'
            raise Http404
    #model = CallTimeRange()
    if request.POST:
        # Пришли данные в POST-запросе.
        if request.POST.get("submit"):
            form = CallTimeRangeForm(model = model, data = request.POST, profile = profile, request = request)
            try:
                if form.is_valid():
                    model = form.ok_model
                    if model:
                        if profile:
                            if profile.has_billing_account:
                                model.billing_account_id = profile.billing_account_id
                                model.save()  # Сохранить ее в базе
                                print "sozdano"
                                print 'timerange_%s' % (model.id,)
                                if time_id and int(time_id) > 0:
                                    return HttpResponse('editnewelement_%s' % (model.id,))
                                return HttpResponse('createnewelement_%s' % (model.id,))
                else:
                    print "Form not valid !"
                    context['form'] = form
                    return context
            except Exception, e:
                print e
            print 'asd'
        else:
            try:
                form = CallTimeRangeForm(model = model, profile = profile, request = request)
            except Exception, e:
                print e
    context['form'] = form
    return context


@login_required
@render_to('account/call_list_bw.html')
def number_list(request, list_id, edit_list_id=0, number_id=0, newelement=0, parent_newelement=0):
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context['newelement'] = newelement
    context['parent_newelement'] = parent_newelement
    context["number_id"] = number_id
    context["edit_list_id"] = edit_list_id
    profile = request.user.get_profile()
    xString = ''
    int_numb = ''
    list_number = TelNumbersList.objects.filter(call_list = False, billing_account_id=profile.billing_account_id)
    context["choices"] = {}
    dict = {}
    for list_n in list_number:
        dict[list_n.id] = list_n.name
    model = TelNumbersList()
    if list_id and int(list_id) > 0:
        model = TelNumbersList.objects.get(pk = list_id)
        if model.billing_account_id != profile.billing_account_id:
            print 'queue_edit queue.billing_account_id != billing_account_id'
            raise Http404
        model_num = TelNumbersListDetailNumbers.objects.filter(telnumberslist_id=list_id)
        model_num.delete()
    context["choices"] = dict
    if request.POST:
        if request.POST.get("submit"):
            int_numb = request.POST.get("int_numb")
            if int_numb == '':
                context['error'] = True
                request.notifications.add(_(u"Ошибка. Добавьте хотя бы один номер"), "error")
                return ret_context_call_list(context, int_numb)

            model.name = request.POST.get("name")
            model.billing_account_id = profile.billing_account_id
            model.call_list = False
            model.save()
            for numb in int_numb.strip(",").split(","):
                if numb != '':
                    save_model_list_number(model.id, numb, profile)
            print 'number_list_%s' % (model.id,)
            if edit_list_id and int(edit_list_id) > 0:
                return HttpResponse('editnewelement_%s' % (model.id,))
            return HttpResponse('createnewelement_%s' % (model.id,))
    return ret_context_call_list(context, int_numb)


@login_required
@render_to('account/create_number_list.html')
def number_list1(request, list_id, number_id=0, newelement=0, parent_newelement=0):
    """
        Новый список
    """
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context['newelement'] = newelement
    context['parent_newelement'] = parent_newelement
    context["number_id"] = number_id
    profile = request.user.get_profile()
    model = TelNumbersList()
    xString = ''
    if profile.billing_account.phones:
        context["have_numbers"] = True
    else:
        context["have_numbers"] = False
    list_number = TelNumbersList.objects.filter(call_list = False, billing_account_id=profile.billing_account_id)
    context["choices"] = {}
    dict = {}
    for list_n in list_number:
        dict[list_n.id] = list_n.name
    context["choices"] = dict

    model = TelNumbersList()
    if list_id and int(list_id) > 0:
        model = TelNumbersList.objects.get(pk = list_id)
        if model.billing_account_id != profile.billing_account_id:
            print 'queue_edit queue.billing_account_id != billing_account_id'
            raise Http404
    if not request.POST:
        print 'n15'
    else:
        if request.POST.get("submit"):
            int_numb = request.POST.get("int_numb")
            one_field = False
            if form.is_valid():
                model = form.ok_model
                if model:
                    ## проверка файла со списком номеров
                    if form.cleaned_data['file_text']:
                        try:
                            if request.FILES['file_text']:
                                xString = request.FILES['file_text'].read()
                                cifri = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ',']
                                for i in xString:
                                    if i not in cifri:
                                        raise
                        except Exception, e:
                            request.notifications.add(_(u"Не правильно заполнен файл со списком номеров"), "error")
                            return ret_context(context, form, int_numb, formset_number, formset_group, formset_extnumber)
                    else:
                        if int_numb == '':
                            context['error'] = True
                            request.notifications.add(_(u"Ошибка. Добавьте хотя бы один номер в пункте 3"), "error")
                            return ret_context(context, form, int_numb, formset_number, formset_group, formset_extnumber)

                    if formset_number.is_valid():
                        ids = [int(form_set_number.cleaned_data['number_dyn']) for form_set_number in formset_number.forms]
                        q = []
                        for num in numbers:
                            for id in ids:
                                if num.id == id:
                                    q.append(num)

                    if formset_group.is_valid():
                        ids = [int(form_set_group.cleaned_data['group']) for form_set_group in formset_group.forms]
                        gr = []
                        for grp in existing_groups:
                            for id in ids:
                                if grp.id == id:
                                    gr.append(grp)

                    if formset_extnumber.is_valid():
                        ids = [int(form_set_extnumber.cleaned_data['extnumber']) for form_set_extnumber in formset_extnumber.forms]
                        ext = []
                        for ex in extnumbers:
                            for id in ids:
                                if ex.id == id:
                                    ext.append(ex)

                    if q == gr == ext == []:
                        context['error_in_4'] = True
                        request.notifications.add(_(u"Выберите внутренний или городской номер или группу"), "error")
                        return ret_context(context, form, int_numb, formset_number, formset_group, formset_extnumber)

                    type_call= form.cleaned_data['type_out_in']
                    query, id_type = get_query(form, type_call)
                    for m in ext:
                        for x in m.phone_numbers_group.numbers.all():
                            name = check_for_error_new(x, query)
                            if name:
                                sttt = get_notifications(name, x.tel_numbers)
                                request.notifications.add(
                                    mark_safe(sttt),
                                    "error"
                                )
                                #request.notifications.add(_(u"Номер %s уже задействован в списке противоположного типа - %s" % (x.tel_number, ', '.join(name),)), "error")
                                return ret_context(context, form, int_numb, formset_number, formset_group, formset_extnumber)
                    for k in gr:
                        for l in k.numbers.all():
                            name = check_for_error_new(l, query)
                            if name:
                                sttt = get_notifications(name, l.tel_number)
                                request.notifications.add(
                                    mark_safe(sttt),
                                    "error"
                                )
                                #request.notifications.add(_(u"Номер %s уже задействован в списке противоположного типа - %s" % (l.tel_number, ', '.join(name),)), "error")
                                return ret_context(context, form, int_numb, formset_number, formset_group, formset_extnumber)

                    for x in q:
                        name = check_for_error_new(x, query)
                        if name:
                            sttt = get_notifications(name, x.tel_number)
                            request.notifications.add(
                                mark_safe(sttt),
                                "error"
                            )
                            #request.notifications.add(_(u"Номер %s уже задействован в списке противоположного типа - %s" % (x.tel_number, ', '.join(name),)), "error")
                            return ret_context(context, form, int_numb, formset_number, formset_group, formset_extnumber)
                    model.billing_account_id = profile.billing_account_id

                    try:
                        model.save()
                    except Exception, e:
                        print e

                    if not one_field:
                        for numb in int_numb.strip(",").split(","):
                            if numb != '':
                                save_model_list_number(model.id, numb, profile)

                    if xString != '':
                        for num in xString.split(","):
                            print "sss: %s" % num
                            save_model_list_number(model.id, num, profile)

                    try:
                        group = TelNumbersList.objects.get(billing_account_id = profile.billing_account_id, id = model.id)
                    except TelNumbersList.DoesNotExist:
                        raise Http404
                    create_group_number_extnumber(gr, q, ext, type_call, group, id_type)
                    print "sozdano"
                    print 'number_list_%s' % (model.id,)
                    return HttpResponse('createnewelement_%s' % (model.id,))
                else:
                    return ret_context(context, form, int_numb, formset_number, formset_group, formset_extnumber)
        else:
            try:
                formset_number = ArticleFormSetNumber(prefix='number')
                formset_group = ArticleFormSetGroup(prefix='group')
                formset_extnumber = ArticleFormSetExtNumber(prefix='extnumber')
                form = ListNumberForm(model = model, profile = profile, request = request)
            except Exception, e:
                print e
    return ret_context(context, form, int_numb, formset_number, formset_group, formset_extnumber)

@login_required
@render_to('account/call_number.html')
def call_number(request, call_number_id=0, number_id=0, newelement=0, parent_newelement=0):
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context['newelement'] = newelement
    context['parent_newelement'] = parent_newelement
    context["number_id"] = number_id
    context["call_number_id"] = call_number_id
    profile = request.user.get_profile()
    model = CallNumber()
    if call_number_id and int(call_number_id) > 0:
        model = CallNumber.objects.get(pk = call_number_id)
        if model.billing_account_id != profile.billing_account_id:
            print 'CallNumber.billing_account_id != billing_account_id'
            raise Http404
    if request.POST:
        # Пришли данные в POST-запросе.
        if request.POST.get("submit"):
            form = CallNumberForm(model = model, data = request.POST, profile = profile, request = request)
            try:
                if form.is_valid():
                   if profile.has_billing_account:
                        model.number = request.POST.get("number")
                        model.billing_account_id = profile.billing_account_id
                        model.save()  # Сохранить ее в базе
                        print "sozdano"
                        print 'timerange_%s' % (model.id,)
                        if call_number_id and int(call_number_id) > 0:
                            return HttpResponse('editnewelement_%s' % (model.id,))
                        return HttpResponse('createnewelement_%s' % (model.id,))
                else:
                    print "Form not valid !"
                    context['form'] = form
                    return context
            except Exception, e:
                print e
        else:
            try:
                form = CallNumberForm(model = model, profile = profile, request = request)
            except Exception, e:
                print e
    context['form'] = form
    return context

def ret_context_call_list(context, int_numb):
    if int_numb != '':
        context["int_numb"] = int_numb
        context["list_int_numb"] = int_numb.strip(",").split(",")
    context["current_view_name"] = "phones_list"
    return context

def checklist(request, list_id):
    message = {"list_name": "", "list_numbers": []}
    list_numbers = []
    if request.is_ajax():
        list_n = TelNumbersList.objects.get(id=list_id)
        try:
            x = TelNumbersListDetailNumbers.objects.filter(telnumberslist__id=list_n.id)
        except Exception, e:
            print e
        message['list_name'] = list_n.name
        for i in x:
            list_numbers.append(i.number)
        message['list_numbers'] = list_numbers
    else:
        message = "You're the lying type, I can just tell."
    json = simplejson.dumps(message)
    return HttpResponse(json, mimetype='application/json')


#def checkbwlist(request, list_id):
#    context = {}
#    profile = request.user.get_profile()
#    if not profile or profile.is_card:
#        raise Http404
#    try:
#        model = TelNumbersList.objects.get(billing_account_id=profile.billing_account_id, id=list_id)
#    except TelNumbersList.DoesNotExist, e:
#        raise Http404
#    model_number_detail = TelNumbersListDetailNumbers.objects.filter(telnumberslist = model.id)
#    model_number = TelNumbersListNumbers.objects.filter(telnumberslist = model.id)
#    model_group = TelNumbersListGroups.objects.filter(telnumberslist = model.id)
#    model_extnumber = TelNumbersListExtNumbers.objects.filter(telnumberslist = model.id)
#    model_number_detail_list = []
#    model_number_list = []
#    model_extnumber_list = []
#    model_group_list = []
#    for x in model_number_detail:
#        model_number_detail_list.append(x.number)
#
#    for x in model_number:
#        model_number_list.append({'number_dyn':x.telnumber_id})
#        if x.type_out:
#            type_call = 2
#            type_list = x.type_out
#        elif x.type_in:
#            type_call = 1
#            type_list = x.type_in
#    if not model_number:
#        model_number_list.append({'number_dyn':0})
#
#    for x in model_group:
#        model_group_list.append({'group':x.group_id})
#        if x.type_out:
#            type_call = 2
#            type_list = x.type_out
#        elif x.type_in:
#            type_call = 1
#            type_list = x.type_in
#    if not model_group:
#        model_group_list.append({'group':0})
#
#    for x in model_extnumber:
#        model_extnumber_list.append({'extnumber':x.extnumber_id})
#        if x.type_out:
#            type_call = 2
#            type_list = x.type_out
#        elif x.type_in:
#            type_call = 1
#            type_list = x.type_in
#    if not model_extnumber:
#        model_extnumber_list.append({'extnumber':0})
#
#    ArticleFormSet = formset_factory(ListNumberDynForm,extra=0)
#
#    xString = ''
##    try:
##        type_call = request.GET['call']
##    except:
##        type_call = request.POST.get("call_type")
#    context = {}
#    bac = []
#    check_other_list_number = []
#    bac.append(profile.billing_account)
#    numbers = []
#    list_number = TelNumbersList.objects.filter(billing_account_id=profile.billing_account_id)
#    context["choices"] = {}
#    dict = {}
#    for list_n in list_number:
#        dict[list_n.id] = list_n.name
#    context["choices"] = dict
#    for ww in BillserviceAccount.objects.filter(assigned_to = profile.billing_account_id):
#        bac.append(ww)
#    for ba in bac:
#        for qq in TelNumber.objects.filter(account = ba):
#            numbers.append(qq)
#    existing_groups = TelNumbersGroup.objects.filter(account = profile.billing_account_id)
#    extnumbers = ExternalNumber.objects.filter(account=profile.billing_account_id)
#    try:
#        group = TelNumbersList.objects.get(billing_account_id = profile.billing_account_id, id = int(list_id))
#    except TelNumbersList.DoesNotExist:
#        raise Http404
#    context["title"] = _(u"""Редактирование списка "%s" """ % group.name)
#    context["edit"] = True
#    context["call_type"] = type_call
#    int_numb = ''
#    ArticleFormSetGroup = formset_factory(GroupDynForm,extra=0)
#    ArticleFormSetGroup.form = staticmethod(curry(GroupDynForm, existing_groups=existing_groups))
#    ArticleFormSetNumber = formset_factory(NumberDynForm,extra=0)
#    ArticleFormSetNumber.form = staticmethod(curry(NumberDynForm, numbers=numbers))
#    ArticleFormSetExtNumber = formset_factory(ExtNumberDynForm,extra=0)
#    ArticleFormSetExtNumber.form = staticmethod(curry(ExtNumberDynForm, extnumbers=extnumbers))
#    context['model_number_detail_list'] = model_number_detail_list
#    formset_number = ArticleFormSetNumber(initial = model_number_list, prefix='number')
#    formset_group = ArticleFormSetGroup(initial = model_group_list, prefix='group')
#    formset_extnumber = ArticleFormSetExtNumber(initial = model_extnumber_list, prefix='extnumber')
#    try:
#        form2 = ListNumberForm(model = model, profile = profile, request = request, id_type = type_list, type_call = type_call)
#        templ = loader.get_template("account/create_number_list_form.html")
#        if int_numb != '':
#            context["int_numb"] = int_numb
#            context["list_int_numb"] = int_numb.strip(",").split(",")
#        context["formset_number"] = formset_number
#        context["formset_group"] = formset_group
#        context["formset_extnumber"] = formset_extnumber
#        context["form"] = form2
#        context["current_view_name"] = "phones_list"
#        context = Context(context)
#    except Exception, e:
#        print e
#    return HttpResponse(templ.render(context))


@login_required
@render_to('account/call_list.html')
def call_list(request, list_id=0, edit_list_id=0, number_id=0, newelement=0, parent_newelement=0):
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context['newelement'] = newelement
    context['parent_newelement'] = parent_newelement
    context["number_id"] = number_id
    context["edit_list_id"] = edit_list_id

    profile = request.user.get_profile()
    xString = ''
    int_numb = ''
    list_number = TelNumbersList.objects.filter(call_list = True, billing_account_id=profile.billing_account_id)
    context["choices"] = {}
    dict = {}
    for list_n in list_number:
        dict[list_n.id] = list_n.name
    model = TelNumbersList()
    if list_id and int(list_id) > 0:
        model = TelNumbersList.objects.get(pk = list_id)
        if model.billing_account_id != profile.billing_account_id:
            print 'queue_edit queue.billing_account_id != billing_account_id'
            raise Http404
        model_num = TelNumbersListDetailNumbers.objects.filter(telnumberslist_id=list_id)
        model_num.delete()
    context["choices"] = dict
    if not request.POST:
        print 'n15'
    else:
        if request.POST.get("submit"):
            int_numb = request.POST.get("int_numb")
            ## проверка файла со списком номеров
#            if request.FILES['file_text']:
#                try:
#                    xString = request.FILES['file_text'].read()
#                    cifri = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ',']
#                    for i in xString:
#                        if i not in cifri:
#                            raise
#                except Exception, e:
#                    request.notifications.add(_(u"Не правильно заполнен файл со списком номеров"), "error")
#                    return ret_context_call_list(context, int_numb)
#            else:
            if int_numb == '':
                context['error'] = True
                request.notifications.add(_(u"Ошибка. Добавьте хотя бы один номер"), "error")
                return ret_context_call_list(context, int_numb)

            model.name = request.POST.get("name")
            model.billing_account_id = profile.billing_account_id
            model.call_list = True
            try:
                model.save()
            except Exception, e:
                print e

            for numb in int_numb.strip(",").split(","):
                if numb != '':
                    save_model_list_number(model.id, numb, profile)

#            if xString != '':
#                print xString
#                for num in xString.split(","):
#                    print "sss: %s" % num
#                    save_model_list_number(model.id, num, profile)

            #request.notifications.add(_(u"Список успешно сохранен"), "success")
            print 'createnewelement_%s' % (model.id,)
            return HttpResponse('createnewelement_%s' % (model.id,))
    return ret_context_call_list(context, int_numb)


def checkivr(request, ivr_id):
    context = {}
    profile = request.user.get_profile()
    if not profile or profile.is_card:
        raise Http404
    if int(ivr_id) > 0:
        try:
            model = create_myivr_temp.objects.get(billing_account_id_temp=profile.billing_account_id, id=ivr_id)
            modelka = create_myivr.objects.filter(billing_account_id=profile.billing_account_id, id_ivr=ivr_id)
        except create_myivr_temp.DoesNotExist, e:
            raise Http404
    elif int(ivr_id) == 0:
        model = create_myivr_temp()
        modelka = create_myivr()
    xString = ''
    context = {}
    int_numb = ''
    try:
        calli = []
        html = ""
        last_html = ""
        context["model"] = model
        numbers = profile.billing_account.phones
        context["choices_numbers"] = []
        context["choicesint"] = []
        my = []
        for number in numbers:
            tns = number.tel_number
            if number.person_name:
                tns += " (" + number.person_name + ")"
            context["choices_numbers"].append(tns)
            my.append(tns)
        for number in numbers:
            tns = number.tel_number
            context["choicesint"].append(tns)
        strm = ""

        i = 1
        context["len_pod_or"] = 0
        if int(ivr_id) > 0:
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
                html = html + """<input type="text" name="name_nabor%s" required value="%s" />""" % (i, cal.nabor)
                if i == 1:
                    html = html + """</label>"""
                html = html + """</li>"""

                html = html + """<li class="iform-item">"""
                if i == 1:
                    html = html + """<span class="label">"""
                    html = html + """%s""" % u'Название'
                    html = html + """<span class="tooltip">"""
                    html = html + """<i></i>"""
                    html = html + """<span class="tooltip-i">%s</span>""" % u'Укажите внутренний номер сотрудника, на который будет переключен вызов при нажатии указанного набора'
                    html = html + """</span>"""
                    html = html + """</span>"""
                html = html + """<input type="text" name="name_call%s" required value="%s" />""" % (i, cal.call)
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
                html = html + """</li>"""
                html = html + """</div>"""
                i = i + 1;
        context["html"] = html
        context = Context(context)
        templ = loader.get_template("account/ivr_form.html")
    except Exception, e:
        print e
    return HttpResponse(templ.render(context))

@login_required
@render_to('account/ivr.html')
def create_ivr(request, ivr_id=0, edit_menu_id=0, number_id=0, newelement=0, parent_newelement=0):
    context = {}
    context['newelement'] = newelement
    context['parent_newelement'] = parent_newelement
    context["number_id"] = number_id
    context["edit_menu_id"] = edit_menu_id
    profile = request.user.get_profile()
    if ivr_id:
        if int(ivr_id) > 0:
            try:
                model_temp = create_myivr_temp.objects.get(id=ivr_id)
                #modelka = create_myivr.objects.using(settings.BILLING_DB).filter(id_ivr=ivr_id)
            except Exception, e:
                raise Http404
        elif int(ivr_id) == 0:
            model_temp = create_myivr_temp()
    else:
        model_temp = create_myivr_temp()
    try:
        ivrs = create_myivr_temp.objects.filter(billing_account_id_temp=profile.billing_account_id)
    except Exception, e:
        print e
    context["choices"] = {}
    context["choices_numbers"] = []
    dict = {}

    for ivr in ivrs:
        dict[ivr.id] = ivr.name
    context["choices"] = dict

    numbers = profile.billing_account.phones
    my = []
    for number in numbers:
        tns = number.tel_number
        if number.person_name:
            tns += " (" + number.person_name + ")"
        context["choices_numbers"].append(tns)
        my.append(tns)

    if request.POST:
        # Пришли данные в POST-запросе.
        if request.POST.get("submit"):
            if request.POST.get("count_or") != "":
                count_or = int(request.POST.get("count_or")) + 1
            else:
                count_or = 1
            bool = check_nabor(request, count_or)
            if bool == False:
                request.notifications.add(_(u'Complete all fields!!!'), 'error')
                return context

            model_temp.name = request.POST.get("name")
            model_temp.billing_account_id_temp = profile.billing_account_id

            if not ivr_id or int(ivr_id) == 0:
                try:
                    model_temp.file_wav = request.FILES['file_wav']
                except:
                    request.notifications.add(_(u'Выберите медиа файл!'), 'error')
                    return context
            else:
                try:
                    model_temp.file_wav = request.FILES['file_wav']
                except:
                    pass

            print model_temp.file_wav
            file_check = str(model_temp.file_wav)
            try:
                if file_check.split('.')[-1] != "wav":
                    raise Exception
            except:
                request.notifications.add(_(u'Wrong format media file'), 'error')
                return context
            print 'ivr7'

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
            print 'ivr8'
            try:
                model_temp.save()
            except Exception, e:
                print e
            print 'ivr9'

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
                return context

            #rec_model(request, count_or, count_pod, model_temp.id, profile)
            if ivr_id:
                if int(ivr_id) > 0:
                    try:
                        model_ivr = create_myivr.objects.filter(id_ivr=ivr_id)
                        model_ivr.delete()
                        #count_or = int(request.POST.get("count_or_or")) + 1
                    except Exception, e:
                        raise Http404

            print "Count_or:%s" % count_or

            parent_dec_flag = False
            for i in range(0, count_or):
                try:
                    if not request.POST.get("name_nabor" + str(i)) and not request.POST.get("name_call" + str(i)):
#                        if edit_menu_id and edit_menu_id != '0':
#                            one_order = OrderScheme.objects.get(id_scheme_id=order.id_scheme_id, number_in_arterial=i)
#                            if one_order:
#                                parent_dec_flag = True
#                                one_order.delete()
                        continue
                    print i
                    print str(request.POST.get("name_nabor" + str(i)))
                    #print str(request.POST.get("name_call" + str(i)))
                    print model_temp.id
                    print profile.billing_account_id
                    model_ivr1 = create_myivr()
                    model_ivr1.billing_account_id = profile.billing_account_id
                    model_ivr1.nabor = request.POST.get("name_nabor" + str(i))
                    model_ivr1.call = request.POST.get("name_call" + str(i))
                    model_ivr1.id_ivr_id = model_temp.id
                    model_ivr1.save() # Сохранить ее в базе
                except Exception as e:
                    print e
            #request.notifications.add(_(u'Ivr successfully added ;)'), 'success')
            try:
                if edit_menu_id and edit_menu_id != '0':
                    print "Redaktirovanie 4erez cons"
                    order = OrderScheme.objects.get(id=edit_menu_id.split("_")[-1])
                    all_order = OrderScheme.objects.filter(id_scheme_id=order.id_scheme_id, nabor_for_ivr__gt='')
                    last_in_all_order = OrderScheme.objects.filter(id_scheme_id=order.id_scheme_id).order_by('number_in_arterial').reverse()[0]
                    k = last_in_all_order.number_in_arterial
                    for one in all_order:
                        try:
                            new_model_ivr = create_myivr.objects.get(id_ivr=ivr_id, nabor=one.nabor_for_ivr)
                        except create_myivr.DoesNotExist as e:
                            one.delete()
                            parent_dec_flag = True
                    new_model_ivr = create_myivr.objects.filter(id_ivr=ivr_id)
                    for one in new_model_ivr:
                        try:
                            one_order = OrderScheme.objects.get(id_scheme_id=order.id_scheme_id, nabor_for_ivr=one.nabor)
                        except OrderScheme.DoesNotExist as e:
                            parent_dec_flag = True
                            k = k + 1
                            new_order = OrderScheme()
                            new_order.id_scheme_id = int(order.id_scheme_id)
                            new_order.number_in_order = 1
                            new_order.type = "voice_menu"
                            new_order.id_element = int(edit_menu_id.split("_")[-2])
                            new_order.nabor_for_ivr = one.nabor
                            new_order.number_in_arterial = k
                            new_order.id_next_scheme_id = None
                            new_order.save()
                if parent_dec_flag:
                    z = request.POST['number_id']
                    try:
                        number = ExternalNumber.objects.get(id = z, account = profile.billing_account_id)
                    except ExternalNumber.DoesNotExist, e:
                        raise Http404
                    vsepomestam(OrderScheme.objects.filter(id_scheme_id = number.id_scheme_id))
            except Exception as e:
                    print e


            print "sozdano"
            print 'create_ivr_%s' % (model_temp.id,)
            if edit_menu_id and edit_menu_id != '0':
                return HttpResponse('editnewelement_%s' % (model_temp.id,))
            return HttpResponse('createnewelement_%s' % (model_temp.id,))
            #return HttpResponseRedirect("/account/myivr/")  # перейти на страницу со списком ивр
    return context

@login_required
@render_to('account/number_template.html')
def check_direction(request, templ_id=0, edit_temp_id=0, number_id=0, newelement=0, parent_newelement=0):
    """
        Новый шаблон
    """
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context['newelement'] = newelement
    context['parent_newelement'] = parent_newelement
    context["number_id"] = number_id
    profile = request.user.get_profile()
    context["title"] = _(u"Создание нового шаблона")
    context["edit_temp_id"] = edit_temp_id
    model_template_rules=[]
    ArticleFormSetNumber = formset_factory(NumberTemplate,extra=0)
    ArticleFormSetNumber.form = staticmethod(curry(NumberTemplate))
    context["select_all_rule"] = NumberTemplateRule.objects.filter(billing_account_id=profile.billing_account_id)
    if request.POST:
        if request.POST.get('submit'):
            formset_number = ArticleFormSetNumber(request.POST, prefix='number')
            if formset_number.is_valid():
                if request.POST.get('name_ready_template') != '0':
                    model_template = NumberTemplates.objects.get(id=request.POST.get('name_ready_template'))
                    model_template.number_template.all().delete()
                else:
                    model_template = NumberTemplates()
                model_template.billing_account_id = profile.billing_account_id
                model_template.name = request.POST.get('name_template')
                model_template.save()

                for form_set_number in formset_number.forms:
                    model = NumberTemplateRule()
                    model.number_template_rule = form_set_number.cleaned_data['template']
                    model.name = form_set_number.cleaned_data['name_template']
                    model.billing_account_id = profile.billing_account_id
                    model.save()
                    model_template.number_template.add(model)
                return HttpResponse('createnewelement_%s' % (model_template.id,))
            else:
                context["formset_number"] = formset_number
                return context
        else:
            context["all_account_template"] = NumberTemplates.objects.filter(billing_account_id=profile.billing_account_id)
            try:
                model_template = NumberTemplates.objects.get(id=edit_temp_id)
                numb_templ_rule = NumberTemplateRule.objects.filter(numbertemplates=model_template)
                context["select_template"] = model_template.id
                context["select_template_name"] = model_template.name
                for x in numb_templ_rule:
                    model_template_rules.append({'name_template':x.name,'template':x.number_template_rule})
                formset_number = ArticleFormSetNumber(initial = model_template_rules, prefix='number')
            except NumberTemplates.DoesNotExist:
                model_template_rules.append({'name_template':'','template':''})
                formset_number = ArticleFormSetNumber(initial = model_template_rules, prefix='number')
    context["formset_number"] = formset_number
    return context