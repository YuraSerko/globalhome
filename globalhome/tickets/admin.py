# coding: utf-8
from django.contrib import admin
from tickets.models import Venue, Event, SubEvent, Get_SubEvent, \
        Category, Tags #, Ticket , Sectors


class Category_Admin(admin.ModelAdmin):
    list_display = ('id', 'title', 'count', 'category_description') 
    search_fields = ('id', 'title')


class Get_SubEvent_Admin(admin.ModelAdmin):
    list_display = ('id', 'deleted', 'sub_event_id', 'title', 'str_date', 'commission', 'region') 
    search_fields = ('id', 'title')
    def region(self, request):
        return Get_SubEvent.objects.get(id = request.id).venue.region_id

class SubEvent_Admin(admin.ModelAdmin):
    list_display = ('id', 'deleted', 'title') 
    search_fields = ('id', 'title')


class Event_Admin(admin.ModelAdmin):
    list_display = ('id', 'title', 'alias') 
    search_fields = ('id', 'title')


class Tags_Admin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'alias', 'count', 'show') 
    search_fields = ('id', 'title')


class Venue_Admin(admin.ModelAdmin):
    list_display = ('id', 'title', 'address', 'alias', 'region_id', 'description_text') 
    search_fields = ('id', 'title')


#===============================================================================
# class Sectors_Admin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'count', 'min_price', 'max_price', 'sectors_id_pomominalu', 'admission') 
#     search_fields = ('sectors_id_pomominalu', 'title')
#===============================================================================


#===============================================================================
# class Ticket_Admin(admin.ModelAdmin):
#     list_display = ('id', 'id_ticket_ponominalu', 'raw', 'seat', 'price') 
#     search_fields = ('id_ticket_ponominalu',)
#===============================================================================


#######################################################
admin.site.register(Get_SubEvent, Get_SubEvent_Admin)
admin.site.register(SubEvent, SubEvent_Admin)
admin.site.register(Event, Event_Admin)
admin.site.register(Category, Category_Admin)
admin.site.register(Tags, Tags_Admin)
admin.site.register(Venue, Venue_Admin)
#admin.site.register(Sectors, Sectors_Admin)
#admin.site.register(Ticket, Ticket_Admin)
