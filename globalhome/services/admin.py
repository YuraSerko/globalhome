# coding: utf-8
from django.contrib import admin
from services.models import SPDescriptionTemplate, ServiceFunctional, AvailableService, AvailableServicePacket, ServicePacketApplication, AssignedServicePacket, AssignServicePacket
from content import BaseContentAdmin
#from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import patterns, url, include
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
#from account.models import get_all_user_choices
from django import forms
from django.db import models
from django.contrib.admin.views.decorators import staff_member_required
from lib.utils import get_ready_context
from django.contrib.auth.models import User

@staff_member_required
def service_functional_configure(request, f_id):
    "Эта функция вызывается для редактирования функционала и его параметров."
    functional = ServiceFunctional.objects.get(id = int(f_id))
    f_class, exception = functional.get_functional()
    
    context = get_ready_context(request, _(u"Setup service functional"), _(u"Service functionals"))
    
    if request.POST:
        if request.POST.get("save"):
            functional.name = request.POST["name"]
            functional.slug = request.POST["slug"]
            functional.module = request.POST["module"]
            functional.save()
            f_class, exception = functional.get_functional()
        if request.POST.get("cancel"):
            return HttpResponseRedirect("../")
    
    context["functional"] = functional
    context["f_class"] = f_class
    context["exception"] = exception
    
    if f_class:
        return f_class.AdminConfigureFunctionalView(functional, request, context)
    
    return render_to_response("admin/services/base_functional_configure.html", context, context_instance = RequestContext(request))

class ServiceFunctionalAdmin(admin.ModelAdmin):
    "Администрирование функционалов услуг"
    list_display = ("name", "slug", "module")
    exclude = ("params_data",)
    actions = None
    
    def get_urls(self):
        urls = super(ServiceFunctionalAdmin, self).get_urls()
        my_urls = patterns('', ("^(.+)/$", service_functional_configure))
        return my_urls + urls
    
    
class SPDescriptionTemplateAdmin(BaseContentAdmin):
    "Администрирование шаблонов описаний услуг"
    pass


class AvailableServiceAdmin(admin.ModelAdmin):
    "Администрирование Доступных услуг"
    list_display = ("name", "functional",)

class AvailableServicePacketAdmin(admin.ModelAdmin):
    "Администрирование доступных пакетов услуг"
    list_display = ("name", "slug")
    exclude = ("params_data",)
    formfield_overrides = {
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
    }

@staff_member_required
def sp_application_edit(request, app_id):
    "view-функция, которая вызывается, когда редактируют заявку на добавление/удаление пакета услуг"
    app_id = int(app_id)
    context = get_ready_context(request, _(u"Service packet application editing"), _(u"Service packets applications"))
    app = ServicePacketApplication.objects.get(id = app_id)
    context["application"] = app
    result, services = app.packet.functionals_call("AdminSPApplicationEditView", request, app, context, also_services = True)
    templates = []
    if result:
        for i, res in enumerate(result):
            if res[0]:
                if res[0] not in templates:
                    templates.append({
                        "template": res[0],
                        "service": services[i],
                    })
            if res[1]:
                context.update(res[1])
    context["custom_services_templates"] = templates
    return render_to_response("admin/services/base_sp_application_edit.html", context, context_instance = RequestContext(request))


class ServicePacketApplicationAdmin(admin.ModelAdmin):
    "Администрирование заявок на подключение/отключение пакетов услуг"
    list_display = ("packet", "assigned_to", "application_type", "assigned_at", "assigned_by", "extra_text")
    list_filter = ("application_type",)
    readonly_fields = ("packet", "application_type", "assigned_to", "assigned_at", "assigned_by")
    exclude = ("params_data",)
    date_hierarchy = "assigned_at"
    actions = None
    search_fields = ("assigned_to__username", "packet__name", "assigned_by__username")
    
    def get_urls(self):
        urls = super(ServicePacketApplicationAdmin, self).get_urls()        
        my_urls = patterns('', ("^(.+)/$", sp_application_edit))
        return my_urls + urls
    
    def has_add_permission(self, request):
        "Запрещаем добавление заявок на пакеты"
        return False
    
    def has_delete_permission(self, request, obj = None):
        "Запрещаем удаление заявок на пакеты"
        return False
    
    def delete_view(self, request, object_id, extra_context = None):
        if request.POST:
            # оооочень сильно тут недоделано
            # отменяем эту заявку и возвращаем обычное поведение
            app = ServicePacketApplication.objects.get(id = object_id)
            app.cancel_admin(request)
            return
            return super(ServicePacketApplicationAdmin, self).delete_view(request, object_id, extra_context)
        else:
            return super(ServicePacketApplicationAdmin, self).delete_view(request, object_id, extra_context)
        pass

