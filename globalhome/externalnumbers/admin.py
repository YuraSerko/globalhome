# coding: utf-8
from django.contrib import admin
# from account.admin import CustomerAccount as User
from django.utils.translation import ugettext_lazy as _
from lib.decorators import render_to
from django.conf.urls import patterns, url, include
from django.http import HttpResponseRedirect
# from lib.http import get_query_string
# from lib.paginator import SimplePaginator
# import log
from django.contrib.admin.views.decorators import staff_member_required
from externalnumbers.models import ExternalNumber, ExternalNumberTarif
from externalnumbers.consts import REGIONS
from django.db import connections, transaction
from settings import BILLING_DB
from django import forms


def get_ready_context(request, title):
    context = {}
    context["request"] = request
    context["user"] = request.user
    context["title"] = title
    context["is_popup"] = True if (request.GET and request.GET.get("_popup")) else False
    context["csrf_token"] = request.COOKIES.get("csrftoken")
    context["app_label"] = "telnumbers"
    context["app_section"] = _(u"Local numbers")
    context["language"] = "ru"
    context["none_value"] = "---"
    return context

def check_number_format_ok(number):
    "Вот тут должна происходить проверка верности формата текущего добавляемого номера"
    if len(str(number)) == 11:
        return True

@staff_member_required
@render_to("admin/localphones/add.html")
def numbers_add(request):
    context = get_ready_context(request, _(u"Add local numbers"))
    context["all_regions"] = REGIONS
    cur = connections[BILLING_DB].cursor()
    cur.execute("SELECT id,about FROM external_numbers_tarif")
    external_numbers = cur.fetchall()
    transaction.commit_unless_managed(BILLING_DB)
    context["all_numbs"] = external_numbers
    if request.POST:
        add_ok = True

        def Err(s):
            request.notifications.add(s, "error")
            context["start_range_str"] = start_range_str
            context["end_range_str"] = end_range_str
            add_ok = False

        def error_range():
            Err(_(u"Error range!").__unicode__())

        if request.POST.get("cancel"):
            return HttpResponseRedirect("../")
        if request.POST.get("add"):
            start_range_str = request.POST.get("start_range")
            end_range_str = request.POST.get("end_range")
            numbers_type = request.POST.get("numbers_type")
            numbers_tarif = request.POST.get("tarif")
            if numbers_type == "2":
                is_free = True
                is_reserved = False
            else:
                is_free = False
                is_reserved = True

            numbers_dinging = True
            if not request.POST.get("dinging"):
                numbers_dinging = False
                is_free = False
                is_reserved = True

            region = request.POST.get("numbers_region", None)
            if not region is None:
                region = int(region)

            if not end_range_str:
                end_range_str = start_range_str
            try:
                start_range = int(start_range_str)
                end_range = int(end_range_str)
            except:
                error_range()

            else:
                if end_range < start_range:
                    error_range()
                else:
                    count = end_range - start_range + 1
                    count_added = 0
                    for i in xrange(count):
                        c_num = start_range + i

                        if not check_number_format_ok(c_num):
                            Err(_(u"Number %s is incorrect format!") % c_num)
                            break
                        else:
                            try:
                                ExternalNumber.objects.get(number=str(c_num))
                            except:
                                pass
                            else:
                                Err(_("Number %s already exists!") % c_num)
                                continue
                            ExternalNumber(
                                number=str(c_num),
                                phone_numbers_group=None,
                                account=None,
                                region=region,
                                tarif_group=numbers_tarif,
                                dinging=numbers_dinging,
                                is_free=is_free,
                                is_reserved=is_reserved
                            ).save(no_assigned_at_save=True)
                            count_added += 1

                    if count_added:
                        request.notifications.add(_(u"%s numbers successfully added") % count_added, "success")

    return context

