# coding: utf-8
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from lib.decorators import render_to
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from models import TelNumber, TelNumbersGroup, TelNumbersZakazy, Status_number
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User

csrf_protect_m = method_decorator(csrf_protect)

def get_ready_context(request, title):
    context = {}
    context["request"] = request
    context["user"] = request.user
    context["title"] = title
    context["is_popup"] = True if (request.GET and request.GET.get("_popup")) else False
    context["csrf_token"] = request.COOKIES.get("csrftoken")
    context["app_label"] = "telnumbers"
    context["app_section"] = _(u"Internal numbers")
    context["language"] = "ru"
    context["none_value"] = "---"
    return context

@staff_member_required
@render_to("admin/telnumbers/add.html")
def add_internal(request):
    context = get_ready_context(request, _(u"Add internal number"))
    context["new_number_juridical"] = TelNumber.get_next_free_number(False, is_juridical = True)
    context["new_number_phisycal"] = TelNumber.get_next_free_number(False, is_juridical = False)
    all_users = []
    for user in User.objects.filter(is_staff=False):
        try:
            profile = user.get_profile()
        except:
            pass
        else:
            user.is_juridical = profile.is_juridical
            user.juridical_id = user.id if profile.is_juridical else -user.id
            all_users.append(user)
    context["users"] = all_users

    if request.POST:
        if request.POST.get("cancel"):
            return HttpResponseRedirect("../")
        if request.POST.get("add"):
            user_id = request.POST.get("user")
            password = request.POST.get("password")
            person_name = request.POST.get("person_name")
            internal_phone = request.POST.get("internal_phone")
            user = User.objects.get(id=user_id)
            profile = user.get_profile()
            number = TelNumber.get_next_free_number(is_juridical=profile.is_juridical)
            bac = profile.billing_account
            tn = TelNumber.create(bac, number, profile.is_juridical, password, person_name, internal_phone)
            request.notifications.add(_(u"Number %s added successfully") % tn, "success")

    return context



from django.conf.urls import patterns, url, include
class TelNumberAdmin(admin.ModelAdmin):
    list_display = ["tel_number", "account", "internal_phone", "person_name"]
    search_fields = ["tel_number", "account__username", "internal_phone", "person_name"]
    readonly_fields = ["tel_number", "account", "internal_phone", "person_name"]
    # exclude = ("is_deleted", "activated")
    actions = None

    def get_urls(self):
        urls = super(TelNumberAdmin, self).get_urls()            
        my_urls = patterns('', ("^add/$", add_internal))
        return my_urls + urls

    def has_delete_permission(self, request, obj = None):
        return False
    
class TelNumbersZakazyAdmin(admin.ModelAdmin):
    list_display = ("id", "bill_account", "date_activation", "date_deactivation", "status_number")
    search_fields = ("bill_account__username", "number__tel_number")
    filter_horizontal = ('number',)


class StatusNumberAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'about')




admin.site.register(TelNumber, TelNumberAdmin)
admin.site.register(TelNumbersZakazy , TelNumbersZakazyAdmin)
admin.site.register(Status_number , StatusNumberAdmin)

from admin_groups import TelNumbersGroupAdmin
admin.site.register(TelNumbersGroup, TelNumbersGroupAdmin)

