# coding: utf-8
from models import Internet_city, Internet_house, Internet_street, Connection_address, Internet_persons_for_connection, ConectionInputHomeAdmin, ScheduleConnectionInternet
from billing_models import Tariff as BillingTariff
from django.contrib import admin
from forms import Connection_address_Admin_Form, Connection_address_map_Admin_Form, Form_insert_home_administration, Connection_address_map, FormScheduleConnectionInternrt
from forms import Connection_address_Admin_Form
from forms import Connection_address_map_Admin_Form
import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Q


class InternetCityAdmin(admin.ModelAdmin):
    list_display = ('id', 'city')
    search_fields = ('city',)


class InternetStreetAdmin(admin.ModelAdmin):

    list_display = ('id', 'street_type', 'street')
    search_fields = ('street',)


class InternetHouseAdmin(admin.ModelAdmin):
    list_display = ('id', 'house')
    search_fields = ('house',)


class InternetPersonsForConnectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'persons')
    search_fields = ('persons',)



class BillingTariffAdmin(admin.ModelAdmin):
    list_display = ('name', 'access_parameters',)
    search_fields = ('id', 'name', 'description')

class Connection_address_Admin(admin.ModelAdmin):
    form = Connection_address_Admin_Form
    list_display = ('street', 'house', 'person_names', 'readiness_degree_sost', 'notes', 'home_adms')
    search_fields = ('street__street', 'house__house')
    list_filter = ('persons',)
    actions = None
    def changelist_view(self, request, extra_context=None):
        self.form.kwargs = {}
        extra_context = {}
        # передаем информацию о галочках в html
        fill_checkbox = ""
        p = 0
        readiness = ""
        while p <= 7:
            readiness = "readiness" + str(p)
            fill_checkbox_part = str(p) + ","
            if (request.POST.get(readiness)):
                fill_checkbox = fill_checkbox + fill_checkbox_part
            p = p + 1
        extra_context['fill_checkbox'] = fill_checkbox
        # передаем количество всех объектов
        obj_quantity = Connection_address.objects.all().count()
        extra_context['obj_quantity'] = obj_quantity
        return super(Connection_address_Admin, self).changelist_view(request, extra_context=extra_context)
    def queryset(self, request):
        qs_string = ""
        qs_string_count = 0;
        qs = super(Connection_address_Admin, self).queryset(request)
        # проверяем наличие post параметров для каждого readiness_degree если есть хотя бы один фильтруем qs иначе возвращаем super
        p = 0
        readiness = ""
        while p <= 7:
            readiness = "readiness" + str(p)
            if (request.POST.get(readiness)) :
                if (qs_string_count > 0):
                    qs_string = qs_string + '|' + request.POST.get(readiness)
                else:
                    qs_string = qs_string + request.POST.get(readiness)
                qs_string_count = qs_string_count + 1
            p = p + 1
        # print (qs_string)
        if (qs_string != ""):
            return qs.filter(eval(qs_string))
        return qs

class Connection_address_map_Admin(admin.ModelAdmin):
    form = Connection_address_map_Admin_Form
    list_display = ('street', 'house', 'person_names', 'readiness_degree_sost', 'notes',)
    search_fields = ('street__street', 'house__house')
    list_filter = ('persons',)
    actions = None
    def changelist_view(self, request, extra_context=None):
        response = super(Connection_address_map_Admin, self).changelist_view(request, extra_context)
        coordhotspot = response.context_data["cl"].query_set
        self.form.kwargs = {}
        extra_context = {}
        # coordhotspot = Connection_address.objects.filter(x__isnull=False, y__isnull=False, persons__id__isnull=False).all()
        extra_context['coordhotspot'] = coordhotspot
        # передаем информацию о галочках в html
        fill_checkbox = ""
        p = 0
        readiness = ""
        while p <= 7:
            readiness = "readiness" + str(p)
            fill_checkbox_part = str(p) + ","
            if (request.POST.get(readiness)):
                fill_checkbox = fill_checkbox + fill_checkbox_part
            p = p + 1
        extra_context['fill_checkbox'] = fill_checkbox
        # передаем количество всех объектов
        obj_quantity = Connection_address.objects.all().count()
        extra_context['obj_quantity'] = obj_quantity
        return super(Connection_address_map_Admin, self).changelist_view(request, extra_context=extra_context)
    def add_view(self, request, form_url='', extra_context=None):
        self.form.kwargs = {}
        extra_context = {}
        coordhotspot = Connection_address.objects.filter(x__isnull=False, y__isnull=False).all()
        extra_context['coordhotspot'] = coordhotspot
        return super(Connection_address_map_Admin, self).add_view(request, form_url='', extra_context=extra_context)
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = {}
        self.form.kwargs = {}
        coordhotspot = Connection_address.objects.filter(x__isnull=False, y__isnull=False).select_related()
        extra_context['coordhotspot'] = coordhotspot
        # get Connection_address_map id
        fp = request.get_full_path()
        fpnoslash = fp.split('/')
        lenfpnoslash = len(fpnoslash)
        camid = fpnoslash[lenfpnoslash - 2]
        # current hotspot coordinates
        try:
            curcoordhotspot = Connection_address.objects.select_related().get(x__isnull=False, y__isnull=False, id=camid)
            extra_context['curcoordhotspot'] = curcoordhotspot
        except Connection_address.DoesNotExist:
            pass
        return super(Connection_address_map_Admin, self).change_view(request, object_id, form_url='', extra_context=extra_context)


    def queryset(self, request):
        qs_string = ""
        qs_string_count = 0;
        qs = super(Connection_address_map_Admin, self).queryset(request)
        # проверяем наличие post параметров для каждого readiness_degree если есть хотя бы один фильтруем qs иначе возвращаем super
        p = 0
        readiness = ""
        while p <= 7:
            readiness = "readiness" + str(p)
            if (request.POST.get(readiness)) :
                if (qs_string_count > 0):
                    qs_string = qs_string + '|' + request.POST.get(readiness)
                else:
                    qs_string = qs_string + request.POST.get(readiness)
                qs_string_count = qs_string_count + 1
            p = p + 1
        # print (qs_string)
        if (qs_string != ""):
            return qs.filter(eval(qs_string))
        return qs