@staff_member_required
@render_to("admin/localphones/edit.html")
def number_edit(request, arg):
    context = get_ready_context(request, _(u"Edit local number"))
    number = ExternalNumber.objects.get(id=int(arg))
    context["number"] = number

    if number.is_free or number.is_reserved:
        context["readonly_number"] = False
        context["all_regions"] = REGIONS
        cur = connections[BILLING_DB].cursor()
        cur.execute("SELECT id,about FROM external_numbers_tarif")
        external_numbers = cur.fetchall()
        transaction.commit_unless_managed(BILLING_DB)
        context["all_numbs"] = external_numbers
    else:
        context["readonly_number"] = True


    if request.POST:
        if request.POST.get("cancel"):
            return HttpResponseRedirect("../")

        if request.POST.get("make_reserved"):
            number.make_reserved()
            request.notifications.add(_(u"Local number successfully reserved"), "success")

        if request.POST.get("make_free"):
            region = request.POST.get("region")
            if region:
                number.set_region(region)
            tarif = request.POST.get("tarif")
            if tarif:
                number.set_tarif(int(tarif))
            number.make_free()

        if request.POST.get("set_tarif"):
            region = request.POST.get("region")
            if region:
                number.set_region(region)
            tarif = request.POST.get("tarif")
            if tarif:
                number.set_tarif(int(tarif))
                request.notifications.add('Тарифная группа изменена', "success")


    number = ExternalNumber.objects.get(id=number.id)
    context["number"] = number
    return context



@staff_member_required
@render_to("admin/localphones/add_tarif.html")
def tarif_add(request):
    context = {}
    cur = connections[BILLING_DB].cursor()
    context = get_ready_context(request, "New tarif")
    cur.execute("SELECT id,cost,name FROM billservice_addonservice where service_type='onetime'")
    external_numbers = cur.fetchall()
    context["all_regions"] = external_numbers
    context["all_numbs"] = external_numbers
    cur.execute("SELECT id,cost,name FROM billservice_addonservice where service_type='periodical'")
    external_numbers = cur.fetchall()
    transaction.commit_unless_managed(BILLING_DB)
    context["all_numbs1"] = external_numbers
    if request.POST:
        add_ok = True

        def Err(s):
            request.notifications.add(s, "error")

            add_ok = False



        if request.POST.get("cancel"):
            return HttpResponseRedirect("../")
        if request.POST.get("add"):
            try:
                name = request.POST.get("name")
                about = request.POST.get("about")
                price_add = request.POST.get("price_add")
                price_abon = request.POST.get("price_abon")
                precode = request.POST.get("precode")
                cur.execute("INSERT INTO external_numbers_tarif (name,about,price_add,price_abon,precode) VALUES ('" + name + "', '" + about + "', '" + price_add + "', '" + price_abon + "', '" + precode + "')")
                transaction.commit_unless_managed(BILLING_DB)
                request.notifications.add(_(u" numbers successfully added"), "success")
            except Exception, e:
                Err(e)
    return context

@staff_member_required
@render_to("admin/localphones/edit_tarif.html")
def tarif_edit(request, arg):
    context = get_ready_context(request, "Редактировать тариф")
    number = ExternalNumberTarif.objects.get(id=int(arg))
    cur = connections[BILLING_DB].cursor()

    context = get_ready_context(request, "Редактировать тариф")

    context["number"] = number

    context["readonly_number"] = False
    cur.execute("SELECT id,cost,name FROM billservice_addonservice where service_type='onetime'")
    external_numbers = cur.fetchall()
    context["all_regions"] = external_numbers
    context["all_numbs"] = external_numbers
    cur.execute("SELECT id,cost,name FROM billservice_addonservice where service_type='periodical'")
    external_numbers = cur.fetchall()
    context["all_numbs1"] = external_numbers
    transaction.commit_unless_managed(BILLING_DB)


    if request.POST:
        if request.POST.get("cancel"):
            return HttpResponseRedirect("../")
        if request.POST.get("set_tarif"):
            cur.execute("UPDATE external_numbers_tarif SET name='" + request.POST["name"] + "', about='" + request.POST["about"] + "', price_add='" + request.POST["add_price"] + "', price_abon='" + request.POST["add_abon"] + "',precode='" + request.POST["precode"] + "' WHERE id=" + arg)
            transaction.commit_unless_managed(BILLING_DB)
            request.notifications.add('Тарифынй план изменен', "success")


    return context


class ChangeTariffForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    tarif = forms.ModelChoiceField(queryset=ExternalNumberTarif.objects.all(), label=u'Тариф')





from django.http import HttpResponse
from django.template import RequestContext, loader
from django.utils.datastructures import SortedDict

def change_tariff(self, request, queryset):
    form = None
    if 'apply' in request.POST:
        form = ChangeTariffForm(request.POST)

        if form.is_valid():
            tarif = form.cleaned_data['tarif']

            count = 0
            for item in queryset:
                item.tarif_group = tarif
                item.save()
                count += 1

            self.message_user(request, "Тариф %s применен к %d номерам." % (tarif, count))
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = ChangeTariffForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

    t = loader.get_template('admin/localphones/change_tariff.html')
    c = RequestContext(request, {'items': queryset, 'form': form, 'title':u'Изменение тарифа'})
    return HttpResponse(t.render(c))

