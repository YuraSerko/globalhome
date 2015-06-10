# -*- coding: utf-8 -*-
from models import Rule
from lib.decorators import render_to, login_required
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from django.utils.translation import ugettext_lazy as _, ugettext
from forms import RuleEditForm, RulesListForm
from datetime import datetime
from settings import BILLING_DB
from fs.models import create_myivr_temp, fax_numbers
from billing.models import *
from content.models import Article
from django.http import Http404
from fs.models import GatewayModel
from fs.gateway import recursive
from telnumbers.models import TelNumbersGroupNumbers

settings.cross_warnings = []
settings.cross_errors = []

@login_required
@render_to('call_forwarding_list.html')
def rules_list(request):  # OK!
    """
        Отображает список правил переадресации
    """
    if request.user.get_profile().is_card:
        raise Http404

    profile = request.user.get_profile()
    context = {}
    context["title"] = _(u"Call forwarding rules")

    try:
        user_guide_article = Article.objects.get(slug="call_forwarding_list_user_guide")
        user_guide = user_guide_article.text
        context["user_guide"] = user_guide
    except:
        pass

    profile = request.user.get_profile()

    if profile:
        if profile.has_billing_account:
            if profile.billing_account.phones:
                context["have_numbers"] = True
            else:
                context["have_numbers"] = False

            rules = Rule.objects.using(BILLING_DB).filter(
                billing_account_id=profile.billing_account_id
            )

            if not request.POST:
                # нету данных, отображаем список правил
                # получить список правил
                for rule in rules:
                    if settings.cross_warnings.count(rule):
                        rule.warning = True
                    if settings.cross_errors.count(rule):
                        rule.error = True

                settings.cross_warnings = []
                settings.cross_errors = []

                form = RulesListForm(rules=rules)
            else:
                # пришли данные, надо включить/выключить некоторые правила
                if request.POST.get("submit"):
                    forwards = Rule.objects.filter(billing_account_id=profile.billing_account_id)

                    form = RulesListForm(rules=rules, request=request)

                    for forw in forwards:
                        if request.POST.get("enabled_%s" % str(forw.id)) == "on":
                            print "from:%s" % forw.from_number
                            try:
                                forward = Rule.objects.get(from_number=forw.from_number, enabled=True).exlude(id=forw.id)
                            except:
                                forward = None
                            if forward != None:
                                request.notifications.add(_(u"On this issue of the diversion"), "warning")
                                return HttpResponseRedirect("/account/call_forwarding/")

                            try:
                                getfax = fax_numbers.objects.get(number=forw.from_number, enabled=True)
                            except:
                                getfax = None
                            if getfax != None:
                                request.notifications.add(_(u"On this issue of the fax function"), "warning")
                                return HttpResponseRedirect("/account/call_forwarding/")

                            try:
                                print "1"
                                temp_ivr = create_myivr_temp.objects.get(number__tel_number=forw.from_number, enabled=True)
                                print "2"
                            except:
                                temp_ivr = None
                            if temp_ivr != None:
                                request.notifications.add(_(u"On this issue is included ivr"), "warning")
                                return HttpResponseRedirect("/account/call_forwarding/")

                    if form.check_cross_ok():
                        rules = form.get_changed_rules()
                        for rule in rules:
                            rule.save()

                        settings.cross_warnings = []
                        settings.cross_errors = []
                    else:
                        settings.cross_warnings = form.cross_warnings
                        settings.cross_errors = form.cross_errors

                        return HttpResponseRedirect("/account/call_forwarding/")
                else:
                    return HttpResponseRedirect("/account/call_forwarding/")

            context["form"] = form
            context["rules"] = rules
    context["current_view_name"] = "callforwarding_rules_list"
    return context

