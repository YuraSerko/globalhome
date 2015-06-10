# coding: utf-8
from django.contrib import admin
import log
from findocs.models import FinDoc, FinDocTemplate, FinDocSignApplication, FinDocSigned, Package_on_connection_of_service, \
                            Rules_of_drawing_up_documents, Check, Act, Invoice, Download_documents, Download_checks,Print_act
from content import BaseContentAdmin
from lib.utils import get_now
from lib.decorators import render_to, login_required
from django.contrib.admin.views.decorators import staff_member_required
from data_centr.views import add_document_in_dict_for_send, send_mail_check
import csv, datetime
from django.http import  HttpResponse
from account.models import Profile, Address
from billing.models import BillserviceSubAccount, BillserviceAccount
from django.db.models import Min
from dateutil.relativedelta import relativedelta  # @UnresolvedImport
from django.db.models import Q
from django.conf.urls import patterns, url
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.forms import ModelForm
from findocs.models import FinDocTemplate, FinDoc
from lib.transliterate import transliterate
import zipfile, shutil, os
from findocs.models import FinDocSignApplication
import datetime
from django.contrib.auth.models import User
from findocs.views import create_package
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from findocs.models import Package_on_connection_of_service
from data_centr.models import Zakazy

from django.db.models import Q

class FinDocAdmin(admin.ModelAdmin):
    list_display = ('id', "name", "type", "template", "slug")
    list_filter = ("type", "name")
    save_as = True

class FinDocTemplateAdmin(BaseContentAdmin):
    # list_display = ("name", "created_by", "created_at", "modified_at")
    # date_hierarchy = "created_at"
    # save_as = True
    pass

class FinDocSignApplicationAdmin(admin.ModelAdmin):
    list_display = ("assigned_to", "findoc", "assigned_by", "assigned_at")
    list_filter = ("findoc", "assigned_to")
    readonly_fields = ("assigned_by", "assigned_at", "findoc", "assigned_to", "user_can_cancel")
    date_hierarchy = "assigned_at"
    exclude = ("params_data",)
    search_fields = ('assigned_to__username', 'assigned_to__id')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.assigned_by = request.user
            obj.assigned_at = get_now()
        return super(FinDocSignApplicationAdmin, self).save_model(request, obj, form, change)

