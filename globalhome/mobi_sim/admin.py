# -*- coding=utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from models import MobiSim
from lib.decorators import render_to
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

csrf_protect_m = method_decorator(csrf_protect)
from billing.models import BillserviceAccount
import settings

class MobiSimAdmin(admin.ModelAdmin):
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def queryset(self, request):
        return []

    META = {}
    notifications = {}



    @csrf_protect_m
    @render_to("admin/mobi_sim.html")
    def changelist_view(self, request, extra_context=None):

        context = {}
        context["request"] = request
        context["user"] = request.user
        context["title"] = _(u"MobiSims")
        context["csrf_token"] = request.COOKIES.get("csrftoken")
        context["app_label"] = "mobisims"
        context["app_section"] = _(u"Mobi Sims")
        context["language"] = "ru"

        self.user = request.user


        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

        # sql = "SELECT billservice_account.id, billservice_account.username as login, billservice_account.password, billservice_card.login as pin FROM billservice_account JOIN billservice_card ON billservice_card.account_id=billservice_account.id WHERE group_id=5 AND billservice_account.username::integer<=6999999 and billservice_account.username::integer>=6000000 and length(billservice_account.username)=7 ORDER by billservice_account.username;"
        sql = "SELECT billservice_account.id, billservice_account.username as login, billservice_account.password, billservice_card.login as pin FROM billservice_account JOIN billservice_card ON billservice_card.account_id=billservice_account.id WHERE group_id=5 AND length(billservice_account.username)=10 ORDER by billservice_account.username;"
        mobisims = BillserviceAccount.objects.raw(sql).using(settings.BILLING_DB)
        # print dir(mobisims)

        def items_count():
            c_mobisims = []
            for m in mobisims:
                c_mobisims.append(m)

            return len(c_mobisims)

        mobisims.count = items_count

        paginator = Paginator(mobisims, 200)  # Show 200 MobiSims per page

        page = request.GET.get('page')
        if not page:
            page = 1
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)

        context["contacts"] = contacts
        return context


    class Meta:
        app_label = "MobiSims"
        verbose_name = _("Mobi sim")
        verbose_name_plural = _("Mobi sims")


admin.site.register(MobiSim, MobiSimAdmin)