change_tariff.short_description = u"Изменить тариф"


def make_free(modeladmin, request, queryset):
    queryset.update(is_free=True, is_reserved=False)

make_free.short_description = u"Освободить"

def make_reserved(modeladmin, request, queryset):
    queryset.update(is_free=False, is_reserved=True)

make_reserved.short_description = u"Зарезервировать"

from telnumbers.models import TelNumbersGroup
from billing.models import BillserviceAccount


class ExternalNumberAdmin(admin.ModelAdmin):
    list_display = ("number", "account", "phone_numbers_group", "region", "assigned_at", "is_free", "is_reserved", "tarif_group", "sip_address", "dinging")
    list_filter = ("region", "is_free", "is_reserved", "tarif_group", "dinging")
    search_fields = ("number", "account__username", "phone_numbers_group__name", "tarif_group")
    actions = [change_tariff, make_free, make_reserved]
    date_hierarchy = "assigned_at"
    list_per_page = 1000
    fieldsets = [ (_(u"General information"), {'fields':["number", "account", "phone_numbers_group",
                                                      "region", "assigned_at", "is_free", "is_reserved", "tarif_group", "sip_address", "dinging", 'auth_user', 'date_deactivation']}),
                 ]



    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({'phone_numbers_group':TelNumbersGroup.objects.all(), 'billing_accounts':BillserviceAccount.objects.all()})
        return  super(ExternalNumberAdmin, self).render_change_form(request, context, add, change, form_url, obj)

    def get_urls(self):
        urls = super(ExternalNumberAdmin, self).get_urls()
#        for i, u in enumerate(urls):
#            if "_add" in u.name:
#                urls[i] = url("^add/$", numbers_add)
#            if "_change" in u.name and "_changelist" not in u.name:
#                urls[i] = url("^(.+)/$", number_edit)
        my_urls = patterns('', ("^add/$", numbers_add))
        return my_urls + urls

    def has_delete_permission(self, request, obj=None):
        if obj:
            if obj.is_free or obj.is_reserved:
                return True
        return False



    def get_actions(self, request):
        """
        Return a dictionary mapping the names of all actions for this
        ModelAdmin to a tuple of (callable, name, description) for each action.
        """
        # If self.actions is explicitally set to None that means that we don't
        # want *any* actions enabled on this page.

        actions = []

        # Gather actions from the admin site first
        # for (name, func) in self.admin_site.actions:
            # description = getattr(func, 'short_description', name.replace('_', ' '))
            # actions.append((func, name, description))

        # Then gather them from the model admin and all parent classes,
        # starting with self and working back up.
        for klass in self.__class__.mro()[::-1]:
            class_actions = getattr(klass, 'actions', [])
            # Avoid trying to iterate over None
            if not class_actions:
                continue
            actions.extend([self.get_action(action) for action in class_actions])

        # get_action might have returned None, so filter any of those out.
        actions = filter(None, actions)

        # Convert the actions into a SortedDict keyed by name
        # and sorted by description.
        actions.sort(lambda a, b: cmp(a[2].lower(), b[2].lower()))
        actions = SortedDict([
            (name, (func, name, desc))
            for func, name, desc in actions
        ])

        return actions

    class Media:
        js = ['/media/js/jquery.min.js',
              '/media/js/chosen.jquery.js',
              '/media/js/chosen_select.js']
        css = {'all':('/media/css/chosen.css',)}


class ExternalNumberAdminTarif(admin.ModelAdmin):
    list_display = ("id", "name", "price_add", "price_abon", "about", "precode")

    search_fields = ("name", "price_add", "price_abon")
    list_filter = ("name", "price_add", "price_abon")

    actions = None


    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        urls = super(ExternalNumberAdminTarif, self).get_urls()
        my_urls = patterns('', ("^add/$", tarif_add), ("^(.+)/$", tarif_edit))
        return my_urls + urls

    def has_delete_permission(self, request, obj=None):
        if obj:
            if obj.is_free or obj.is_reserved:
                return True
        return False

admin.site.register(ExternalNumber, ExternalNumberAdmin)
admin.site.register(ExternalNumberTarif, ExternalNumberAdminTarif)