class FinDocSignedAdmin(admin.ModelAdmin):
    list_display = ('id', "signed_by", "findoc", "signed_at", "assigned_by")
    list_filter = ("findoc",)
    readonly_fields = ("assigned_by",)
    date_hierarchy = "signed_at"
    search_fields = ('signed_by__username',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.assigned_by = request.user
        return super(FinDocSignedAdmin, self).save_model(request, obj, form, change)

class Package_on_connection_of_service_Admin(admin.ModelAdmin):
    readonly_fields = ('id', 'user', 'url_after_sign', 'url_after_cancel', 'slugs_document', 'findoc_sign')
    list_display = ('id', 'user', 'url_after_sign', 'url_after_cancel', 'slugs_document', 'activate', 'deactivate', 'activate_admin', 'date_create', 'package_status')
    search_fields = ('user__username', 'user__id', 'data')
    list_filter = ('package_status', 'activate', 'deactivate', 'activate_admin')
    class Media:
        js = ['/media/js/package_on_connection_of_service_admin.js']
    def get_urls(self):
        urls = super(Package_on_connection_of_service_Admin, self).get_urls()
        my_urls = patterns("", ("^download_findoc_admin/$", download_findoc_admin), \
                           ("^sign_findoc_admin/$", sign_findoc_admin),)
        return my_urls + urls

#========================================================================================================
# для распечатки
@staff_member_required
@render_to("download_findoc_admin.html")
def download_findoc_admin(request):
    pack_id = request.GET['pack_id']
    package_obj = Package_on_connection_of_service.objects.get(id=pack_id)
    # находим объект User
    user_obj = User.objects.get(id=package_obj.user.id)
    # найдем id для findoc c соответствующим slugs
    findoc_obj = FinDoc.objects.get(slug='akt_priema_peredachi_oborudovaniya_spisok')
    context = {}
    now = datetime.datetime.now()
    doc = FinDocSignApplication(
                        assigned_at=now,
                        findoc=findoc_obj,
                        assigned_to=user_obj,
                        user_can_cancel=True,
                        service_for_billing="application_from_a_package")
    doc.save()
    app_text = doc.process_text(request=request, findocapp_id=doc.id)
    # удаляем заявку
    doc.delete()
    # здесь непосредственно передатеся текст договора из базы в html ку
    context["application_text"] = app_text
    # создаем документ для скачки
    text = app_text.encode('utf-8')
    f_name = transliterate(findoc_obj.name.encode('utf-8'))
    filename = "%s" % f_name + "-" + "-" + "%s" % findoc_obj.id
    out_f = open('%s.doc' % filename, 'w')
    out_f.write(text)
    out_f.close()
    gz1 = zipfile.ZipFile ('%s.zip' % filename, 'w', 8)
    gz1.write(out_f.name)
    gz1.close()
    shutil.move('%s.zip' % filename, 'media/doc/%s.zip' % filename)
    os.remove('%s.doc' % filename)
    context["display"] = filename
    return context


#=========================================================================================================
# подписать договор
@staff_member_required
@render_to("sign_findoc_admin.html")
def sign_findoc_admin(request):
    pack_id = request.GET['pack_id']
    package_obj = Package_on_connection_of_service.objects.get(id=pack_id)
    # находим объект User
    user_obj = User.objects.get(id=package_obj.user.id)
    # найдем id для findoc c соответствующим slugs
    findoc_obj = FinDoc.objects.get(slug='akt_priema_peredachi_oborudovaniya_spisok')
    context = {}
    # находим объект User
    now = datetime.datetime.now()

    doc = FinDocSignApplication(
                        assigned_at=now,
                        findoc=findoc_obj,
                        assigned_to=user_obj,
                        user_can_cancel=True,
                        service_for_billing="application_from_a_package")
    doc.save()
    app_text = doc.process_text(request=request, findocapp_id=doc.id)
    # удаляем заявку
    doc.delete()
    # здесь непосредственно передатеся текст договора из базы в html ку
    context["application_text"] = app_text
    context['pack_id'] = pack_id
    return context
#=========================================================================================================

class Rules_of_drawing_up_documents_Admin(admin.ModelAdmin):
    list_display = [f.name for f in Rules_of_drawing_up_documents._meta.fields]


@staff_member_required
@render_to("admin/check_user_view.html")
def show_check(request, arg):
    context = {}
    document = Check.objects.get(id=int(arg))
    context["document"] = document
    return context


@staff_member_required
@render_to("admin/check_user_view.html")
def show_act(request, arg):
    context = {}
    document = Act.objects.get(id=int(arg))
    context["document"] = document
    return context


@staff_member_required
@render_to("admin/check_user_view.html")
def show_invoice(request, arg):
    context = {}
    document = Invoice.objects.get(id=int(arg))
    context["document"] = document
    return context


def send_document(modeladmin, request, queryset):
    dict_documents_for_send = {}
    for query_obj in queryset:
        dict_documents_for_send = add_document_in_dict_for_send(dict_documents_for_send, query_obj.created_by.id, str(queryset.model.__name__), [query_obj.id])
    send_mail_check(dict_documents_for_send)
send_document.short_description = u"Отправить пользователю на почту"


def convert_to_csv(modeladmin, request, queryset):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment;filename="spisok_%s.csv"' % (queryset.model.__name__)
    writer = csv.writer(response, delimiter=';' , dialect='excel')
    writer.writerow(['N document', 'Name', 'Internal number', 'ID user'])
    for query_obj in queryset:
        try:
            profile_obj = Profile.objects.get(user=query_obj.created_by)
            if not profile_obj.is_juridical:
                try:
                    bill_acc = BillserviceAccount.objects.get(id=profile_obj.billing_account_id)
                    number = BillserviceSubAccount.objects.filter(account=bill_acc).aggregate(Min('username'))['username__min']
                    main_billing_account_id = profile_obj.main_billing_account_id()
                    writer.writerow([query_obj.number, query_obj.created_by.username.encode('cp1251'), number, '[%s]' % main_billing_account_id])
                except Exception, e:
                    print e
        except Profile.DoesNotExist:
            continue
    return response
convert_to_csv.short_description = u"Конвертировать список в CSV"

from django.contrib import messages
class CheckAdmin(admin.ModelAdmin):


    list_display = ['number', 'created_by', 'year', 'month', 'every_month', 'sent', 'valid']
    list_filter = ('year', 'month', 'sent', 'every_month')
    search_fields = ('created_by__username',)
    actions = [send_document, convert_to_csv]

    # def has_add_permission(self, request):
        # Nobody is allowed to add
    #    return False

    # def has_delete_permission(self, request, obj=None):
        # Nobody is allowed to delete
    #    return False


    def get_form(self, request, obj=None, **kwargs):
        form = CheckForm

        return form
    """def get_urls(self):
        urls = super(CheckAdmin, self).get_urls()
        my_urls = patterns('', ("^(.+)/$", show_check),)
        return my_urls + urls"""
    def get_urls(self):
        urls = super(CheckAdmin, self).get_urls()
        my_urls = patterns('', ("^(add)/$", show_check_add), ("^(.+)/$", show_check))
        return my_urls + urls
    class Media:
        js = ['/media/js/jquery.min.js',
              '/media/js/chosen.jquery.js',
              '/media/js/chosen_select.js']
        css = {'all':('/media/css/chosen.css',)}

class ActAdmin(admin.ModelAdmin):
    list_display = ['number', 'created_by', 'year', 'month', 'sent']
    list_filter = ('year', 'month', 'sent')
    search_fields = ('created_by__username',)
    ordering = ('-year', '-month', '-number',)
    actions = [send_document, convert_to_csv]

    def has_add_permission(self, request):
        # Nobody is allowed to add
        return False

    def has_delete_permission(self, request, obj=None):
        # Nobody is allowed to delete
        return False

    def get_urls(self):
        urls = super(ActAdmin, self).get_urls()
        my_urls = patterns('', ("^(.+)/$", show_act),)
        return my_urls + urls





class CheckForm(forms.ModelForm):
    class Meta:
        model = Check
        fields = ['created_by', 'year', 'month', 'every_month', 'created_at', 'sent', 'number', 'findoc', 'type_paid', 'valid', 'text']
    def __init__(self, *args, **kwargs):
        super(CheckForm, self).__init__(*args, **kwargs)
        self.fields['number'].help_text = u'если поле не заполнено, то автоматически подставляется новое значение'
        self.fields['findoc'].help_text = u'необходимо выбрать договор по которому выставляется счет'
        self.fields['valid'].help_text = u'не отображается в личном кабинете пользователя'


@staff_member_required
@render_to("admin/check_custom.html")
def show_check_add(request, arg):
    context = {}
    context['save'] = "_update"
    context['up_val'] = u"Обновить документ"

    p_o = Profile.objects.get(user=1)
    context['pr'] = p_o
    addresses = p_o.addresses.all()
    findoc_template = FinDocTemplate.objects.get(id=41)

    findoc = FinDoc.objects.all()
    check_form = CheckForm(instance=findoc_template)
    context['form'] = check_form
    context["document"] = findoc_template
    error_message, info_message, valid = [], [], True

    if request.POST:
        user = request.POST.get('created_by')
        if user:
            pro_o = Profile.objects.get(user=user)
            context['legal_adrress'] = pro_o.get_legal_adrress()
        if not request.POST['number']:
            context['number'] = Check.get_next_number(Check, datetime.datetime.now().year)
        sign = FinDocSigned.objects.filter(signed_by=pro_o.user, findoc__id=request.POST['id_findoc_post'])
        if sign:
            context['signed'] = sign
        context['id'] = request.POST['created_by']
        try:
            profile_object = Profile.objects.get(user=request.POST['created_by'])
        except Profile.DoesNotExist():
            pass
        if profile_object:
            if profile_object.is_juridical:
                context['prof2'] = profile_object
            else:
                context['prof1'] = profile_object

        date = request.POST['created_at']
        number = request.POST['number']
        context['date_field'] = date
        context['number_field'] = number
        context['findoc_number'] = request.POST['id_findoc_post']

        if not context.has_key('signed'):
            context['form_is_valid'] = info_message
            info_message.append("У этого пользователя нет подписанных документов.")

        try:
            if int(request.POST['number']):
                context['number'] = request.POST['number']
        except:
            pass
        context['type_paid'] = request.POST['type_paid']

        if context.has_key('form') and request.POST.has_key('_continue'):
            f = CheckForm(request.POST)
            new_number = f
            if new_number.is_valid():
                new_number = f.save(commit=True)
                new_number.save()
                valid = True
                info_message.append("check 'Check object' был успешно добавлен. Ниже вы можете снова его отредактировать.")

            else:
                valid = False
                error_message.append("Пожалуйста, исправьте ниже.")
                context.update({'error_list' : True})
        if not(valid):
            context['form_is_not_valid'] = error_message

        if (valid) and request.POST.has_key('_continue'):
            context['form_is_valid'] = info_message

        if context.has_key('form') and request.POST.has_key('_addanother'):
            f = CheckForm(request.POST)
            new_number = f
            if new_number.is_valid():
                new_number = f.save(commit=True)
                new_number.save()
                valid = True
                info_message.append("check 'Check object' успешно добавлен. Ниже вы можете добавить еще check.")
                context['number'] = ""
                context['type_paid'] = ""
                context['id'] = ""
                context['prof'] = ""

            else:
                valid = False
                error_message.append("Пожалуйста, исправьте ниже.")
                context.update({'error_list' : True})
        if not(valid):
            context['form_is_not_valid'] = error_message

        if (valid) and request.POST.has_key('_addanother'):
            context['form_is_valid'] = info_message

        if context.has_key('form') and request.POST.has_key('_update'):
            f = CheckForm(request.POST)
            new_number = f
            if new_number.is_valid():
                context['save'] = "_save"
                context['up_val'] = u"Сохранить"
                valid = True
                context['form_is_valid'] = info_message
                info_message.append("Данные документа были успешно обновлены")
            if not new_number.is_valid() and context.has_key('number') and not request.POST['type_paid'] == "" and not request.POST['created_by'] == "":
                valid = False
                context['form_is_valid'] = info_message
                info_message.append("Поле номер счета успешно обновилось.")

            if request.POST['type_paid'] == "" or request.POST['created_by'] == "":
                valid = False
                error_message.append("Пожалуйста, исправьте ниже.")
                context.update({'error_list' : True})
        if context.has_key('form') and request.POST.has_key('_save'):
            f = CheckForm(request.POST)
            new_number = f
            if new_number.is_valid():
                new_number.save()
                valid = True
                info_message.append("check 'Check object' был успешно создан")
            else:
                valid = False
                error_message.append("Пожалуйста, исправьте ниже.")
                context.update({'error_list' : True})
        if not(valid):
            context['form_is_not_valid'] = error_message

        if (valid) and request.POST.has_key('_save'):
            context['form_is_valid'] = info_message
            messages.add_message(request, messages.INFO, "check 'Check object' был успешно создан.")
            return HttpResponseRedirect(request.path.replace("/add/", ""))

    return context



class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['number', 'created_by', 'year', 'month', 'sent']
    list_filter = ('year', 'month', 'sent')
    search_fields = ('created_by__username',)
    ordering = ('-year', '-month', '-number',)
    actions = [send_document, convert_to_csv]

    def has_add_permission(self, request):
        # Nobody is allowed to add
        return False

    def has_delete_permission(self, request, obj=None):
        # Nobody is allowed to delete
        return False

    def get_urls(self):
        urls = super(InvoiceAdmin, self).get_urls()
        my_urls = patterns('', ("^(.+)/$", show_invoice),)
        return my_urls + urls

from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
csrf_protect_m = method_decorator(csrf_protect)

class DownloadDocumentsAdmin(admin.ModelAdmin):
    # actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def queryset(self, request):
        return []

    META = {}  # это нужно
    notifications = {}  # и это нужно

    @csrf_protect_m
    @render_to("admin/download_documents.html")
    def changelist_view(self, request, extra_context=None):
        context = {}
        context["request"] = request
        context["user"] = request.user
        context["title"] = u'Скачать архив документов за определенную дату'
        context["csrf_token"] = request.COOKIES.get("csrftoken")
        context["app_label"] = Download_documents._meta.app_label
        context["app_section"] = Download_documents._meta.verbose_name_plural

#        dict_year_check = Check.objects.filter(every_month = True).order_by('year').distinct().values('year')
#        year_check = [i["year"] for i in dict_year_check]
        dict_year_act = Act.objects.order_by('year').distinct().values('year')
        year_act = [i["year"] for i in dict_year_act]
        dict_year_invoice = Invoice.objects.order_by('year').distinct().values('year')
        year_invoice = [i["year"] for i in dict_year_invoice]
        spis_years = set(year_act) | set(year_invoice)
        context['spis_years'] = spis_years
        if request.GET.has_key('year') and request.GET.has_key('month'):
            from StringIO import StringIO
            from zipfile import ZipFile

            year = request.GET['year']
            month = request.GET['month']
            start_month = datetime.datetime(int(year), int(month), 1, 0, 0, 0)
            end_month = start_month + relativedelta(months=1)
            print start_month, end_month

            in_memory = StringIO()
            zip = ZipFile(in_memory, "a")

#            check_queryset = Check.objects.filter(Q(created_at__gte=start_month) & Q(created_at__lt=end_month) & Q(every_month = True))
#            for check_obj in check_queryset:
#                zip.writestr("%s/check_%s.doc" % (check_obj.created_by.username.encode('cp866'), check_obj.number), check_obj.text.encode('utf-8'))

            act_queryset = Act.objects.filter(Q(created_at__gte=start_month) & Q(created_at__lt=end_month))
            for act_obj in act_queryset:
                if act_obj.text:
                    zip.writestr("%s/act_%s.doc" % (act_obj.created_by.username.encode('cp866'), act_obj.number), act_obj.text.encode('utf-8'))
                else:
                    zip.writestr("%s/act_%s.doc" % (act_obj.created_by.username.encode('cp866'), act_obj.number), '')

            invoice_queryset = Invoice.objects.filter(Q(created_at__gte=start_month) & Q(created_at__lt=end_month))
            for invoice_obj in invoice_queryset:
                if invoice_obj.text:
                    zip.writestr("%s/invoice_%s.doc" % (invoice_obj.created_by.username.encode('cp866'), invoice_obj.number), invoice_obj.text.encode('utf-8'))
                else:
                    zip.writestr("%s/invoice_%s.doc" % (invoice_obj.created_by.username.encode('cp866'), invoice_obj.number), '')

            # fix for Linux zip files read in Windows
            for file in zip.filelist:
                file.create_system = 0

            zip.close()

            response = HttpResponse(mimetype="application/zip")
            response["Content-Disposition"] = "attachment; filename=act_sf_%s_%s.zip" % (month, year)

            in_memory.seek(0)
            response.write(in_memory.read())
            return response

        return context


class DownloadChecksAdmin(admin.ModelAdmin):
    # actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def queryset(self, request):
        return []

    META = {}  # это нужно
    notifications = {}  # и это нужно

    @csrf_protect_m
    @render_to("admin/download_documents.html")
    def changelist_view(self, request, extra_context=None):
        context = {}
        context["request"] = request
        context["user"] = request.user
        context["title"] = u'Скачать архив документов за определенную дату'
        context["csrf_token"] = request.COOKIES.get("csrftoken")
        context["app_label"] = Download_documents._meta.app_label
        context["app_section"] = Download_documents._meta.verbose_name_plural

        dict_year_check = Check.objects.filter(every_month=True).order_by('year').distinct().values('year')
        year_check = [i["year"] for i in dict_year_check]
        spis_years = set(year_check)
        context['spis_years'] = spis_years
        if request.GET.has_key('year') and request.GET.has_key('month'):
            from StringIO import StringIO
            from zipfile import ZipFile

            year = request.GET['year']
            month = request.GET['month']
            start_month = datetime.datetime(int(year), int(month), 1, 0, 0, 0)
            end_month = start_month + relativedelta(months=1)
            print start_month, end_month

            in_memory = StringIO()
            zip = ZipFile(in_memory, "a")

            check_queryset = Check.objects.filter(Q(created_at__gte=start_month) & Q(created_at__lt=end_month) & Q(every_month=True))
            for check_obj in check_queryset:
                if check_obj.text:
                    zip.writestr("%s/check_%s.doc" % (check_obj.created_by.username.encode('cp866'), check_obj.number), check_obj.text.encode('utf-8'))
                else:
                    zip.writestr("%s/check_%s.doc" % (check_obj.created_by.username.encode('cp866'), check_obj.number), '')

            # fix for Linux zip files read in Windows
            for file in zip.filelist:
                file.create_system = 0

            zip.close()

            response = HttpResponse(mimetype="application/zip")
            response["Content-Disposition"] = "attachment; filename=checks_%s_%s.zip" % (month, year)

            in_memory.seek(0)
            response.write(in_memory.read())
            return response

        return context


class PrintActAdmin(admin.ModelAdmin):
    # actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def queryset(self, request):
        return []

    META = {}  # это нужно
    notifications = {}  # и это нужно

    @render_to("admin/Print_act.html")
    def changelist_view(self, request, extra_context=None):
        context = {}
        context["errors"] = []
        context["application_text"] = ""
        context["title"] = u'Просмотр акта приемки/передачи'
        context["app_label"] = Print_act._meta.app_label
        context["app_section"] = Print_act._meta.verbose_name_plural
        zayavka_id = request.GET["zakaz_id"]
        url_after_sign = "/account/internet/demands/activation/"+str(zayavka_id)+"/"
        try:
            zakaz = Zakazy.objects.get(id=zayavka_id)
        except Exception, exc:
            context["errors"].append("No such zakaz id")
            return context
        bill_acc = zakaz.bill_account
        try:
            user = User.objects.get(username=bill_acc.username)
        except Exception, exc:
            context["errors"].append("No such user")
            return context
        app_list = FinDocSignApplication.objects.filter(assigned_to=user)  # получаем все заявки
        for app in app_list:  # удаляем все существующие заявки для данного пользователя
            app.delete()
        slug = "akt_priemki_peredachi_vypoln_rabot"
        doc = FinDoc.objects.get(slug=slug)
        user_can_cancel = True
        sd = FinDocSignApplication(
            assigned_to=user,
            assigned_at=get_now(),
            findoc=doc,
            user_can_cancel=user_can_cancel,
            service_for_billing="application_from_a_package"
        )
        sd.pickle_params({"redirect_after_sign": url_after_sign})
        sd.save()

        try:
            package_obj = Package_on_connection_of_service.objects.get(url_after_sign=url_after_sign, user=user)
        except:
            slugs = ['akt_priemki_peredachi_vypoln_rabot']
            successfully_create = create_package(user,
                                                 '/account/internet/demands/activation/%s/' % zayavka_id,
                                                 reverse('my_inet'),
                                                 '',
                                                 slugs)
            if not successfully_create:
                return HttpResponse("Can't create package!")
            else:
                package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                package_obj.activate = True
                package_obj.save()
        activate = package_obj.activate
        deactivate = package_obj.deactivate
        package_obj.activate = False
        package_obj.deactivate = False
        package_obj.save()
        app = FinDocSignApplication.objects.filter(assigned_to=user, findoc__slug=slug)
        app = app[0]
        app_id = app.id
        app_text = app.process_text(request=request, findocapp_id=app_id)
        context["application_text"] = app_text
        package_obj.activate = activate
        package_obj.deactivate = deactivate
        package_obj.save()


        return context

admin.site.register(Check, CheckAdmin)
admin.site.register(Act, ActAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Rules_of_drawing_up_documents, Rules_of_drawing_up_documents_Admin)
admin.site.register(FinDoc, FinDocAdmin)
admin.site.register(FinDocTemplate, FinDocTemplateAdmin)
admin.site.register(FinDocSignApplication, FinDocSignApplicationAdmin)
admin.site.register(FinDocSigned, FinDocSignedAdmin)
admin.site.register(Package_on_connection_of_service, Package_on_connection_of_service_Admin)
admin.site.register(Download_documents, DownloadDocumentsAdmin)
admin.site.register(Download_checks, DownloadChecksAdmin)
admin.site.register(Print_act,PrintActAdmin)
