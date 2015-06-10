# -*-coding=utf-8-*-
from models import *
from django.contrib import admin
from forms import MikrotikForm
from internet.models import Connection_address, Internet_city, Internet_street, Internet_house
import trans
from django.utils.translation import ugettext as _
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.contrib.admin.util import unquote
from django.utils.encoding import force_text
from django.db.models import Q
from django.http import  HttpResponse, HttpResponseRedirect

class MikrotikModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


class MACaddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'MAC_address', 'mikrotik', ]
    search_fields = ['MAC_address', ]


class InstallerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name', ]




class ChangeParentForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    parent = forms.ModelChoiceField(queryset=Mikrotik.objects.all().filter(type_of_settings='primary').order_by('name_of_mikrotik'), label=u'Родительский микротик') 



class ChangeAddressForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    address = forms.ModelChoiceField(queryset=Connection_address.objects.select_related().order_by('street__street_type', 'street__street', 'house__house'), label=u'Адрес')

def change_parent(self, request, queryset):
    model = self.model
    opts = model._meta
    form = None
    if 'apply' in request.POST: 
        form = ChangeParentForm(request.POST)
        if form.is_valid():
            parent = form.cleaned_data['parent']
            count = 0
            for item in queryset:
                if (item.address == parent.address and (item.address)):
                    item.parent = parent
                    item.save()
                    count += 1
            self.message_user(request, "Значение parent %s установленно у %d микротиков." % (parent, count))
            return HttpResponseRedirect(request.get_full_path())
    if not form:
        form = ChangeParentForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
    t = loader.get_template('admin/action.html')
    c = RequestContext(request, {'items': queryset,
                                'form': form,
                                'title':u'Изменить родительский микротик',
                                'app_label': opts.app_label,
                                'hidden_input':'change_parent',
                                'label':'Поле Parent будет установлено для следующих микротиков:',
                                'opts':opts,
                                 })
    return HttpResponse(t.render(c))
change_parent.short_description = u"Изменить родительский микротик"
change_parent.allow_tags = True




       
def set_address(self, request, queryset):
    model = self.model
    opts = model._meta
    form = None
    if 'apply' in request.POST:
        form = ChangeAddressForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data['address']
            count = 0
            for item in queryset:
                item.address = address.id
                item.save()
                count += 1
            self.message_user(request, "Значение address %s %s %s установленно у %d микротиков." % (address.city, address.street, address.house, count))
            return HttpResponseRedirect(request.get_full_path())
    if not form:
        form = ChangeAddressForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
    t = loader.get_template('admin/action.html')
    c = RequestContext(request, {'items': queryset,
                                 'hidden_input':'set_address',
                                 'label':'Установить адрес для следующих микротиков:',
                                 'form': form,
                                 'title':u'Изменить адрес',
                                 'app_label': opts.app_label,
                                 'opts':opts,
                                 })
    return HttpResponse(t.render(c))
set_address.short_description = u"Изменить адрес"
set_address.allow_tags = True



