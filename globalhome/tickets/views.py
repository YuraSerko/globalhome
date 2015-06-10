# coding: utf-8

from lib.decorators import render_to, login_required
from django.http import HttpResponseRedirect, Http404
from tickets.models import Category, Tags, Get_SubEvent, Venue #SubEvent,
from hotspot.views import hotspot_identity
from django.db.models import Q
import urllib
import json 
import time
#from models import Ticket
import traceback


def price_same(ll):
    for l1 in ll:
        count = 0
        for l2 in ll:
            if l1==l2:
                count = count+1
        if count>1:
            for c in range(count-1):
                ll.remove(l1)
    return ll


old_region = None
def menu_lists(category_list, tags_list): # Если нет тегов по категрии, то и меню не будет. Отображаются теги по существующим событиям в регионе
    categ = Category.objects.all().filter(id__in = price_same(category_list))
    tags = Tags.objects.all().filter(alias__in = tags_list)
    return categ, tags, category_list, tags_list


def db_request(region_events):
    category_list = []
    tags_list = []
    for ob in region_events:
        for tag in ob.tags_category.all():
            tags_list.append(tag.alias)
            if tag.category:
                category_list.append(tag.category.id)
    return category_list, tags_list


def menu(request, region_events, rigion= False):
    global category_list
    global tags_list
    global old_region
    context = {}

    if old_region == region: # Запрос к базе осуществляется только при смене региона чтобы не грузить с базы тоже самое
        pass
    else:
        category_list, tags_list = db_request(region_events)
    try:
        categ, tags, category_list, tags_list = menu_lists(category_list, tags_list)
    except NameError:
        category_list, tags_list = db_request(region_events)
        categ, tags, category_list, tags_list = menu_lists(category_list, tags_list)
    context['tags'] = tags
    context['category'] = categ
    old_region = region
    return context


def search_ponominalu(request, region=False):
    context = {}
    region_events = Get_SubEvent.objects.filter(venue__region_id = region)
    context.update(menu(request, region_events, region))

    if request.GET.get('q_search'):

        context['ticket_page'] = False
        context['ticket_page'] = False
        context['grouptag'] = False
        context['buy_ticket_page'] = False
        context['sector_view'] = False
        context['venue_view_page'] = False
        context['no_results'] = False
        search = Get_SubEvent.objects.filter(title__icontains = request.GET.get('q_search')).filter(venue__region_id = region ).filter(deleted = False)
        if search.count() >1:
            context['dates'] = True
            #search = search[0]
        if search:
            context['search_results'] = search
        else:
            context['no_search_results'] = True

    return context


region = None
class Base():
    ref_codes = { 0:'all_events_ref_c', 1:'moscow_region', 8:'sanp_region', 19:'ekb__region', 17:'krd_region', 77:'tms_region',
                  90:'petr_region', 9:'nnov_region', 79:'ivan_region', 166: 'sochi_region', 31:'novs_region',
                15: 'kazan_region', 59: 'vologda_region', 72:'belgor_region', 179: 'cher_region', 3: 'tver_region', 58: 'kaluga_region',
                11: 'chebok_region', 75: 'krasno_region', 177: 'vluki_region', 67: 'ijevsk_region', 124: 'orel_region'}
    regions = { 1:u'Москва', 8:u'Санкт-Петербург', 19:u'Екатеринбург', 17:u'Краснодар', 77:u'Томск', 
               90:u'Петрозаводск', 9:u'Нижний Новгород', 79:u'Иваново', 166: u'Сочи', 31:u'Новосибирск',
                15: u'Казань', 59: u'Вологда', 72:u'Белгород', 179: u'Череповец', 3: u'Тверь', 58: u'Калуга',
                11: u'Чебоксары', 75: u'Красноярск', 177: u'Великие Луки', 67: u'Ижевск', 124: u'Орёл'} 
    def base(self, request, region = False):
        context = {}
        if region:
            context['regions'] = self.regions
            context['region'] = region
            context['region_value'] = self.regions[int(region)]
            context['ref_code'] = self.ref_codes[int(region)]
        else:
            context['regions'] = self.regions
            context['region_value'] = self.regions[1]
            
        if request.POST.has_key('region_id'):
            region = request.POST.get('region_id')
            events = Get_SubEvent.objects.filter(venue__region_id = region ).filter(deleted = False) 
            if events:
                context['region'] = region
                context['region_value'] = regions[int(region)]

        return context