@staff_member_required
def sp_assigned_edit(request, asp_id):
    "view-функция, которая вызывается, когда редактируют назначенный пакет услуг"
    asp_id = int(asp_id)
    context = get_ready_context(request, _(u"Assigned service packet editing"), _(u"Assigned services packets"))
    asp = AssignedServicePacket.objects.get(id = asp_id)
    context["assigned_sp"] = asp
    
    if request.POST:
        if request.POST.get("save"):
            asp.enabled = bool(request.POST.get("enabled"))
            asp.save()
    
    result, services = asp.packet.functionals_call("AdminSPAssignedEditView", request, asp, context, also_services = True)
    templates = []
    if result:
        for i, res in enumerate(result):
            if res[0]:
                if res[0] not in templates:
                    templates.append({
                        "template": res[0],
                        "service": services[i],
                    })
            if res[1]:
                context.update(res[1])
    context["custom_services_templates"] = templates
    
    return render_to_response("admin/services/base_sp_assigned_edit.html", context, context_instance = RequestContext(request))

class AssignedServicePacketAdmin(admin.ModelAdmin):
    "Администрирование назначенных пакетов услуг"
    list_display = ("packet", "assigned_to", "assigned_at", "application_cteated_at", "assigned_by", "extra_text")
    date_hierarchy = "assigned_at"
    exclude = ("params_data",)
    actions = None
    search_fields = ("assigned_to__username", "packet__name", "assigned_by__username")
    
    def has_add_permission(self, request):
        "Запрещаем добавление назначенных пакетов"
        return False

    def get_urls(self):
        urls = super(AssignedServicePacketAdmin, self).get_urls()
        my_urls = patterns('', ("^(.+)/$", sp_assigned_edit))
        return my_urls + urls

    def delete_view(self, request, object_id, extra_context = None):
        if request.POST:
            object_id = int(object_id)
            asp = AssignedServicePacket.objects.get(id = object_id)
            asp.detach(by = request.user)
            request.notifications.add(_(u"Application for detaching service packet created."), "success")
            return HttpResponseRedirect("../")
        else:
            return super(AssignedServicePacketAdmin, self).delete_view(request, object_id, extra_context)

@staff_member_required
def assign_service_packet(request):
    "view-функция, которая вызывается, когда редактируют назначенный пакет услуг"
    context = get_ready_context(request, _(u"Assigning service packet"), _(u"Assign service packet"))
    
    if request.GET:
        user_id = request.GET.get("user")
        packet_id = request.GET.get("packet")
        try:
            to_user = User.objects.get(id = int(user_id))
            packet = AvailableServicePacket.objects.get(id = int(packet_id))
        except:
            pass
        else:
            context["select_user_and_packet"] = False
            context["to_user"] = to_user
            context["packet"] = packet
            
            if request.POST:
                if request.POST.get("cancel"):
                    return HttpResponseRedirect(".")
                if request.POST.get("assign"):
                    result, services = packet.functionals_call("AdminSPAssignView", request, context, to_user, assign = True, also_services = True)
            else:
                result, services = packet.functionals_call("AdminSPAssignView", request, context, to_user, assign = False, also_services = True)
            responce = None
            templates = []
            if result:
                for i, res in enumerate(result):
                    if res[0]:
                        if res[0] not in templates:
                            templates.append({
                                "template": res[0],
                                "service": services[i],
                            })
                    if res[1]:
                        context.update(res[1])
                    if res[2]:
                        responce = res[2]
            context["custom_services_templates"] = templates
            if responce:
                return responce
    else:
        context["select_user_and_packet"] = True
        ausers = []
        for user in User.objects.filter(is_staff = False, is_active = True):
            try:
                if user.get_profile().get_display_name():
                    ausers.append(user)
            except:
                pass
        context["available_users"] = ausers
        context["available_packets"] = AvailableServicePacket.objects.all()
        
    
    return render_to_response("admin/services/base_assign_service_packet.html", context, context_instance = RequestContext(request))

class AssignServicePacketAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super(AssignServicePacketAdmin, self).get_urls()
        my_urls = patterns('', ("^$", assign_service_packet))
        return my_urls + urls

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj = None):
        return False



admin.site.register(ServiceFunctional, ServiceFunctionalAdmin)
admin.site.register(SPDescriptionTemplate, SPDescriptionTemplateAdmin)
admin.site.register(AvailableService, AvailableServiceAdmin)
admin.site.register(AvailableServicePacket, AvailableServicePacketAdmin)
admin.site.register(ServicePacketApplication, ServicePacketApplicationAdmin)
admin.site.register(AssignedServicePacket, AssignedServicePacketAdmin)
admin.site.register(AssignServicePacket, AssignServicePacketAdmin)
