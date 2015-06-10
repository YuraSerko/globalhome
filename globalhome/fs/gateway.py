# -*- coding=utf-8 -*-
# Create your views here.

from forms import GatewayForm
from models import GatewayModel
from django.http import Http404
from lib.decorators import render_to, login_required
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from telnumbers.forms import group_widget_data
from fsmanage.admin import telnet_login
from settings import FREESWITCH
from telnumbers.models import TelNumbersGroup, TelNumbersGroupNumbers
from call_forwarding.models import Rule
import time

def recursive(int_numb):
    allforward = Rule.objects.filter(from_number=int_numb)
    print "recursive"
    if allforward:
        for x in allforward:
            if '@' in x.to_number:
                return False
            elif len(x.to_number)==7:
                print "len7"
                fl = recursive(x.to_number)
                return fl
    elif '@' in str(int_numb):
        return False
    return True

def get_status_gateway(label, id_gateway):
    fs = telnet_login(FREESWITCH[label]['ESL_HOST'], FREESWITCH[label]['ESL_PORT'], FREESWITCH[label]['ESL_PASSWORD'])
    fs.write("api sofia profile registration rescan\r\n\r\n")
    time.sleep(5)
    fs.write("api sofia status gateway %s\r\n\r\n" % (id_gateway,))
    data = fs.read_until("total.", 10).splitlines()

    return data, fs

@login_required
@render_to('list_gateway.html')
def list_gateway(request):
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context["title"] = _(u"Sip подключение: Ваши подключения")
    context["current_view_name"] = "list_gateway"
    profile = request.user.get_profile()
    if profile:
        if profile.has_billing_account:
            if profile.billing_account.phones:
                context["have_numbers"] = True
            else:
                context["have_numbers"] = False
        list_gateway = GatewayModel.objects.filter(billing_account_id=profile.billing_account_id)

        if list_gateway:
            context["gateways"] = list_gateway

        if request.POST:
            # пришли данные, надо включить/выключить некоторые ivr
            if request.POST.get("save"):
                for gateway in list_gateway:
                    if request.POST.get(str(gateway.id)) == "on":
                        if not gateway.enabled:
                            print gateway.tel_group_id
                            model_group = TelNumbersGroupNumbers.objects.filter(telnumbersgroup=gateway.tel_group_id)
                            for x in model_group:
                                print x.telnumber
                                flag = recursive(x.telnumber)
                                if not flag:
                                    request.notifications.add(_(u'Данная услуга недоступна при включенной переадресации на Sip-аккаунт другого сервиса'), 'error')
                                    return context

                            gateway.enabled = True
                            gateway.label = 'fs2'
                            gateway.save()
                            data, fs = get_status_gateway('fs2', str(gateway.id))
                            for dat in data:
                                if dat[:5] == "State":
                                    if "UNREGED" in dat.split(" ")[-1]:
                                        fs.write("api sofia profile registration killgw %s\r\n\r\n" % (str(gateway.id),))
                                        request.notifications.add(_(u'Sip подключение не включено, проверьте правильность логина и пароля'), 'error')
                                        gateway.enabled = False
                                        gateway.save()
                                    elif "REGED" in dat.split(" ")[-1]:
                                        request.notifications.add(_(u'Sip подключение успешно включено'), 'success')
                                    else:
                                        fs.write("api sofia profile registration killgw %s\r\n\r\n" % (str(gateway.id),))
                                        request.notifications.add(_(u'Sip подключение не включено, проверьте правильность логина и пароля'), 'error')
                                        gateway.enabled = False
                                        gateway.save()
                    else:
                        if gateway.enabled:
                            if gateway.label:
                                fs = telnet_login(FREESWITCH[str(gateway.label)]['ESL_HOST'], FREESWITCH[str(gateway.label)]['ESL_PORT'], FREESWITCH[str(gateway.label)]['ESL_PASSWORD'])
                                fs.write("api sofia profile registration killgw %s\r\n\r\n" % (str(gateway.id),))
                                gateway.label = None
                            gateway.enabled = False
                            gateway.save()
            else:
                return HttpResponseRedirect("/account/gateway/")
    return context