@render_to('tickets.html')
def ponominalu_tickets(request):
    context = {}
    global region
    b = Base()
    regions = b.regions
    if region:
        events = Get_SubEvent.objects.filter(venue__region_id = region ).filter(deleted = False)
        context['region'] = region
        context['region_value'] = regions[int(region)]
    else:
        region = 1
        events = Get_SubEvent.objects.filter(venue__region_id = 1 ).filter(deleted = False) # По умолчанию Москва
        context['region'] = region
        context['region_value'] = regions[int(region)]
    
    context['ticket_page'] = True
    context['regions'] = regions
    if request.POST.has_key('region_id'):
        region = request.POST.get('region_id')
        events = Get_SubEvent.objects.filter(venue__region_id = region ).filter(deleted = False) 
        context['region'] = region
        context['region_value'] = regions[int(region)]

    context['all_events'] = events
    context.update(hotspot_identity(request))
    context.update(search_ponominalu(request, region))

    return context


@render_to('tickets.html')
def grouptag(request, tag, region):
    context = {}
    b = Base()
    context['grouptag_page'] = True
    sub_event = Get_SubEvent.objects.filter(tags_category__alias = tag).filter(venue__region_id = region).filter(deleted = False)
    if sub_event:
        context['grouptag'] = sub_event
    else:
        context['no_results'] = True
    context.update(b.base(request, region))
    context.update(hotspot_identity(request))
    context.update(search_ponominalu(request, region))
    return context


@render_to('tickets.html')
def buy_ticket(request, alias, region):
    context = {}
    b = Base()
    #print date
    context['buy_ticket_page'] = True
    event = Get_SubEvent.objects.filter(event__alias = alias).filter(venue__region_id = region).filter(deleted = False) #.filter(str_date = date)
    if event:
        context['buy_event'] = event
    else:
        raise Http404
    if request.POST.has_key('date_event'):
        event = Get_SubEvent.objects.filter(str_date = request.POST.get('date_event')).filter(deleted = False)
    context.update(b.base(request, region))
    context.update(hotspot_identity(request))
    context.update(search_ponominalu(request, region))
    return context


