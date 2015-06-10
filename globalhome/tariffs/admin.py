# coding: utf-8
import os
import locale

from django.views.decorators.csrf import csrf_exempt
from django.core.context_processors import csrf
from optparse import OptionParser
from django.contrib import admin
from tariffs.models import TelZoneGroup, TelZone, TelCode, TariffGroup, Tariff, UploadTariffs, tuts
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from django.forms import fields
from django.forms.widgets import SelectMultiple
from billing.models import BillserviceAccount
# from django.contrib.admin.filterspecs import FilterSpec, ChoicesFilterSpec, BooleanFieldFilterSpec
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from lib.decorators import render_to, login_required
import settings
# import datetime,time
from time import gmtime, strftime, localtime
from django.db import models


csrf_protect_m = method_decorator(csrf_protect)

class TelZoneGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "var_slug", "id")
    search_fields = ("name",)

class TelZoneAdmin(admin.ModelAdmin):
    list_display = ("group", "name", "ru_RU", "id")
    list_display_links = ("group", "name")
    ordering = ("name", "id")
    search_fields = ("name", "ru_RU")
    list_filter = ("group",)
    actions = ["change_telzone_group"]

    def change_telzone_group(self, request, queryset):
        """
            Админское действие - массовая смена группы телефонной зоны у выбранных зон
        """
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect("/change_telzone_group/?ids=%s" % ",".join(selected))
    change_telzone_group.short_description = _(u"Change telzone group for selected telzones")


class TelCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "tel_zone", "id")
    list_display_links = ("tel_zone", "code")
    ordering = ("tel_zone", "code")
    search_fields = ("code", "tel_zone__name", "tel_zone__ru_RU")

class TariffGroupAdmin(admin.ModelAdmin):
    """
        Это администратор модели биллинговой группы
        !!!!!! изменить шаблон подтверждения удаления группы, чтобы там было написано, что
        все пользователи этой группы будут переключены на группу default !!!!!!!
    """
    list_display = ("group_name", "id")
    actions = None
    ordering = ("group_name",)

    def has_delete_permission(self, request, obj=None):
        """
            Тут я проверяю, чтобы не удалили первую группу (default)
        """
        if obj:
            if obj.id == 1:
                return False
        return super(TariffGroupAdmin, self).has_delete_permission(request, obj=obj)

class TariffAdmin(admin.ModelAdmin):
    list_display = ("billing_group", "tel_zone", "price", "get_start_date", "get_end_date", "is_active")
    ordering = ("tel_zone", "billing_group", "start_date", "end_date")
    actions = None
    exclude = ("is_active",)

    change_form_template = r"admin/tariffs/edit.html"

    list_filter = (
        "billing_group",  # !!!!!!!!! в будущем возможно прийдется убрать, если групп будет много
        "is_active",
        "start_date",
        "end_date"
    )

    def has_delete_permission(self, request, obj=None):
        """
            Запрещено удалять тарифы через админку!
        """
        return False

    def get_form(self, request, obj=None, **kwargs):
        """
            Тут я получаю форму, которую мне сделала админка и насильно впихиваю в нее еще одно поле
        """
        if obj:
            # делаем форму нередактируемой, если приказали редактировать существующий, а не добавить новый тариф
            self.readonly_fields = ["billing_group", "tel_zone", "price", "get_start_date", "get_end_date", "is_active"]
            form = super(TariffAdmin, self).get_form(request, obj=obj, **kwargs)

            del form.base_fields["start_date"]
            del form.base_fields["end_date"]

        else:
            self.readonly_fields = []
            form = super(TariffAdmin, self).get_form(request, obj=obj, **kwargs)

            choices = []
            for ch in form.base_fields["billing_group"].choices:
                if ch[0] != str(u""):
                    choices += [ch]

            form.base_fields["billing_group"].choices = choices

        return form