@login_required
@render_to('call_forwarding_edit_rule.html')
def rule_add(request):  # OK!
    """
        Добавляем правило
    """


    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context["title"] = _(u"Adding call forwarding rule")
    context["adding_new"] = True
    try:
        user_guide_article = Article.objects.get(slug="call_forwarding_add_user_guide")
        user_guide = user_guide_article.text
        context["user_guide"] = user_guide
    except:
        pass

    model = Rule()

    profile = request.user.get_profile()  # получаем профиль текущего пользователя

    if not request.POST:
        # Первый вызов. Просто отобразить пустую форму.
        form = RuleEditForm(model=model, profile=profile, request=request)
    else:
        # Пришли данные в POST-запросе.
        # Надо проверить форму на валижность,
        # потом проверить на пересекаемость временных интервалов
        # потом добавить в базу


        if request.POST.get("submit"):  # если нажали Submit а не Cancel
            rule_number = request.POST.get("from_number")
            to_number = request.POST.get("to_number")

            try:
                getfax = fax_numbers.objects.get(number=rule_number, enabled=True)
            except:
                getfax = None
            if getfax != None:
                request.notifications.add(_(u"On this issue of the fax function"), "warning")
                return HttpResponseRedirect("/account/call_forwarding/add_rule/")


            temp_ivr = create_myivr_temp.objects.filter(billing_account_id_temp=profile.billing_account_id, enabled=True, number__tel_number=rule_number)
            if temp_ivr:
                request.notifications.add(_(u"On this issue is included ivr"), "warning")
                return HttpResponseRedirect("/account/call_forwarding/add_rule/")
            # получаем форму из запроса
            form = RuleEditForm(model=model, data=request.POST, profile=profile, request=request)
            flag = recursive(to_number)
            if not flag:
                gr_id = TelNumbersGroupNumbers.objects.filter(telnumber__tel_number=rule_number)
                print rule_number
                gateway = None
                for g_id in gr_id:
                    gateway = GatewayModel.objects.filter(tel_group=g_id.telnumbersgroup_id, enabled=True)
                if gateway:
                    request.notifications.add(_(u"Данный номер или номер, участвующий в цепочке из переадресаций, задействован в регистрации на внешних Sip сервисах"), "warning")
                    context['form'] = form
                    return context
            # проверяем на валидность
            if form.is_valid():  # если форма верная
                # model = form.GetModel()         # получить модель
                model = form.ok_model
                if model:
                    if profile:
                        if profile.has_billing_account:
                            model.billing_account_id = profile.billing_account_id
                            model.save()  # Сохранить ее в базе
                            request.notifications.add(_(u"Rule was succesfuly added."), "success")
                            return HttpResponseRedirect("/account/call_forwarding/")  # перейти на страницу со списком правил
                        else:
                            raise Error("Current user don't have a billing account!")
                    else:
                        raise Error("Cannot get current user's profile!")
                else:
                    return HttpResponseRedirect("/account/call_forwarding/add_rule/")
        else:
            return HttpResponseRedirect("/account/call_forwarding/")

    context["current_view_name"] = "callforwarding_rules_list"
    context["form"] = form
    return context

