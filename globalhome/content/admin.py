# coding: utf-8
from django.contrib import admin
from content.models import Article, News, ButtonPanelHref, ButtonPanelUrls
from treeadmin.admin import TreeAdmin
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from content import BaseContentAdmin

from models import *
from django.views.decorators.csrf import csrf_protect
from lib.decorators import render_to, login_required
from django.utils.decorators import method_decorator
csrf_protect_m = method_decorator(csrf_protect)
from lib.ModelColumnsManager import ColumnsManager
from billing.forms import *
import settings, os, log
from content import AV_COLUMNS
from lib.http import get_query_string
from django.db import connections, transaction

class TextContentAdmin(BaseContentAdmin):
    actions = []

class ArticleAdmin(TextContentAdmin):
    list_display = ('id', 'name', 'show_inner_url')
    list_display_links = ('name',)
    tree_display_replace = (('name', 'tree_name',), ('path', None), (None, 'tree_actions'))

    def show_inner_url(self, obj):
        if obj.slug:
#            url_name = 'article_by_slug'
            var = obj.slug
        else:
#            url_name = 'article'
            var = obj.id
        return '/content/article/%s/' % var
#        return reverse(url_name, args=[var])
    show_inner_url.short_description = _(u"URL on site")

class ArticleMoscowAdmin(TextContentAdmin):
    list_display = ('id', 'name', 'show_inner_url')
    list_display_links = ('name',)
    tree_display_replace = (('name', 'tree_name',), ('path', None), (None, 'tree_actions'))

    def show_inner_url(self, obj):
        if obj.slug:
#            url_name = 'moscow_article_by_slug'
#            var.append(obj.prefix)
            var = obj.slug
        else:
#            url_name = 'article'
            var = obj.id
        return '/%s/%s/' % (obj.prefix, var)
#        return reverse(url_name, args=var)
    show_inner_url.short_description = _(u"URL on site")


class NewsAdmin(TextContentAdmin):
    list_display = ('name', 'created_by', 'created_at', 'is_published')
    list_filter = ('created_at', 'is_published')

class PrefixAdmin(admin.ModelAdmin):
    pass



