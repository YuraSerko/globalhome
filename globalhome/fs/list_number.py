# -*- coding=utf-8 -*-
# Create your views here.
import os, sys
import copy
import json
from lib.decorators import render_to, login_required, render_to_response
from settings import *
from settings import BILLING_DB, MEDIA_ROOT, FREESWITCH, OBZVON_URL
from django.http import Http404
from lib.decorators import render_to, login_required, render_to_response
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from forms import ListNumberDynForm, ListNumberForm, NumberDynForm, ExtNumberDynForm, GroupDynForm
from models import TelNumbersList, TelNumbersListNumbers, TelNumbersListDetailNumbers, TelNumbersListGroups, TelNumbersListExtNumbers
from django.forms.formsets import formset_factory
from billing.models import BillserviceAccount
from django.db.models import Q
from telnumbers.models import TelNumber, TelNumbersGroup
from externalnumbers.models import ExternalNumber
from django.utils.functional import curry
import codecs
from django.utils.safestring import mark_safe


@login_required
@render_to('list_number.html')
def groups_list(request):
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context["title"] = _(u"Списки номеров")
    profile = request.user.get_profile()
    if profile.billing_account.phones:
        context["have_numbers"] = True
    else:
        context["have_numbers"] = False

    try:
        groups2 = TelNumbersList.objects.filter(billing_account_id = profile.billing_account_id)
    except Exception, e:
        raise Http404
    list_dict_in_name = {}
    list_dict_out_name = {}
    list_dict_black = {}
    list_dict_white = {}
    d_black = {}
    d_white = {}
    ext_black = {}
    ext_white = {}

    for group in groups2:
        list_dict_black[group.id] = {1:[], 2:[]}
        list_dict_white[group.id] = {1:[], 2:[]}
        d_black[group.id] = {1:[], 2:[]}
        d_white[group.id] = {1:[], 2:[]}
        ext_black[group.id] = {1:[], 2:[]}
        ext_white[group.id] = {1:[], 2:[]}

        list_dict_in_name[group.id] = group.name
        list_dict_out_name[group.id] = group.name

        lists = TelNumbersListNumbers.objects.filter(telnumberslist_id = group.id)
        for l in lists:
            if l.type_in == 1:
                list_dict_black[group.id][1].append(l.telnumber.tel_number)
            elif l.type_in == 2:
                list_dict_white[group.id][1].append(l.telnumber.tel_number)

            if l.type_out == 1:
                list_dict_black[group.id][2].append(l.telnumber.tel_number)
            elif l.type_out == 2:
                list_dict_white[group.id][2].append(l.telnumber.tel_number)

        groups = TelNumbersListGroups.objects.filter(telnumberslist_id = group.id)
        for g in groups:
            if g.type_in == 1:
                d_black[group.id][1].append(g.group.name)
            elif g.type_in == 2:
                d_white[group.id][1].append(g.group.name)
            if g.type_out == 1:
                d_black[group.id][2].append(g.group.name)
            elif g.type_out == 2:
                d_white[group.id][2].append(g.group.name)

        extn = TelNumbersListExtNumbers.objects.filter(telnumberslist_id = group.id)
        for e in extn:
            if e.type_in == 1:
                ext_black[group.id][1].append(e.extnumber.number)
            elif e.type_in == 2:
                ext_white[group.id][1].append(e.extnumber.number)
            if e.type_out == 1:
                ext_black[group.id][2].append(e.extnumber.number)
            elif e.type_out == 2:
                ext_white[group.id][2].append(e.extnumber.number)

        for m in list_dict_black[group.id].keys():
            if list_dict_black[group.id][m] == [] and d_black[group.id][m] == [] and ext_black[group.id][m] == []:
                del list_dict_black[group.id][m]
                del d_black[group.id][m]
                del ext_black[group.id][m]

        for m in list_dict_white[group.id].keys():
            if list_dict_white[group.id][m] == [] and d_white[group.id][m] == [] and ext_white[group.id][m] == []:
                del list_dict_white[group.id][m]
                del d_white[group.id][m]
                del ext_white[group.id][m]
            if list_dict_white[group.id] == {}:
                del list_dict_white[group.id]
                del ext_white[group.id]
                del d_white[group.id]

    context["current_view_name"] = "phones_list"
    context["list_dict_in_name"] = list_dict_in_name
    context["list_dict_out_name"] = list_dict_out_name
    context["ext_black"] = ext_black
    context["ext_white"] = ext_white
    context["d_black"] = d_black
    context["d_white"] = d_white
    context["list_dict_black"] = list_dict_black
    context["list_dict_white"] = list_dict_white
    return context