#===============================================================================
# def get_sector(ponominalu_sector_id, event): # По этой функции идет отрисовка всевозможных мест сектора
#     context = {}
#     color = {1:'magenta_1', 2:'green', 3:'blue_p', 4:'pink', 5:'dark-green', 6:'grey',  7:'orange', 8:'blue', 9:'brown',
#              10:'dark_khaki', 11:'gold', 12:'red', 13:'magenta', 14:'slate_blue', 15:'teal', 16:'cornflowerblue',
#              17:'magenta_1', 18:'green', 19:'blue_p', 20:'pink', 21:'dark-green', 22:'grey',  23:'orange', 24:'blue', 25:'brown',
#              26:'dark_khaki', 27:'gold', 28:'red', 29:'magenta', 30:'slate_blue', 31:'teal', 32:'cornflowerblue',
#              33:'magenta_1', 34:'green', 35:'blue_p', 36:'pink', 37:'dark-green', 38:'grey',  39:'orange', 40:'blue', 41:'brown'}
#     number_values = []
#     n = {}
#     list_n = []
#     data = urllib.urlopen('http://api.cultserv.ru/jtransport/partner/get_sector?sector_id=%s&session=123'%(ponominalu_sector_id)).read()
#     data_python = json.loads(data)
# 
#     for key, value in data_python.items():
#         print key
# 
#         if key == 'message':
#              
#             for key, value in value.items():
#                 if key == 'title':
#                     sector_title =  value
#                 if key == 'content':
#                     for value in value:
#                         for key, value in value.items():
#                             if key == 'number':
#                                 number_values.append(value)
#                                 number = value
#                             if key == 'seats':
#                                 for row in value:
#                                     for k, v in row.items():
#                                         if k == 'n':
#                                             list_n.append(v)
#                                 n[number] = list_n
#                                 seat_count = len(list_n)
#                                 list_n = []
#     raw = []
#     seats = []
#     exist = {}
#     same_list = []
#     no = True
#     for e in event.tickets.all(): # Разделение на разные словари, словарь с ключем ряда имеет массив мест
#         #print e.raw
#         raw.append(e.raw)
#         if no:
#             same = e.raw
#             no = False
#         if e.raw == same:
#             seats.append(e.seat)
#             exist[e.raw] = seats
#             same = e.raw
#             same_list.append(e.price)
# 
#         else:
#             seats = []
#             seats.append(e.seat)
#             same_list.append(e.price)
#             exist[e.raw] = seats
#             no = True
#     table_result = u'''<h4 class = "delvr fLeft instead" >%s</h4>
#     <div class = "delvr_1"> Доступно билетов: %s </div>'''%(sector_title, event.tickets.all().count())
# 
#     price_numbers = [int(el) for el in price_same(same_list)]
#     for price in sorted(price_numbers, reverse=False):
#         for i, e in enumerate(event.tickets.all(), start = 1): # попробовать может на одном ряду разделить разные по цвету прайсы
#             if int(e.price) == int(price):
#                 print e.price
#                 number_color = int(e.raw) # i
#         #print color[number_color],
#         #print "  |"+str(number_color)
#         table_result += u'''<div class = "color_div_price %s"></div><div class = "price_inline">%s Р</div>'''%(color[number_color],price)
# 
#     table_result += u'''<div id = "table_overflow"><table id = 'table_all_seats'><tr><td >Ряд</td>'''
#     for seat in range(0, seat_count):
#         table_result += u'<td class = "sector_scene" >Сцена</td>'
#     table_result +=u'''</tr>'''
# 
#     green = None
#     for number in number_values:
#         # Добавил этот if и вмест 2 нижнего if сделал elif
#         if  unicode(number) in raw:
#             green = True
#             table_result += u'''
#                         <tr id = "%s" ><td  >%s</td> 
#                                         '''%(number, number)
#         elif number == 0:
#             table_result += u'''
#                         <tr><td class = "space %s"></td> 
#                                         '''%(number)
#         else:
#             table_result += u'''
#                         <tr><td>%s</td> 
#                                         '''%(number)
#         yes = False
#         for seat in n[number]:
#             try:
#                 exist[str(number)]
#                 yes = True
#             except: 
#                 pass
#             if yes:
#                 if unicode(seat) in exist[str(number)]:
#                     try:
#                         # Не правильно ! ! !
#                         ticket_id = get_tickets(event.id, ponominalu_sector_id, event.id)
#                         print color[number]
#                         table_result +='''<td id = "%s_%s" class = "%s"><a onclick = "ajax_addTicket(%s, %s)" href = "#null">%s</a></td>
#                         '''%(number, seat, color[number], seat, ponominalu_sector_id, seat) #ticket_id , event.id, ponominalu_sector_id,
#                     except KeyError:
#                         error = traceback.format_exc()
#                         send_email(u'Ошибка в приложении по билетам', u'Ошибка в словаре цветов для отображения мест в билетах, трейсбек ошибки: %s'%(error) , settings.DEFAULT_FROM_EMAIL, ["Zz1n@globalhome.su", 'sales@globalhome.su', 'noc@globalhome.su'])
#                 elif seat == 0:
#                     table_result +=u'''<td class = "space %s" ></td>
#                     '''%(seat)
#                 else:
#                     table_result +='''<td >%s</td>
#                     '''%(seat)
#             elif seat == 0:
#                 table_result +=u'''<td class = "space %s" ></td>
#                 '''%(seat)
#             else:
#                 table_result +='''<td class = "gggg">%s</td>
#                 '''%(seat)
#         table_result += u'''</tr>'''
#     table_result += u'''</table></div> <!--table_overflow-->''' #</tr>
#     return table_result 
#===============================================================================


@render_to('tickets.html')
def sector_view(request, alias, date, time, sector_id):
    context = {}
    context['sector_view'] = True
    context['event_object'] = Get_SubEvent.objects.filter(Q(event__alias=alias), Q(str_date = date) ).filter(deleted = False)
    if request.POST.has_key('ticket_seat'):
        pass
    try:
        event = Get_SubEvent.objects.get(event__alias=alias).filter(deleted = False)
    except Get_SubEvent.MultipleObjectsReturned: # Если на одно событие присутствуют несколько дат
        event = Get_SubEvent.objects.filter(event__alias=alias).filter(deleted = False)[0]
    get_tickets(event.id, sector_id, event.id)
 
    context['sector_seats'] = get_sector(sector_id, event)
    context.update(hotspot_identity(request))
    context.update(search_ponominalu(request))
    return context


@render_to('tickets.html')
def venue_view(request, alias, region):
    context = {}
    b = Base()
    context['venue_view_page'] = True
    venue = Venue.objects.get(alias = alias) #__contains
    #print venue
    context['venue_event'] = venue

    context.update(b.base(request, region))
    context.update(hotspot_identity(request))
    context.update(search_ponominalu(request))
    return context
