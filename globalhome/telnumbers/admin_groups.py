# coding: utf-8
from django.contrib import admin
from account.admin import CustomerAccount as User
from django.utils.translation import ugettext_lazy as _
from lib.decorators import render_to
from telnumbers.models import TelNumbersGroup, TelNumber
from django.conf.urls import patterns, url, include
from django.http import Http404, HttpResponseRedirect
from lib.http import get_query_string
from lib.paginator import SimplePaginator
from telnumbers.forms import EditTelNumbersGroupForm
import log
from django.contrib.admin.views.decorators import staff_member_required

def get_ready_context(request, title):
    context = {}
    context["request"] = request
    context["user"] = request.user
    context["title"] = title
    context["is_popup"] = True if (request.GET and request.GET.get("_popup")) else False
    context["csrf_token"] = request.COOKIES.get("csrftoken")
    context["app_label"] = "telnumbers"
    context["app_section"] = _(u"Groups numbers")
    context["language"] = "ru" 
    return context

@staff_member_required
@render_to("admin/groups/list_groups.html")
def list_groups_view(request):
    "Отображает список юридических пользователей со ссылками на редактирование их групп"
    context = get_ready_context(request, _(u"User's groups"))
    users = User.objects.filter(profile__is_juridical = True, is_staff = False)
    query = get_query_string(request, exclude = ("page",))
    paginator = SimplePaginator(users, 50, "?page=%%s&%s" % query)
    paginator.set_page(request.GET.get("page", 1))
    paginator.Total = users.count()
    users = paginator.get_page()         
    context["paginator"] = paginator
    context["users"] = users
    return context
    
@staff_member_required
@render_to("admin/groups/list_user_groups.html")
def list_user_groups(request, user_id):
    "Отображает список групп указанного пользователя для их редактирования"
    context = get_ready_context(request, _(u"User's groups"))
    try:
        user = User.objects.get(id = user_id)
    except Exception, e:
        log.add("Exception 1 in telnumbers.admin_groups.TelNumbersGroupAdmin.list_user_groups: '%s'" % e)
        raise Http404
    profile = user.get_profile()
    if not profile.is_juridical:
        raise Http404
    context["target_user"] = user
    bac = profile.billing_account
    groups = TelNumbersGroup.objects.filter(account = bac)
    context["groups"] = groups
    return context

@staff_member_required
@render_to("admin/groups/edit_group.html")
def edit_group(request, group_id):
    "Редактирование выбранной группы"
    context = get_ready_context(request, _(u"Edit group"))
    try:
        group = TelNumbersGroup.objects.get(id = group_id)
    except Exception, e:
        log.add("Exception 1 in telnumbers.admin_groups.TelNumbersGroupAdmin.edit_group: '%s'" % e)
        raise Http404
    bac = group.account
    try:
        user = User.objects.get(username = bac.username)
    except Exception, e:
        log.add("Exception 2 in telnumbers.admin_groups.TelNumbersGroupAdmin.edit_group: '%s'" % e)
        raise Http404
    context["target_user"] = user
    profile = user.get_profile()
    if not profile.is_juridical:
        raise Http404
    try:
        numbers = TelNumber.objects.filter(account = bac)
        existing_groups = TelNumbersGroup.objects.filter(account = bac)
    except Exception, e:
        log.add("Exception 3 in telnumbers.admin_groups.TelNumbersGroupAdmin.edit_group: '%s'" % e)
        raise e
    if request.POST:
        form = EditTelNumbersGroupForm(request.POST.copy(), numbers = numbers, existing_groups = existing_groups, group = group)
        # а вот тут уже валидация и основные действия с данными
        if request.POST.get("save"):
            if form.is_valid():
                data = form.cleaned_data
                # изменяем группу
                ids = [int(item) for item in data["numbers"]]
                numbers = numbers.filter(id__in = ids)
                group.set_data(data["name"], numbers)
                # а потом
                request.notifications.add(_(u"Group was saved succesfully"), "success")
        return HttpResponseRedirect("../../user_groups/%s/" % user.id)
    else:
        form = EditTelNumbersGroupForm(group = group, numbers = numbers, existing_groups = existing_groups)
    context["form"] = form
    context["group"] = group
    return context

@staff_member_required
@render_to("admin/groups/delete_group.html")
def delete_group(request, group_id):
    "Удаление выбранной группы"
    context = get_ready_context(request, _(u"Delete group"))
    try:
        group = TelNumbersGroup.objects.get(id = group_id)
    except Exception, e:
        log.add("Exception 1 in telnumbers.admin_groups.TelNumbersGroupAdmin.delete_group: '%s'" % e)
        raise Http404
    context["group"] = group
    bac = group.account
    try:
        user = User.objects.get(username = bac.username)
    except Exception, e:
        log.add("Exception 2 in telnumbers.admin_groups.TelNumbersGroupAdmin.edit_group: '%s'" % e)
        raise Http404
    context["target_user"] = user
    profile = user.get_profile()
    if not profile.is_juridical:
        raise Http404
    context["numbers"] = group.numbers.all()
    if request.POST:
        if request.POST.get("delete"):
            group.delete()
            request.notifications.add(_(u"Group was succesfully deleted"), "success")
        return HttpResponseRedirect("../../user_groups/%s/" % user.id)
    return context

@staff_member_required
@render_to("admin/groups/add_group.html")
def add_group(request, user_id):
    "Добавление новой группы"
    try:
        user = User.objects.get(id = user_id)
    except Exception, e:
        log.add("Exception 1 in telnumbers.admin_groups.TelNumbersGroupAdmin.add_group: '%s'" % e)
        raise Http404
    context = get_ready_context(request, _(u"Add group for user %s") % user)
    profile = user.get_profile()
    if not profile.is_juridical:
        raise Http404
    bac = profile.billing_account
    try:
        numbers = TelNumber.objects.filter(account = bac)
        existing_groups = TelNumbersGroup.objects.filter(account = bac)
    except Exception, e:
        log.add("Exception 2 in telnumbers.views.group_add: '%s'" % e)
        raise e
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
                request.notifications.add(_(u"Group was created succesfully"), "success")
        return HttpResponseRedirect("../../user_groups/%s/" % user.id)
    else:
        form = EditTelNumbersGroupForm(numbers = numbers, existing_groups = existing_groups)
    context["form"] = form
    context["target_user"] = user
    return context



class TelNumbersGroupAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super(TelNumbersGroupAdmin, self).get_urls()
        my_urls =  patterns("",
            url("^$", list_groups_view),
            url("^user_groups/(?P<user_id>\d+)/$", list_user_groups),
            url("^edit_group/(?P<group_id>\d+)/$", edit_group),
            url("^delete_group/(?P<group_id>\d+)/$", delete_group),
            url("^add_group/(?P<user_id>\d+)/$", add_group),
        )
        return my_urls + urls