# class CheckAdmin(admin.ModelAdmin):
#    list_display = ["created_by", "created_at", "modified_at", "name", "text"]
#
#    actions = None
#
#    def has_add_permission(self, request):
#        return False
#
#    def has_delete_permission(self, request, obj=None):
#        return False
#
#    def queryset(self, request):
#        return []
#
#    META = {}
#    notifications = {}
#
#    @csrf_protect_m
#    @render_to("admin/check_list.html")
#    def changelist_view(self, request, extra_context=None):
#        context = {}
#        context["request"] = request
#        context["user"] = request.user
#        context["title"] = _(u"Billed calls")
#        context["csrf_token"] = request.COOKIES.get("csrftoken")
#        context["app_label"] = "billing"
#        context["app_section"] = _(u"Billed calls")
#        context["language"] = "ru"
#
#        self.user = request.user
#
#        sort = request.GET.get("sort")
#        order = request.GET.get("order")
#
#
#        '''
#        if sort and order:
#            colman = ColumnsManager(Check, using = settings.GLOBALHOME_DB2, sort = int(sort), order = order)
#        else:
#            colman = ColumnsManager(Check, using = settings.GLOBALHOME_DB2)
#        print colman.items
#        '''
#        if 'filter' in request.GET:
#            form = AdminBilledCallsFilter(request.GET)
#        else:
#            form = AdminBilledCallsFilter()
#            date_from = first_date()
#            date_to = last_date()
#            caller_number = ""
#            called_number = ""
#            account_id = 0
#            called_account_id = 0
#            length_choice = 0
#            check_choice = 0
#
#        if form.is_valid():
#            date_from = form.cleaned_data["date_from"]
#            date_to = form.cleaned_data['date_to']
#            if date_from and date_to:
#                if date_from > date_to:
#                    request.notifications.add(_(u"You have selected an incorrect date interval!"), "warning")
#            if date_to:
#                date_to += timedelta(days = 1)
#            caller_number = form.cleaned_data['caller_number']
#            called_number = form.cleaned_data['called_number']
#            account_id = int(form.cleaned_data["account1"])
#            check_choice = int(form.cleaned_data["check_choice"])
#            print check_choice
#
#        def double_proc(s):
#            res = ""
#            for i in xrange(len(s)):
#                if s[i] == "*":
#                    res += "%%"
#                else:
#                    res += s[i]
#            return res
#
#        where = ""
#        cur2 = connections[settings.GLOBALHOME_DB2].cursor()
#
#        if date_from or date_to or account_id or check_choice:
#
#            if date_from:
#                where += "created_at >= '%s'" % date_from
#
#            if date_to:
#                if where: where += " AND "
#                where += "created_at <= '%s'" % date_to
#
#            if account_id:
#                if where: where += " AND "
#                where += "created_by_id = %s" % account_id
#                print where
#            if check_choice:
#                if check_choice == 1:
#                    if where: where += " AND "
#                    where += "type = '%s'" % 'check'
#                if check_choice == 2:
#                    if where: where += " AND "
#                    where += "type = '%s'" % 'invoice'
#                if check_choice == 3:
#                    if where: where += " AND "
#                    where += "type = '%s'" % 'act'
#
#            cur2.execute("SELECT content_check.id, content_check.created_at, content_check.type, content_check.name, auth_user.username, content_check.sent, content_check.number FROM content_check JOIN auth_user on(content_check.created_by_id = auth_user.id) WHERE %s;"% (where,))
#        else:
#            cur2.execute("SELECT * FROM content_check;",)
#
#
#        check = cur2.fetchall()
#        context["for_check"] = check
#        selected_columns = request.session.get("billservice_phonetransaction_selected_columns")
#
#
#
#        context["form"] = form
#
#        if extra_context:
#            context.update(extra_context)
#
#        return context
#
#    class Meta:
#        app_label = "billing"
#        verbose_name = _("Check views")
#        verbose_name_plural = _("Check views")

class HostelinformAdmin(admin.ModelAdmin):
    list_display = ('floor', 'room', 'number', 'install_date', 'password', 'ip', 'mac', 'install_name', 'settings', 'status', 'hostel_number', 'note')  # отображаем калонками
    list_display_links = ('floor', 'number',)  # какие поля доступны для изменения
    search_fields = ('floor', 'room', 'number', 'short_number', 'mac', 'ip',)  # вверху  поиск
    list_filter = ('status', 'university_name', 'install_name', 'settings')  # справа  фильтр
#    date_hierarchy = 'time' # вверху  новая панель по выбору месяца
#    ordering = ('-time',) # сартировка по дате

#    actions = ["change"] # добавляет  поле в  всплывающий список  для  редактирование  выбранных  обьектов

class Section_type_admin(admin.ModelAdmin):
    list_display = ('id', 'name', 'about')

class UrlsConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'description_action', 'description_key', 'how_much_action', 'how_much_key', 'how_to_connect_action', 'how_to_connect_key', 'where_to_go_action', 'where_to_go_key',)
    list_display_links = ('key',)
    search_fields = ('key', 'description_action', 'description_key', 'how_much_action', 'how_much_key', 'how_to_connect_action', 'how_to_connect_key', 'where_to_go_action', 'where_to_go_key',)

class ButtonPanelUrlsAdmin(admin.ModelAdmin):
    list_display = ('urls', 'key',)
    list_display_links = ('urls',)
    search_fields = ('urls', 'key',)


# admin.site.register(Hostelinform, HostelinformAdmin)
# admin.site.register(Check, CheckAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Article_moscowdata, ArticleMoscowAdmin)
admin.site.register(Prefix_article, PrefixAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(News_Moscowdata, NewsAdmin)
admin.site.register(Section_type, Section_type_admin)
admin.site.register(ButtonPanelHref, UrlsConfigAdmin)
admin.site.register(ButtonPanelUrls, ButtonPanelUrlsAdmin)




