class ChangeTypeOfSettings(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    type_of_settings = forms.ChoiceField(choices=TYPE_OF_SETTINGS, label=u'Тип настроек')

def change_type_of_settings(self, request, queryset):
    model = self.model
    opts = model._meta
    form = None
    if 'apply' in request.POST:
        form = ChangeTypeOfSettings(request.POST)
        if form.is_valid():
            type_of_settings = form.cleaned_data['type_of_settings']
            count = 0
            for item in queryset:
                item.type_of_settings = type_of_settings
                item.save()
                count += 1
            self.message_user(request, "Установлен %s тип настроек у %d микротиков." % (DIC_TYPE_OF_SETTINGS[type_of_settings], count))
            return HttpResponseRedirect(request.get_full_path())
    if not form:
        form = ChangeTypeOfSettings(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
    t = loader.get_template('admin/action.html')
    c = RequestContext(request, {'items': queryset,
                                 'hidden_input':'change_type_of_settings',
                                 'label':'Изменить тип настроек для следующих микротиков:',
                                 'form': form,
                                 'title':u'Изменить тип настроек',
                                 'app_label': opts.app_label,
                                 'opts':opts,
                                 })
    return HttpResponse(t.render(c))
change_type_of_settings.short_description = u"Изменить тип настроек"
change_type_of_settings.allow_tags = True



class ChangeTypeOfModel(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    mikrotik_model = forms.ModelChoiceField(required=False, queryset=MikrotikModel.objects.all().order_by('name'), label=u'Модель')

def change_type_of_model(self, request, queryset):
    model = self.model
    opts = model._meta
    form = None
    if 'apply' in request.POST:
        form = ChangeTypeOfModel(request.POST)
        if form.is_valid():
            mikrotik_model = form.cleaned_data['mikrotik_model']
            count = 0
            for item in queryset:
                item.mikrotik_model = mikrotik_model
                item.save()
                count += 1
            self.message_user(request, "Модель %s была установлена у %d микротиков." % (mikrotik_model, count))
            return HttpResponseRedirect(request.get_full_path())
    if not form:
        form = ChangeTypeOfModel(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
    t = loader.get_template('admin/action.html')
    c = RequestContext(request, {'items': queryset,
                                 'hidden_input':'change_type_of_model',
                                 'label':'Установить модель для следующих микротиков:',
                                 'form': form,
                                 'title':u'Изменить модель микротика',
                                 'app_label': opts.app_label,
                                 'opts':opts,
                                 })
    return HttpResponse(t.render(c))
change_type_of_model.short_description = u"Изменить модель микротика"
change_type_of_model.allow_tags = True



class ChangeInstaller(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    installer_name = forms.ModelChoiceField(required=False, queryset=Installer.objects.all().order_by('name'), label=u'Кто установил')

def chage_installer(self, request, queryset):
    model = self.model
    opts = model._meta
    form = None
    if 'apply' in request.POST:
        form = ChangeInstaller(request.POST)
        if form.is_valid():
            installer_name = form.cleaned_data['installer_name']
            count = 0
            for item in queryset:
                item.installer_name = installer_name
                item.save()
                count += 1
            self.message_user(request, "Поле кто установил было установлено значение %s у %d микротиков." % (installer_name, count))
            return HttpResponseRedirect(request.get_full_path())
    if not form:
        form = ChangeInstaller(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
    t = loader.get_template('admin/action.html')
    c = RequestContext(request, {'items': queryset,
                                 'hidden_input':'chage_installer',
                                'label':'Поле кто установил будет изменено для следующих микротиков:',
                                 'form': form,
                                 'title':u'Изменить установщика',
                                 'app_label': opts.app_label,
                                 'opts':opts,
                                 })
    return HttpResponse(t.render(c))
chage_installer.short_description = u"Изменить установщика"
chage_installer.allow_tags = True


 
class ChangeDateInstallation(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    date_installation = forms.DateField(help_text=u'Вида yyyy-mm-dd')

def chage_date_installation(self, request, queryset):
    model = self.model
    opts = model._meta
    form = None
    if 'apply' in request.POST:
        form = ChangeDateInstallation(request.POST)
        if form.is_valid():
            date_installation = form.cleaned_data['date_installation']
            count = 0
            for item in queryset:
                item.date_installation = date_installation
                item.save()
                count += 1
            self.message_user(request, "Дата установки %s установлена у %d микротиков." % (date_installation, count))
            return HttpResponseRedirect(request.get_full_path())
    if not form:
        form = ChangeDateInstallation(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
    t = loader.get_template('admin/action.html')
    c = RequestContext(request, {'items': queryset,
                                 'hidden_input':'chage_date_installation',
                                 'label':'Дата установки будет установлена для следующих микротиков:',
                                 'form': form,
                                 'title':u'Изменить дату установки',
                                 'app_label': opts.app_label,
                                 'opts':opts,
                                 })
    return HttpResponse(t.render(c))
chage_date_installation.short_description = u"Изменить дату установки"
chage_date_installation.allow_tags = True



class SetFlagOfInstallation(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    is_installed = forms.BooleanField(required=False, label=u'Установлен')       
    
def set_flag_of_installation(self, request, queryset):
    model = self.model
    opts = model._meta
    form = None
    if 'apply' in request.POST:
        form = SetFlagOfInstallation(request.POST)
        if form.is_valid():
            is_installed = form.cleaned_data['is_installed']
            count = 0
            for item in queryset:
                item.is_installed = is_installed
                item.save()
                count += 1
            self.message_user(request, "Изменено значение установлен ли микротик на %s у %d микротиков." % (is_installed, count))
            return HttpResponseRedirect(request.get_full_path())
    if not form:
        form = SetFlagOfInstallation(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
    t = loader.get_template('admin/action.html')
    c = RequestContext(request, {'items': queryset,
                                 'hidden_input':'set_flag_of_installation',
                                 'label':'Флаг установки будет установлен для следующих микротиков:',
                                 'form': form,
                                 'title':u'Изменить флаг установки',
                                 'app_label': opts.app_label,
                                 'opts':opts,
                                 })
    return HttpResponse(t.render(c))
set_flag_of_installation.short_description = u"Изменить флаг установки"
set_flag_of_installation.allow_tags = True


class MikrotikAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'MAC_addresses', 'used_ipsubnet', 'type_of_settings', 'address_of_mikrotik', 'parent', 'porch', 'floor', 'flat',
                     'mikrotik_name', 'mikrotik_model', 'installer_name', 'date_installation', 'last_day_of_test', 'is_installed', 'notation', ]
    list_filter = ('type_of_settings', 'mikrotik_model', 'installer_name', 'is_installed')
    search_fields = ['field_for_search', 'name_of_mikrotik', 'ip_address', ]
    actions = [change_parent, set_address, set_flag_of_installation, chage_date_installation, chage_installer, change_type_of_model, change_type_of_settings]
    list_display_links = ('ip_address', 'MAC_addresses',)
    readonly_fields = ['download_speed', 'upload_speed', 'street', 'house', 'corpse'] #'name_of_mikrotik', 
    special_field = 'address_of_mikrotik'
    save_as = True
    form = MikrotikForm


    def mikrotik_name(self, obj):
        if obj.type_of_settings == 'primary':
            return '<a href="?parent__id__exact=%d">%s</a>' % (obj.id, obj.name_of_mikrotik)
        return obj.name_of_mikrotik
    mikrotik_name.allow_tags = True
    mikrotik_name.short_description = u"Наименование микротика"
    mikrotik_name.admin_order_field = 'name_of_mikrotik'
    
  
    
    def save_model(self, request, obj, form, change):
        from internet_providers.models import Account
        if obj.type_of_settings == 'primary' and Account.objects.filter(connection_address=obj.address):
            account = Account.objects.filter(connection_address=obj.address)[0]
            obj.download_speed = account.download_speed
            obj.upload_speed = account.upload_speed
        obj.save()
    
    
    def get_changelist(self, request, **kwargs):
        from changelist import SpecialOrderingChangeList
        return SpecialOrderingChangeList


    def address_of_mikrotik(self, obj):
        try:
            obj = Connection_address.objects.get(id=int(obj.address))
            city = '%s' % (obj.city)
            street = ' <a href="?q=%s+%s">%s</a>' % (obj.city , obj.street, obj.street)
            house = ' <a href="?q=%s+%s+%s">%s</a>' % (obj.city , obj.street, obj.house , obj.house)
            return '%s %s %s' % (city, street, house)
        except Exception, e:
            return ''
    address_of_mikrotik.allow_tags = True
    address_of_mikrotik.short_description = u"Адрес установки"
    address_of_mikrotik.admin_order_field = 'address'


    def add_view(self, request, form_url='', extra_context=None):
        "The 'add' admin view for this model."
        extra_context = {} if not(extra_context) else extra_context
        extra_context.update({'has_add_second_mikrotik': False})
        extra_context.update({'qs_primary_mikrotiks': Mikrotik.objects.all().filter(type_of_settings='primary').order_by('name_of_mikrotik', 'ip_address'),
                            'qs_secondary_mikrotiks': Mikrotik.objects.all().filter(Q(type_of_settings='secondary') | Q(type_of_settings='reserve')).order_by('name_of_mikrotik', 'ip_address')})
        return super(MikrotikAdmin, self).add_view(request, form_url, extra_context)


    def change_view(self, request, object_id, form_url='', extra_context=None):
        "The 'change' admin view for this model."
        obj = self.get_object(request, unquote(object_id))
        extra_context = {} if not(extra_context) else extra_context
        extra_context.update({'has_add_second_mikrotik': True if obj.type_of_settings == 'primary' else False})
        extra_context.update({'qs_primary_mikrotiks': Mikrotik.objects.all().filter(type_of_settings='primary').order_by('name_of_mikrotik', 'ip_address'),
                            'qs_secondary_mikrotiks': Mikrotik.objects.all().filter(Q(type_of_settings='secondary') | Q(type_of_settings='reserve')).order_by('name_of_mikrotik', 'ip_address')})
        return super(MikrotikAdmin, self).change_view(request, object_id, form_url, extra_context)


 
    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """
        opts = self.model._meta
        msg_dict = {'name': force_text(opts.verbose_name), 'obj': force_text(obj)}
        if "_addsecond" in request.POST and obj.type_of_settings == 'primary':
            msg = _('The %(name)s "%(obj)s" was changed successfully. You may add another %(name)s below.') % msg_dict
            self.message_user(request, msg)
            return HttpResponseRedirect(reverse('admin:%s_%s_add' % 
                                        (opts.app_label, opts.module_name),
                                        current_app=self.admin_site.name) + "?_parent=%s" % (obj.id))
        return super(MikrotikAdmin, self).response_change(request, obj)
   
    def address_of_mikrotik_for_order(self, obj):
        try:
            obj = Connection_address.objects.get(id=int(obj.address))
            return u'%s %s %s' % (obj.city, obj.street, obj.house)
        except Exception, Connection_address.DoesNotExist:
            return ''    
    special_action = address_of_mikrotik_for_order


    class Media:
        js = ['/media/js/changelist-filter.js',
              '/media/js/jquery.min.js',
              '/media/js/chosen.jquery.js',
              '/media/js/chosen_select.js',
              '/media/js/add_page_zakazy_fieldsets.js']
        css = {'all':('/media/css/chosen.css',)}
admin.site.register(Installer, InstallerAdmin)
admin.site.register(MikrotikModel, MikrotikModelAdmin)
admin.site.register(Mikrotik, MikrotikAdmin)
admin.site.register(MACaddress, MACaddressAdmin)