def save_model_list_number(id, number, profile):
    model_number = TelNumbersListDetailNumbers()
    model_number.billing_account_id = profile.billing_account_id
    model_number.telnumberslist_id = id
    model_number.number = number
    model_number.save()

@login_required
@render_to('list_number_delete.html')
def groups_list_delete(request, id_list):
    """Удаление"""
    profile = request.user.get_profile()
    if profile.is_card:
        raise Http404
    context = {}
    context["title"] = _(u"Удаление списка")
    model = None
    try:
        model = TelNumbersList.objects.get(billing_account_id=profile.billing_account_id, id=id_list)
    except TelNumbersList.DoesNotExist:
        raise Http404
    numbers = TelNumbersListDetailNumbers.objects.filter(telnumberslist_id=id_list)
    lists = TelNumbersListNumbers.objects.filter(telnumberslist_id = id_list)
    groups = TelNumbersListGroups.objects.filter(telnumberslist_id = id_list)
    extn = TelNumbersListExtNumbers.objects.filter(telnumberslist_id = id_list)

    context["list_numbers"] = ', '.join(numbers.values_list('number', flat=True))
    context["lists"] = ', '.join(lists.values_list('telnumber__tel_number', flat=True))
    context["groups"] = ', '.join(groups.values_list('group__name', flat=True))
    context["extn"] = ', '.join(extn.values_list('extnumber__number', flat=True))
    context["list"] = model
    if request.POST:
        if request.POST.get("submit"):  # если нажали Submit а не Cancel
            model.delete()
            request.notifications.add(_(u"Список удален"), "success")
        return HttpResponseRedirect("/account/phones_list/")
    context["current_view_name"] = "phones_list"
    return context


def ret_context(context, form, int_numb, formset_number, formset_group, formset_extnumber):
    if int_numb != '':
        context["int_numb"] = int_numb
        context["list_int_numb"] = int_numb.strip(",").split(",")
    context["formset_number"] = formset_number
    context["formset_group"] = formset_group
    context["formset_extnumber"] = formset_extnumber
    context["form"] = form
    context["current_view_name"] = "phones_list"
    return context

def check_for_error_edit(var, query, id_list):
    nameall = []
    error3 = TelNumbersListNumbers.objects.filter(Q(telnumber__tel_number=var) & query).exclude(telnumberslist_id=id_list)
    error4 = TelNumbersListGroups.objects.filter(Q(group__numbers__tel_number=var) & query).exclude(telnumberslist_id=id_list)
    error5 = TelNumbersListExtNumbers.objects.filter(Q(extnumber__phone_numbers_group__numbers__tel_number=var) & query).exclude(telnumberslist_id=id_list)
    if error3:
        for x in error3:
            type_call = 1 if x.type_in else 2
            id_type = x.type_in if x.type_in else x.type_out
            nameall.append({'id':x.telnumberslist.id, 'name':x.telnumberslist.name, 'type_call':type_call, 'id_type':id_type})
    if error4:
        for x in error4:
            type_call = 1 if x.type_in else 2
            id_type = x.type_in if x.type_in else x.type_out
            nameall.append({'id':x.telnumberslist.id, 'name':x.telnumberslist.name, 'type_call':type_call, 'id_type':id_type})
    if error5:
        for x in error5:
            type_call = 1 if x.type_in else 2
            id_type = x.type_in if x.type_in else x.type_out
            nameall.append({'id':x.telnumberslist.id, 'name':x.telnumberslist.name, 'type_call':type_call, 'id_type':id_type})
    return nameall

def check_for_error_new(var, query):
    nameall = []
    error3 = TelNumbersListNumbers.objects.filter(Q(telnumber__tel_number=var) & query)
    error4 = TelNumbersListGroups.objects.filter(Q(group__numbers__tel_number=var) & query)
    error5 = TelNumbersListExtNumbers.objects.filter(Q(extnumber__phone_numbers_group__numbers__tel_number=var) & query)
    if error3:
        for x in error3:
            type_call = 1 if x.type_in else 2
            id_type = x.type_in if x.type_in else x.type_out
            nameall.append({'id':x.telnumberslist.id, 'name':x.telnumberslist.name, 'type_call':type_call, 'id_type':id_type})
    if error4:
        for x in error4:
            type_call = 1 if x.type_in else 2
            id_type = x.type_in if x.type_in else x.type_out
            nameall.append({'id':x.telnumberslist.id, 'name':x.telnumberslist.name, 'type_call':type_call, 'id_type':id_type})
    if error5:
        for x in error5:
            type_call = 1 if x.type_in else 2
            id_type = x.type_in if x.type_in else x.type_out
            nameall.append({'id':x.telnumberslist.id, 'name':x.telnumberslist.name, 'type_call':type_call, 'id_type':id_type})
    return nameall