@login_required
@render_to('call_forwarding_edit_rule.html')
def rule_edit(request, rule_id):  # OK!
    """
        Редактируем заданное правило
    """

    if request.user.get_profile().is_card:
        raise Http404

    context = {}
    context["title"] = _(u"Editing call forwarding rule")
    context["rule_id"] = rule_id
    try:
        user_guide_article = Article.objects.get(slug="call_forwarding_edit_user_guide")
        user_guide = user_guide_article.text
        context["user_guide"] = user_guide
    except:
        pass

    model = None
    try:
        model = Rule.objects.using(BILLING_DB).get(id=rule_id)
    except:
        pass
    profile = request.user.get_profile()  # получаем профиль текущего пользователя

    if model.billing_account_id != profile.billing_account_id:
        # Пользователь запросил не своё правило, фигу ему!
        return HttpResponseNotFound()
    if not request.POST:
        # Первый вызов. Просто отобразить форму.
        form = RuleEditForm(model=model, profile=profile, request=request)
    else:
        # Пришли данные в POST-запросе.
        # Надо проверить форму на валижность,
        # потом проверить на пересекаемость временных интервалов
        # потом добавить в базу


        if model.billing_account_id != profile.billing_account_id:
            # Пользователь запросил не своё правило, фигу ему!
            return HttpResponseNotFound()

        if request.POST.get("submit"):  # если нажали Submit а не Cancel
            rule_number = request.POST.get("from_number")
            to_number = request.POST.get("to_number")


            try:
                getfax = fax_numbers.objects.get(number=rule_number, enabled=True)
            except:
                getfax = None
            if getfax != None:
                request.notifications.add(_(u"On this issue of the fax function"), "warning")
                return HttpResponseRedirect("/account/call_forwarding/edit_rule/%s/" % rule_id)
            try:
                temp_ivr = create_myivr_temp.objects.filter(billing_account_id_temp=profile.billing_account_id, enabled=True, number__tel_number=rule_number)
            except Exception, e:
                temp_ivr = None
            if temp_ivr:
                request.notifications.add(_(u"On this issue is included ivr"), "warning")
                return HttpResponseRedirect("/account/call_forwarding/edit_rule/%s/" % rule_id)
            # получаем форму из запроса
            form = RuleEditForm(model=model, data=request.POST, profile=profile, request=request)
            flag = recursive(to_number)
            if not flag:
                gr_id = TelNumbersGroupNumbers.objects.filter(telnumber__tel_number=rule_number)
                print rule_number
                gateway = None
                for g_id in gr_id:
                    gateway = GatewayModel.objects.filter(tel_group=g_id.telnumbersgroup_id, enabled=True)
                if gateway:
                    request.notifications.add(_(u"Данный номер или номер, участвующий в цепочке из переадресаций, задействован в регистрации на внешних Sip сервисах"), "warning")
                    context['form'] = form
                    return context
            # проверяем на валидность
            if form.is_valid():  # если форма верная
                # model = form.GetModel()         # получить модель
                model = form.ok_model
                if model:
                    model.save()  # Сохранить ее в базе
                    request.notifications.add(_(u"Rule was succesfuly saved."), "success")
                    return HttpResponseRedirect("/account/call_forwarding/")  # перейти на страницу со списком правил
        else:
            return HttpResponseRedirect("/account/call_forwarding/")

    context["form"] = form
    context["current_view_name"] = "callforwarding_rules_list"
    return context

@login_required
@render_to('call_forwarding_delete_rule.html')
def rule_delete(request, rule_id):  # OK!
    """
        Удаляем заданное правило
    """

    if request.user.get_profile().is_card:
        raise Http404

    context = {}
    context["title"] = _(u"Deleting call forwarding rule")

    profile = request.user.get_profile()
    model = None

    try:
        model = Rule.objects.using(BILLING_DB).get(id=rule_id)
    except:
        pass

    context["rule"] = model

    if model:
        if model.billing_account_id != profile.billing_account_id:
            # Пользователь запросил не своё правило, фигу ему!
            return HttpResponseNotFound()
    else:
        return HttpResponseNotFound()

    if request.POST:
        if request.POST.get("submit"):  # если нажали Submit а не Cancel
            if model:
                if model.billing_account_id != profile.billing_account_id:
                    # Пользователь запросил не своё правило, фигу ему!
                    return HttpResponseNotFound()

                model.delete()
                request.notifications.add(_(u"Rule was succesfuly deleted."), "success")
        return HttpResponseRedirect("/account/call_forwarding/")
    context["current_view_name"] = "callforwarding_rules_list"
    return context

def check_rule(request):
    print "check_RULE"
    number_fax = request.GET['number_fax']

    try:
        ivr = create_myivr_temp.objects.get(number__tel_number=number_fax, enabled=True)
    except:
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

    print number_fax
    return HttpResponse("ok")