@login_required
@render_to('add_gateway.html')
def add_gateway(request, id_gateway=None):
    if request.user.get_profile().is_card:
        raise Http404
    profile = request.user.get_profile()
    context = {}
    if not id_gateway:
        model = GatewayModel()
        context["title"] = _(u"Sip подключение: Создание")
    else:
        context["title"] = _(u"Sip подключение: Редактирование")
        try:
            model = GatewayModel.objects.get(id=id_gateway, billing_account_id=profile.billing_account_id)
        except GatewayModel.DoesNotExist:
            raise Http404
    if profile:
        if profile.has_billing_account:
            if profile.billing_account.phones:
                context["have_numbers"] = True
            else:
                context["have_numbers"] = False
    try:
        g_id = model.tel_group.id
    except:
        g_id = -1
    print g_id
    context["hid"] = g_id
    groups = profile.billing_account.telnumbersgroup_set.all()
    choices, settings = group_widget_data(groups, g_id)
    if not request.POST:
        # Первый вызов. Просто отобразить пустую форму.
        form = GatewayForm(model=model, profile=profile, request=request, choices=choices, settings=settings)
    else:
        if request.POST.get("connect"):
            form = GatewayForm(model=model, data=request.POST, profile=profile, request=request, choices=choices, settings=settings)
            if form.is_valid():  # если форма верная
                # model = form.ok_model
                try:
                    if not id_gateway:
                        model_check = GatewayModel.objects.get(sip_address_original=request.POST.get("sip_address"), login=request.POST.get("login"))
                        if model_check:
                            request.notifications.add(_(u'Sip подключение уже существует'), 'error')
                            context["form"] = form
                            return context
                except GatewayModel.DoesNotExist:
                    pass
                model.billing_account_id = profile.billing_account_id
                model.sip_address_original = form.cleaned_data["sip_address"]
                model.sip_address = form.cleaned_data["sip_address"]
                model.login = form.cleaned_data["login"]
                model.password = form.cleaned_data["password"]
                model.tel_group_id = form.cleaned_data["user_groups"]

                model_group = TelNumbersGroupNumbers.objects.filter(telnumbersgroup=model.tel_group_id)
                for x in model_group:
                    flag = recursive(x.telnumber)
                    if not flag:
                        request.notifications.add(_(u'Данная услуга недоступна при включенной переадресации на Sip-аккаунт другого сервиса'), 'error')
                        context["form"] = form
                        return context

                if id_gateway:
                    fs = telnet_login(FREESWITCH[str(model.label)]['ESL_HOST'], FREESWITCH[str(model.label)]['ESL_PORT'], FREESWITCH[str(model.label)]['ESL_PASSWORD'])
                    fs.write("api sofia profile registration killgw %s\r\n\r\n" % (str(id_gateway)))
                model.label = 'fs2'
                model.save()  # Сохранить ее в базе
                id_add = ""
                data, fs = get_status_gateway('fs2', str(model.id))
                for dat in data:
                    if dat[:5] == "State":
                        if "UNREGED" in dat.split(" ")[-1]:
                            if not id_gateway:
                                id_add = str(model.id)
                                model.delete()
                            else:
                                id_add = str(model.id)
                                model.enabled = False
                                model.save()
                            fs.write("api sofia profile registration killgw %s\r\n\r\n" % (id_add,))
                            request.notifications.add(_(u'Sip подключение не добавлено, проверьте правильность логина и пароля'), 'error')
                            context["form"] = form
                            return context
                        elif "REGED" in dat.split(" ")[-1]:
                            request.notifications.add(_(u'Sip подключение успешно добавлено'), 'success')
                        else:
                            if not id_gateway:
                                id_add = str(model.id)
                                model.delete()
                            else:
                                id_add = str(model.id)
                                model.enabled = False
                                model.save()
                            fs.write("api sofia profile registration killgw %s\r\n\r\n" % (id_add,))
                            request.notifications.add(_(u'Sip подключение не добавлено, проверьте правильность логина и пароля'), 'error')
                            context["form"] = form
                            return context

                return HttpResponseRedirect("/account/gateway/")
        else:
            return HttpResponseRedirect("/account/gateway/")
    context["current_view_name"] = "list_gateway"
    context["form"] = form
    return context


@login_required
@render_to('delete_gateway.html')
def delete_gateway(request, id_gateway):
    """Удаление"""
    profile = request.user.get_profile()
    if not profile:
        raise Http404
    if profile.is_card:
        raise Http404

    context = {}
    context["title"] = _(u"Sip подключение: Удалить подключение")
    model = None

    try:
        model = GatewayModel.objects.get(id=id_gateway)
    except GatewayModel.DoesNotExist:
        raise Http404

    context["gateway"] = model
    if model.billing_account_id != profile.billing_account_id:
        raise Http404
    if request.POST:
        if request.POST.get("submit"):  # если нажали Submit а не Cancel
            if model.enabled:
                print "model.enabled"
                if model.label:
                    fs = telnet_login(FREESWITCH[str(model.label)]['ESL_HOST'], FREESWITCH[str(model.label)]['ESL_PORT'], FREESWITCH[str(model.label)]['ESL_PASSWORD'])
                    fs.write("api sofia profile registration killgw %s\r\n\r\n" % (str(model.id)))
            model.delete()
            request.notifications.add(_(u"Подключение удалено"), "success")
        return HttpResponseRedirect("/account/gateway/")
    context["current_view_name"] = "list_gateway"
    return context