def get_query(form, type_call):
    query = Q()
    if type_call == '1':
        id_type = form.cleaned_data['type_in']
        if id_type == '1':
            query &= Q(type_in=2)
        else:
            query &= Q(type_in=1)
    else:
        id_type = form.cleaned_data['type_out']
        if id_type == '1':
            query &= Q(type_out=2)
        else:
            query &= Q(type_out=1)
    return query, id_type

def create_group_number_extnumber(gr, q, ext, type_call, group, id_type):
    for k in gr:
        if type_call == '1':
            group.telnumberslistgroups_set.create(group_id=k.id, type_in=id_type)
        else:
            group.telnumberslistgroups_set.create(group_id=k.id, type_out=id_type)
    for x in q:
        if type_call == '1':
            group.telnumberslistnumbers_set.create(telnumber_id=x.id, type_in=id_type)
        else:
            group.telnumberslistnumbers_set.create(telnumber_id=x.id, type_out=id_type)
    for e in ext:
        if type_call == '1':
            group.telnumberslistextnumbers_set.create(extnumber_id=e.id, type_in=id_type)
        else:
            group.telnumberslistextnumbers_set.create(extnumber_id=e.id, type_out=id_type)

def get_notifications(name, tel_number):
    s = ''
    for one in name:
        ttt=[]
        ttt.append("return OpenInNewTab('/account/phones_list/fix/edit/" + str(one['id']) + "/" + str(one['type_call']) + "/?call=" + str(one['id_type']) + "');")
        for t in ttt:
            s += '<a href="%(link)s" onclick="%(onclick)s">%(name)s</a> ' % {"link": "#", "onclick": t, "name": one['name']}
        sttt = _(u'Ошибка! Номер %s уже задействован в списке противоположного типа - %s ' % (tel_number, s))
    return sttt

@login_required
@render_to('list_number_add.html')
def groups_list_add(request):
    """
        Новый список
    """
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    profile = request.user.get_profile()
    context["title"] = _(u"Создание нового списка")

    #ArticleFormSet = formset_factory(ListNumberDynForm)

    model = TelNumbersList()
    xString = ''
    if profile.billing_account.phones:
        context["have_numbers"] = True
    else:
        context["have_numbers"] = False

    bac = []
    bac.append(profile.billing_account)
    numbers = []
    for ww in BillserviceAccount.objects.filter(assigned_to = profile.billing_account_id):
        bac.append(ww)
    for ba in bac:
        for qq in TelNumber.objects.filter(account = ba):
            numbers.append(qq)
    existing_groups = TelNumbersGroup.objects.filter(account = profile.billing_account_id)
    extnumbers = ExternalNumber.objects.filter(account=profile.billing_account_id)
    int_numb = ''
    ArticleFormSetGroup = formset_factory(GroupDynForm)
    ArticleFormSetGroup.form = staticmethod(curry(GroupDynForm, existing_groups=existing_groups))
    ArticleFormSetNumber = formset_factory(NumberDynForm)
    ArticleFormSetNumber.form = staticmethod(curry(NumberDynForm, numbers=numbers))
    ArticleFormSetExtNumber = formset_factory(ExtNumberDynForm)
    ArticleFormSetExtNumber.form = staticmethod(curry(ExtNumberDynForm, extnumbers=extnumbers))
    if not request.POST:
        formset_number = ArticleFormSetNumber(prefix='number')
        formset_group = ArticleFormSetGroup(prefix='group')
        formset_extnumber = ArticleFormSetExtNumber(prefix='extnumber')
        form = ListNumberForm(model = model, profile = profile, request = request)
    else:
        int_numb = request.POST.get("int_numb")
        one_field = False
        formset_number = ArticleFormSetNumber(request.POST, prefix='number')
        formset_group = ArticleFormSetGroup(request.POST, prefix='group')
        formset_extnumber = ArticleFormSetExtNumber(request.POST, prefix='extnumber')
        form = ListNumberForm(model = model, data = request.POST, profile = profile, request = request)
        if form.is_valid():                 # если форма верная
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
                    print xString
                    for num in xString.split(","):
                        print "sss: %s" % num
                        save_model_list_number(model.id, num, profile)

                try:
                    group = TelNumbersList.objects.get(billing_account_id = profile.billing_account_id, id = model.id)
                except TelNumbersList.DoesNotExist:
                    raise Http404

                create_group_number_extnumber(gr, q, ext, type_call, group, id_type)

                request.notifications.add(_(u"Список успешно сохранен"), "success")
                return HttpResponseRedirect("/account/phones_list/") # перейти на страницу со списком
            else:
                return ret_context(context, form, int_numb, formset_number, formset_group, formset_extnumber)
    return ret_context(context, form, int_numb, formset_number, formset_group, formset_extnumber)