class UploadTariffsAdmin(admin.ModelAdmin):
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def queryset(self, request):
        return []

    META = {}  # это нужно
    notifications = {}  # и это нужно

    @csrf_protect_m
    @render_to("admin/tariffs/csv_upload_form.html")
    def changelist_view(self, request, extra_context=None):
        """
            Это я тут перекрываю view-функцию отображения списка объектов.
            Вот какраз тут должно быть отображение приглашения загрузить CSV файл с тарифами

            !!!!!!!хотя наверно не очень хорошо тут (в admin.py) помещать view-логику!!!!!!!
        """
        context = {}
        context["request"] = request
        context["user"] = request.user
        context["title"] = _(u"Upload tariffs from CSV file")
        context["csrf_token"] = request.COOKIES.get("csrftoken")
        context["app_label"] = UploadTariffs._meta.app_label
        context["app_section"] = UploadTariffs._meta.verbose_name_plural

        from forms import UploadTariffsForm

        errors = []
        warnings = []
        messages = []

        if request.method == "POST":
            form = UploadTariffsForm(request.POST, request.FILES)
            start_time = datetime.now()
            result_str = ""
            if form.is_valid():
                try:
                    try:
                        file = request.FILES["file"]

                        # !!!!!!!! а вот тут я вручную буду сохранять этот файл, хотя вроде это не очень хорошая идея
                        # (всмысле должен быть какой-то другой способ сделать это дело)
                        # а хотя может так и нужно...

                        fname = settings.TARIF_ROOT + os.sep + \
                            str(strftime("tariffs_csv" + os.sep + "%Y%m%d_%H%M%S_BY_%%s-%%s", localtime())) % (request.user, file.name)

                        sf = open(fname, "wb")
                        for chunk in file.chunks():
                            sf.write(chunk)
                        sf.close()

                    except Exception, e:
                        request.notifications.add(_(u"Error uploading file!"), "error")
                        raise e

                    def get_add_notifications(parser):
                        "извлекает сообщения/ошибки/ворнинги из парсера"
                        if parser.errors:
                            s = ""
                            for msg in parser.errors:
                                s += msg + "<br />"
                            errors.extend(parser.errors)
                            parser.errors = []
                        if parser.warnings:
                            s = ""
                            for msg in parser.warnings:
                                s += msg + "<br />"
                            warnings.extend(parser.warnings)
                            parser.warnings = []
                        if parser.messages:
                            s = ""
                            for msg in parser.messages:
                                s += msg + "<br />"
                            messages.extend(parser.messages)
                            parser.messages = []


                    # а вот тут мы распарсиваем этот файл
                    from csv_parse_tariffs import CSVTariffParser

                    replace_zone_names = False
                    if form.cleaned_data.get("replace_zone_names") == "True":
                        replace_zone_names = True
                    replace_existing_tariffs = False
                    if form.cleaned_data.get("replace_existing_tariffs") == "True":
                        replace_existing_tariffs = True
                    autocreate_codes_and_zones = False
                    if form.cleaned_data.get("autocreate_codes_and_zones") == "True":
                        autocreate_codes_and_zones = True
                    ignore_missing_zones = False
                    if form.cleaned_data.get("ignore_missing_zones") == "True":
                        ignore_missing_zones = True
                    add_mobile_codes = False
                    if form.cleaned_data.get("add_mobile_codes") == "True":
                        add_mobile_codes = True

                    # создаю мой парсер
                    parser = CSVTariffParser(
                        fname,
                        int(form.cleaned_data["billing_group"]),
                        replace_zone_names,
                        replace_existing_tariffs,
                        autocreate_codes_and_zones,
                        ignore_missing_zones,
                        add_mobile_codes
                    )
                    parser.ParseCSVFile()
                    get_add_notifications(parser)
                    if not parser.had_stop:
                        parser.ParseData()
                        get_add_notifications(parser)
                        if not parser.had_stop:
                            parser.CalculateChanges()
                            get_add_notifications(parser)
                            if not parser.had_stop:
                                parser.ApplyChanges()
                                get_add_notifications(parser)


                except Exception, e:
                    e_str = _(u"Exception! %s").__unicode__()
                    e_str = e_str % e
                    request.notifications.add(e_str, "error")
                else:
                    if not parser.had_stop:
                        result_str = _(u"File succesfully uploaded and inserted to database").__unicode__() + "<br>"

            total_time = datetime.now() - start_time
            result_str += (_(u"Total time: %s").__unicode__()) % total_time
            request.notifications.add(result_str, "success")
        else:
            form = UploadTariffsForm()

        def HtmlLine(s):
            if str(type(s)) == "<type 'unicode'>" or str(type(s)) == "<type 'str'>":
                return "<li>" + unicode(s) + "</li>"
            else:
                return "<li>" + s.__unicode__() + "</li>"


        if errors:
            s = "<ul>"
            for msg in errors:
                s += HtmlLine(msg)
            if parser.err_count:
                s += HtmlLine((_(u"Errors total: %s").__unicode__()) % parser.err_count)
            s += "</ul>"
            request.notifications.add(s, "error")
        if warnings:
            s = "<ul>"
            for msg in warnings:
                s += HtmlLine(msg)
            if parser.warn_count:
                s += HtmlLine((_(u"Warnings total: %s").__unicode__()) % parser.warn_count)
            s += "</ul>"
            request.notifications.add(s, "warning")
        if messages:
            s = "<ul>"
            for msg in messages:
                s += HtmlLine(msg)
            if parser.msg_count:
                s += HtmlLine((_(u"Messages total: %s").__unicode__()) % parser.msg_count)
            s += "</ul>"
            request.notifications.add(s, "success")

        context["form"] = form
        if extra_context:
            context.update(extra_context)

        return context

admin.site.register(TelZoneGroup, TelZoneGroupAdmin)
admin.site.register(TelZone, TelZoneAdmin)
admin.site.register(TelCode, TelCodeAdmin)
admin.site.register(TariffGroup, TariffGroupAdmin)
admin.site.register(Tariff, TariffAdmin)
admin.site.register(UploadTariffs, UploadTariffsAdmin)



