# -*- coding=utf-8 -*-
# Create your views here.
import os, sys
from lib.decorators import render_to, login_required, render_to_response
try:
    from settings import *
    from settings import BILLING_DB, MEDIA_ROOT, FREESWITCH
    from django.http import Http404
    from string import split
    from models import fax_numbers, create_myivr_temp
    from call_forwarding.models import Rule
    from lib.decorators import render_to, login_required, render_to_response
    from django.utils.translation import ugettext_lazy as _
    from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
    #from django_extensions.management.commands.dumpscript import InstanceCode
except Exception,e:
    print "get_fax exception: %s" % e
    exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print "Exception in createSSHClient: file:%s line:%s" % (fname, exc_tb.tb_lineno)

@login_required
@render_to('list_getfax.html')
def list_getfax(request):
    """
        Отображает список всех факсов
    """
    if request.user.get_profile().is_card:
        raise Http404

    context = {}
    context["title"] = _(u"List fax numbers")
    profile = request.user.get_profile()

    if profile:
        if profile.has_billing_account:
            if profile.billing_account.phones:
                context["have_numbers"] = True
            else:
                context["have_numbers"] = False

            faxs = fax_numbers.objects.filter(billing_account_id = profile.billing_account_id)
            if request.POST:
                # пришли данные, надо включить/выключить некоторые ivr
                if request.POST.get("submit"):
                    for fax in faxs:
                        if request.POST.get(str(fax.id))=="on":
                            try:
                                forward = Rule.objects.get(from_number = fax.number, enabled = True)
                            except:
                                forward = None
                            if forward != None:
                                request.notifications.add(_(u"On this issue of the diversion"), "warning")
                                return HttpResponseRedirect("/account/getfax/list_getfax/")
                            try:
                                ivr = create_myivr_temp.objects.get(number_ivr = fax.number, enabled = True)
                            except:
                                ivr = None
                            if ivr != None:
                                request.notifications.add(_(u"On this issue is included ivr"), "warning")
                                return HttpResponseRedirect("/account/getfax/list_getfax/")
                            temp_getfax = fax_numbers.objects.filter(billing_account_id = profile.billing_account_id,enabled = True,number = fax.number).exclude(id = fax.id)
                            if temp_getfax:
                                request.notifications.add(_(u"This number is already in use"), "warning")
                                return HttpResponseRedirect("/account/getfax/list_getfax/")
                            fax.enabled = True
                        else:
                            fax.enabled = False
                        fax.save()
                else:
                    return HttpResponseRedirect("/account/getfax/list_getfax/")

            context["getfaxs"] = faxs
    context['current_view_name'] = 'list_getfax'
    return context

@login_required
@render_to('create_getfax.html')
def create_getfax(request, getfax_id=0):
    """
        Создание и редактирование
    """
    if request.user.get_profile().is_card:
        raise Http404

    context = {}
    context["title"] = _(u"Receive fax")
    profile = request.user.get_profile()
    context["red_fax"] = []
    if getfax_id:
        redact = fax_numbers.objects.get(id = getfax_id)
        context["red_fax"] = fax_numbers.objects.get(id = getfax_id)
        emaili = redact.email.split(",")
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
    numbers = profile.billing_account.phones
    context["choices"] = []
    for number in numbers:
        tns = number.tel_number
        if number.person_name:
            tns += " (" + number.person_name + ")"
        context["choices"].append( (tns) )
    if request.POST:
        # Пришли данные в POST-запросе.
        if request.POST.get("submit"):
            number_fax = request.POST.get("number")[:7]

            if getfax_id > 0:
                use = "/account/getfax/edit_getfax/%s/" % getfax_id
            else:
                use = "/account/getfax/create_getfax/"

            temp_getfax = fax_numbers.objects.filter(billing_account_id = profile.billing_account_id,enabled = True,number = number_fax).exclude(id=getfax_id)
            if temp_getfax:
                request.notifications.add(_(u"This number is already in use"), "warning")
                return HttpResponseRedirect(use)

            try:
                forward = Rule.objects.get(from_number = number_fax, enabled = True)
            except:
                forward = None
            if forward != None:
                context["style"] = "block"
                context["class"] = "error"
                context["text"] = "On this issue of the diversion"
                context["email"] = request.POST.get("email_adress")
                context["number"] = request.POST.get("number")
                return context

            try:
                ivr = create_myivr_temp.objects.get(number_ivr = number_fax, enabled = True)
            except:
                ivr = None
            if ivr != None:
                context["style"] = "block"
                context["class"] = "error"
                context["text"] = "On this issue is included ivr"
                context["email"] = request.POST.get("email_adress")
                context["number"] = request.POST.get("number")
                return context


            if getfax_id > 0:
                model = fax_numbers.objects.using(BILLING_DB).get(id = getfax_id)
                request.notifications.add(_(u'Факс успешно отредактирован'), 'success')
            else:
                model = fax_numbers()
                model.enabled = True
                request.notifications.add(_(u'Факс успешно добавлен'), 'success')
            model.number = request.POST.get("number")[:7]
            emailik = ""
            count = int(request.POST.get("count_email"))
            for i in range(1, count+1):
                emailik = emailik + request.POST.get("email_adress" + str(i))
                emailik = emailik + ','
            model.email = emailik.strip(',')
            model.billing_account_id = profile.billing_account_id
            model.save()
            return HttpResponseRedirect("/account/getfax/list_getfax/")
        else:
            return HttpResponseRedirect("/account/getfax/list_getfax/")
    context['current_view_name'] = 'list_getfax'
    return context

@login_required
@render_to('delete_getfax.html')
def delete_getfax(request, getfax_id): # OK!
    """
        Удаляем ivr
    """
    if request.user.get_profile().is_card:
        raise Http404

    context = {}
    context["title"] = _(u"Clear fax number")
    profile = request.user.get_profile()
    model = None

    try:
        model = fax_numbers.objects.using(BILLING_DB).get(id = getfax_id)
    except:
        pass

    context["getfax"] = model
    if model:
        if model.billing_account_id != profile.billing_account_id:
            return HttpResponseNotFound()
    else:
        return HttpResponseNotFound()
    if request.POST:
        if request.POST.get("submit"): # если нажали Submit а не Cancel
            if model:
                if model.billing_account_id != profile.billing_account_id:
                    return HttpResponseNotFound()
                model.delete()
                request.notifications.add(_(u"Fax number was succesfuly cleared."), "success")
        return HttpResponseRedirect("/account/getfax/list_getfax/")
    context['current_view_name'] = 'list_getfax'
    return context


def ajax_check(request):
    try:
        number_fax = request.GET['number_fax'][:7]
    except Exception, e:
        raise Http404
    if not number_fax.isdigit():
        return HttpResponse("no_number")
    else:
        try:
            forward = Rule.objects.get(from_number = number_fax, enabled = True)
        except:
            forward = None
        if forward != None:
            return HttpResponse("gra4")

        try:
            ivr = create_myivr_temp.objects.get(number_ivr = number_fax, enabled = True)
        except:
            ivr = None
        if ivr != None:
            return HttpResponse("ivr_gra4")

        try:
            getfax = fax_numbers.objects.get(number = number_fax, enabled = True)
        except:
            getfax = None
        if getfax != None:
            return HttpResponse("getfax_gra4")
        return HttpResponse("ok")