@login_required
@render_to('list_number_fix.html')
def groups_list_fixedit(request, id_type, id_list):
    """
        Редактирование
    """
    context = {}
    profile = request.user.get_profile()
    if not profile or profile.is_card:
        raise Http404

    try:
        model = TelNumbersList.objects.get(billing_account_id=profile.billing_account_id, id=id_list)
    except TelNumbersList.DoesNotExist, e:
        raise Http404
    model_number_detail = TelNumbersListDetailNumbers.objects.filter(telnumberslist = model.id)
    model_number = TelNumbersListNumbers.objects.filter(telnumberslist = model.id)
    model_group = TelNumbersListGroups.objects.filter(telnumberslist = model.id)
    model_extnumber = TelNumbersListExtNumbers.objects.filter(telnumberslist = model.id)

    model_number_detail_list = []
    model_number_list = []
    model_extnumber_list = []
    model_group_list = []
    for x in model_number_detail:
        model_number_detail_list.append(x.number)

    for x in model_number:
        model_number_list.append({'number_dyn':x.telnumber_id})
    if not model_number:
        model_number_list.append({'number_dyn':0})

    for x in model_group:
        model_group_list.append({'group':x.group_id})
    if not model_group:
        model_group_list.append({'group':0})

    for x in model_extnumber:
        model_extnumber_list.append({'extnumber':x.extnumber_id})
    if not model_extnumber:
        model_extnumber_list.append({'extnumber':0})

    ArticleFormSet = formset_factory(ListNumberDynForm,extra=0)

    xString = ''

    try:
        type_call = request.GET['call']
    except:
        type_call = request.POST.get("call_type")

    context = {}
    bac = []
    check_other_list_number = []
    bac.append(profile.billing_account)
    numbers = []
    for ww in BillserviceAccount.objects.filter(assigned_to = profile.billing_account_id):
        bac.append(ww)
    for ba in bac:
        for qq in TelNumber.objects.filter(account = ba):
            numbers.append(qq)
    existing_groups = TelNumbersGroup.objects.filter(account = profile.billing_account_id)
    extnumbers = ExternalNumber.objects.filter(account=profile.billing_account_id)
    try:
        group = TelNumbersList.objects.get(billing_account_id = profile.billing_account_id, id = int(id_list))
    except TelNumbersList.DoesNotExist:
        raise Http404
    context["title"] = _(u"""Редактирование списка "%s" """ % group.name)
    context["edit"] = True
    context["call_type"] = type_call
    int_numb = ''
    ArticleFormSetGroup = formset_factory(GroupDynForm,extra=0)
    ArticleFormSetGroup.form = staticmethod(curry(GroupDynForm, existing_groups=existing_groups))
    ArticleFormSetNumber = formset_factory(NumberDynForm,extra=0)
    ArticleFormSetNumber.form = staticmethod(curry(NumberDynForm, numbers=numbers))
    ArticleFormSetExtNumber = formset_factory(ExtNumberDynForm,extra=0)
    ArticleFormSetExtNumber.form = staticmethod(curry(ExtNumberDynForm, extnumbers=extnumbers))

    if request.POST:
        if request.POST.get("save"):  # если нажали Submit а не Cancel
            int_numb = request.POST.get("int_numb").strip(",").split(",")
            one_field = False
            formset_number = ArticleFormSetNumber(request.POST, prefix='number')
            formset_group = ArticleFormSetGroup(request.POST, prefix='group')
            formset_extnumber = ArticleFormSetExtNumber(request.POST, prefix='extnumber')
            form2 = ListNumberForm(model = model, data = request.POST, profile = profile, request = request)
            if form2.is_valid():                 # если форма верная
                model = form2.ok_model
                if model:
                    ## проверка файла со списком номеров
                    if form2.cleaned_data['file_text']:
                        try:
                            if request.FILES['file_text']:
                                xString = request.FILES['file_text'].read()
                                cifri = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ',']
                                for i in xString:
                                    if i not in cifri:
                                        raise
                        except Exception, e:
                            request.notifications.add(_(u"Не правильно заполнен файл со списком номеров"), "error")
                            return ret_context(context, form2, int_numb, formset_number, formset_group, formset_extnumber)
                    else:
                        if int_numb == '':
                            context['error'] = True
                            request.notifications.add(_(u"Ошибка. Добавьте хотя бы один номер в пункте 3"), "error")
                            return ret_context(context, form, int_numb, formset_number, formset_group, formset_extnumber)
                else:
                    return ret_context(context, form2, int_numb, formset_number, formset_group, formset_extnumber)

            #########################
            q = []
            if formset_number.is_valid():
                ids = [int(form_set_number.cleaned_data['number_dyn']) for form_set_number in formset_number.forms]
                for num in numbers:
                    for id in ids:
                        if num.id == id:
                            q.append(num)

            gr = []
            if formset_group.is_valid():
                ids = [int(form_set_group.cleaned_data['group']) for form_set_group in formset_group.forms]
                for grp in existing_groups:
                    for id in ids:
                        if grp.id == id:
                            gr.append(grp)

            ext = []
            if formset_extnumber.is_valid():
                ids = [int(form_set_extnumber.cleaned_data['extnumber']) for form_set_extnumber in formset_extnumber.forms]
                for ex in extnumbers:
                    for id in ids:
                        if ex.id == id:
                            ext.append(ex)

            if q == gr == ext == []:
                context['error_in_4'] = True
                request.notifications.add(_(u"Выберите внутренний или городской номер, или группу"), "error")
                return ret_context(context, form2, int_numb, formset_number, formset_group, formset_extnumber)

            type_call = form2.cleaned_data['type_out_in']
            query, id_type = get_query(form2, type_call)

            for m in ext:
                for x in m.phone_numbers_group.numbers.all():
                    name = check_for_error_edit(x, query, id_list)
                    if name:
                        sttt = get_notifications(name, x)
                        request.notifications.add(
                            mark_safe(sttt),
                            "error"
                        )
                        #request.notifications.add(_(u"Номер %s уже задействован в списке противоположного типа: %s" % (x, ', '.join(name),)), "error")
                        return ret_context(context, form2, int_numb, formset_number, formset_group, formset_extnumber)

            for k in gr:
                for l in k.numbers.all():
                    name = check_for_error_edit(l, query, id_list)
                    if name:
                        sttt = get_notifications(name, l)
                        request.notifications.add(
                            mark_safe(sttt),
                            "error"
                        )
                        #request.notifications.add(_(u"Номер %s уже задействован в списке противоположного типа: %s" % (l, ', '.join(name),)), "error")
                        return ret_context(context, form2, int_numb, formset_number, formset_group, formset_extnumber)

            for x in q:
                name = check_for_error_edit(x, query, id_list)
                if name:
                    sttt = get_notifications(name, x.tel_number)
                    request.notifications.add(
                        mark_safe(sttt),
                        "error"
                    )
                    #request.notifications.add(_(u"Номер %s уже задействован в списке противоположного типа: %s" % (x.tel_number, ', '.join(name),)), "error")
                    return ret_context(context, form2, int_numb, formset_number, formset_group, formset_extnumber)

            group.telnumberslistgroups_set.all().delete()
            group.telnumberslistnumbers_set.all().delete()
            group.telnumberslistextnumbers_set.all().delete()

            model.billing_account_id = profile.billing_account_id
            try:
                model.save()
            except Exception, e:
                print e

            if id_list:
                old_number = TelNumbersListDetailNumbers.objects.filter(telnumberslist_id=model.id)
                for numb in old_number:
                    numb.delete()

            if not one_field:
                for numb in request.POST.get("int_numb").strip(",").split(","):
                    save_model_list_number(model.id, numb, profile)

            if xString != '':
                for num in xString.split(","):
                    save_model_list_number(model.id, num, profile)

            create_group_number_extnumber(gr, q, ext, type_call, group, id_type)

            request.notifications.add(_(u"Связь успешно отредактирована"), "success")
        return HttpResponseRedirect("/account/phones_list/")
    else:
        print model_number_detail_list
        context['model_number_detail_list'] = model_number_detail_list
        formset_number = ArticleFormSetNumber(initial = model_number_list, prefix='number')
        formset_group = ArticleFormSetGroup(initial = model_group_list, prefix='group')
        formset_extnumber = ArticleFormSetExtNumber(initial = model_extnumber_list, prefix='extnumber')
        form2 = ListNumberForm(model = model, profile = profile, request = request, id_type = id_type)
    return ret_context(context, form2, int_numb, formset_number, formset_group, formset_extnumber)