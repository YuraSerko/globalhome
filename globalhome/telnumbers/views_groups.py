# coding: utf-8
from django.utils.translation import ugettext_lazy as _, ugettext
from django.http import Http404, HttpResponseRedirect, HttpResponse
from lib.decorators import render_to, login_required
from models import TelNumbersGroup, TelNumber
import log
from forms import EditTelNumbersGroupForm
from django.contrib.auth.models import User
from django.db import connections, transaction
from billing.models import BillserviceAccount
from django.shortcuts import render_to_response
from django.template import RequestContext

@login_required
@render_to('groups/list.html')
def groups_list(request):
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context["title"] = _(u"Groups of numbers")
    user = request.user
    profile = user.get_profile()
    bac = profile.billing_account
    has_phones = (bac.phones.count() > 0)
    context["has_phones"] = has_phones
    context["add"] = True
    groups = None
    try:
        groups = TelNumbersGroup.objects.filter(account = bac)
    except Exception, e:
        log.add("Exception 1 in telnumbers.views.groups_list: '%s'" % e)
        raise e
    context["groups"] = groups
    context["current_view_name"] = "account_phones_groups"
    return context


@login_required
def groups_group_add(request):
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    print 'get = %s'%request.GET
    if request.GET.get('popup_window') == '1':
        context['popup_window'] = True
    else:
        context['popup_window'] = False
    context["title"] = _(u"Adding a group of numbers")
    user_id = None
    if request.GET:
        user_id = request.GET.get("user_id")
        if request.user.is_staff and user_id:
            user_id = int(user_id)
        else:
            user_id = None
    if user_id:
        user = User.objects.get(id = user_id)
        context["to_user"] = user
    else:
        user = request.user
    profile = user.get_profile()
    bac = profile.billing_account
    numbers = []
    try:
        
        numbers = TelNumber.objects.filter(account = bac)
        
        existing_groups = TelNumbersGroup.objects.filter(account = bac)
        
    except Exception, e:
        log.add("Exception 1 in telnumbers.views.group_add: '%s'" % e)
        raise e
    if request.GET:
        if request.GET.get("popup_window"):
            context["window_is_popup"] = True
    context["current_view_name"] = "account_phones_groups"
    context["has_phones"] = (numbers.count() > 0)
    
    if len(numbers)==0:
        request.notifications.add(_(u"You have no internal numbers. You should create one first"), "info")
        
        context["show"]="1"
        return render_to_response('groups/add_popup.html', context, context_instance=RequestContext(request))
    if request.POST:
                
        form = EditTelNumbersGroupForm(request.POST.copy(), numbers = numbers, existing_groups = existing_groups)
        
        # а вот тут уже валидация и основные действия с данными
        if request.POST.get("add"):
            if form.is_valid():
                data = form.cleaned_data
                # создаем группу и тд и тп
                ids = [int(item) for item in data["numbers"]]
                numbers = numbers.filter(id__in = ids)
                group = TelNumbersGroup.create(data["name"], bac, numbers)
                # а потом
                if not context['popup_window']:
                    request.notifications.add(_(u"Group was created succesfully"), "success")
                    return HttpResponseRedirect("/account/phones_groups/")
                else:
                    context["group_added_successed"] = True
                    context["added_group_id"] = group.id
                   
#                   return render_to_response('groups/add_popup.html', context, context_instance=RequestContext(request))
                    
        else:
            if context['popup_window']:
                return render_to_response('groups/add_popup.html', context, context_instance=RequestContext(request))
            else:
                return render_to_response('groups/add.html', context, context_instance=RequestContext(request))
    else:
       
        form = EditTelNumbersGroupForm(numbers = numbers, existing_groups = existing_groups, )
        
    context["form"] = form
    if context['popup_window']:
        return render_to_response('groups/add_popup.html', context, context_instance=RequestContext(request))
    else:
        return render_to_response('groups/add.html', context, context_instance=RequestContext(request))
        


@login_required
@render_to('groups/edit.html')
def groups_group_edit(request, group_id):
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context["title"] = _(u"Editing the group of numbers")
    user = request.user
    profile = user.get_profile()
    bac = []
    bac.append(profile.billing_account)
    numbers = []
    try:
        for ww in BillserviceAccount.objects.filter(assigned_to = profile.billing_account_id):
            bac.append(ww)
        for ba in bac:
            for qq in TelNumber.objects.filter(account = ba):
                numbers.append(qq)      
        existing_groups = TelNumbersGroup.objects.filter(account = profile.billing_account)
        group = TelNumbersGroup.objects.get(id = group_id)
    except Exception, e:
        log.add("Exception 1 in telnumbers.views.group_edit: '%s'" % e)
        raise e
    if group.account != bac[0]:
        raise Http404
    if request.POST:
        form = EditTelNumbersGroupForm(request.POST.copy(), numbers = numbers, existing_groups = existing_groups, group = group)
        # а вот тут уже валидация и основные действия с данными
        if request.POST.get("save"):
            if form.is_valid():
                data = form.cleaned_data
                # изменяем группу
                ids = [int(item) for item in data["numbers"]]
                q = []
                for num in numbers:
                    for id in ids:
                        print id
                        print num.id
                        if num.id == id:
                            q.append(num)   
                group.set_data(data["name"], q)
                request.notifications.add(_(u"Group was saved succesfully"), "success")
                return HttpResponseRedirect("/account/phones_groups/")
        else:
            return HttpResponseRedirect("/account/phones_groups/")
    else:
        form = EditTelNumbersGroupForm(group = group, numbers = numbers, existing_groups = existing_groups)
    context["form"] = form
    context["group"] = group
    context["current_view_name"] = "account_phones_groups"
    return context

@login_required
@render_to('groups/delete.html')
def groups_group_delete(request, group_id):
    
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context["title"] = _(u"Deleting the group of numbers")
    user = request.user
    profile = user.get_profile()
    bac = profile.billing_account
    numbers = []
    try:
        numbers = TelNumber.objects.filter(account = bac)
        group = TelNumbersGroup.objects.get(id = group_id)
    except Exception, e:
        log.add("Exception 1 in telnumbers.views.group_delete: '%s'" % e)
        raise e
    if group.account != bac:
        raise Http404
    
    if request.POST:
        if request.POST.get("delete"):
            # вот тут нужно отсоединить все городские телефоны, которые ссылаются на эту группу
            nums = list(group.externalnumber_set.all())
            for num in nums:
                num.phone_numbers_group = None
                num.save()
            group.delete()
            request.notifications.add(_(u"Group was succesfully deleted"), "success")
        return HttpResponseRedirect("/account/phones_groups/")
    context["group"] = group
    context["numbers"] = group.numbers.all()
    context["current_view_name"] = "account_phones_groups"
    return context