class InputFormHomeAdministration(admin.ModelAdmin):
    form = Form_insert_home_administration
    list_display = ('street', 'house', 'person_names', 'readiness_degree', 'notes')
    search_fields = ('city', 'street', 'house')





class ConectionListAdmin(admin.ModelAdmin):
    form = FormScheduleConnectionInternrt
    list_display = ('time',)

    def object_link(self):
        return 'time'


    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = {}
        self.form.kwargs = {}
        date_list = []
        date_now = datetime.datetime.now().date()
        weekday_str = ''
        for i in xrange(1, 51):
            if date_now.weekday() == 5 or date_now.weekday() == 6:
                weekday_str = weekday_str + str(date_now.day) + "-" + str(date_now.month) + "-" + str(date_now.year) + u'; '
                extra_context['weekday_str'] = weekday_str

            date_list.append(str(date_now.day) + "-" + str(date_now.month) + "-" + str(date_now.year))
            date_now = date_now + relativedelta(days=1)
        extra_context['date_list'] = date_list

        check_obj = ScheduleConnectionInternet.objects.get(id=object_id)
        list_id = ScheduleConnectionInternet.objects.filter(district=check_obj.district)
        str_id = '; '.join(t.date + u'_' + t.time for t in list_id)
        extra_context['list_bagr'] = str_id
        extra_context['obj_id'] = str(check_obj.date) + u'_' + str(check_obj.time)
        data_title_str = u''
        for li in list_id:
            data_title_str = data_title_str + str(li.date) + u'_' + str(li.time) + u'%' + li.adress.__unicode__() + u'  ' + u'кв.' + li.flat + ';'
        extra_context['data_title_str'] = data_title_str
        return super(ConectionListAdmin, self).change_view(request, object_id, form_url='', extra_context=extra_context)


    def add_view(self, request, form_url='', extra_context=None):
        self.form.kwargs = {}
        extra_context = {}
        date_list = []
        date_now = datetime.datetime.now().date()
        weekday_str = ''
        for i in xrange(1, 51):
            if date_now.weekday() == 5 or date_now.weekday() == 6:
                weekday_str = weekday_str + str(date_now.day) + "-" + str(date_now.month) + "-" + str(date_now.year) + u'; '
                extra_context['weekday_str'] = weekday_str
            date_list.append(str(date_now.day) + "-" + str(date_now.month) + "-" + str(date_now.year))
            date_now = date_now + relativedelta(days=1)
        extra_context['date_list'] = date_list
        extra_context['start_ajax_ivent'] = True

        return super(ConectionListAdmin, self).add_view(request, form_url='', extra_context=extra_context)


    def changelist_view(self, request, extra_context=None):

        self.form.kwargs = {}
        extra_context = {}
        check_obj = ScheduleConnectionInternet.objects.all()
        zakazi_str = '; '.join(str(t.id) + '%' + t.date + u'_' + t.time + '%' + t.district + '%' + t.adress.__unicode__() + u'  ' + u'��.' + t.flat for t in check_obj)
        extra_context['zakazi_str'] = zakazi_str
        date_list = []
        date_now = datetime.datetime.now().date()
        weekday_str = ''
        for i in xrange(1, 51):
            if date_now.weekday() == 5 or date_now.weekday() == 6:
                weekday_str = weekday_str + str(date_now.day) + "-" + str(date_now.month) + "-" + str(date_now.year) + u'; '
                extra_context['weekday_str'] = weekday_str

            date_list.append(str(date_now.day) + "-" + str(date_now.month) + "-" + str(date_now.year))
            date_now = date_now + relativedelta(days=1)
        extra_context['date_list'] = date_list


        return super(ConectionListAdmin, self).changelist_view(request, extra_context=extra_context)


#     class Media:
#         js = ['/media/js/zakazy_admin.js']


admin.site.register(Connection_address_map, Connection_address_map_Admin)
admin.site.register(Connection_address, Connection_address_Admin)
admin.site.register(Internet_city, InternetCityAdmin)

admin.site.register(Internet_persons_for_connection, InternetPersonsForConnectionAdmin)
admin.site.register(BillingTariff, BillingTariffAdmin)
admin.site.register(ConectionInputHomeAdmin, InputFormHomeAdministration)
admin.site.register(ScheduleConnectionInternet, ConectionListAdmin)



