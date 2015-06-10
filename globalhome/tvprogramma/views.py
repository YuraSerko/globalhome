# coding: utf-8
from tvprogramma.models import TvChannels, TvForecastSources, TvForecast
from django.db.models import Q
from django.db.models import Max
from hotspot.views import hotspot_identity
from lib.decorators import render_to
import datetime
#======================================================================================================================
def breakList(list, step):
    #print 'BREAK_LIST'
    new_list_ext = []
    list_dict = {}
    j = 1
    
    start = 0
    end = step
    while start<=len(list):
        
        l = list[start:end]
        start = end
        end = end + step
        new_list_ext.append(l)
        l = []
    for ll in new_list_ext:
        list_dict[j] = ll
        j=j+1
        
    return list_dict


def get_current_time_id(day_part, date, chid, source, cur_minute, cur_hour):  # chid = item.id
    
    #print day_part, date, chid, source, cur_minute, cur_hour
    if day_part == 1:
        tv_forecast_objs = TvForecast.objects.filter( Q(date = date),   Q(channel = chid), Q(source =source), Q(time_minute__lte = cur_minute),  Q(time_hour = cur_hour),)
        if tv_forecast_objs.count() == 0:
            tv_forecast_objs = TvForecast.objects.filter( Q(date = date),   Q(channel = chid), Q(source =source),  Q(time_hour__lt = cur_hour),  Q(time_hour__gte=5), Q(time_hour__lte=23)      )
            if tv_forecast_objs.count() != 0:
                tv_m_qs = TvForecast.objects.filter( Q(date = date),   Q(channel = chid), Q(source =source),  Q(time_hour__lt = cur_hour),  Q(time_hour__gte=5), Q(time_hour__lte=23)).aggregate(Max('id'))
        else:
            tv_m_qs = TvForecast.objects.filter( Q(date = date),   Q(channel = chid), Q(source =source),  Q(time_hour = cur_hour), Q(time_minute__lte = cur_minute),     ).aggregate(Max('id'))
        
    
    if day_part == 2:
        tv_forecast_objs = TvForecast.objects.filter( Q(date = date),   Q(channel = chid), Q(source =source), Q(time_minute__lte = cur_minute),  Q(time_hour = cur_hour),)
        if tv_forecast_objs.count() == 0:
            tv_forecast_objs = TvForecast.objects.filter( Q(date = date),   Q(channel = chid), Q(source =source),  Q(time_hour__lt = cur_hour),  Q(time_hour__gte=0)     )
            if tv_forecast_objs.count() == 0:
                tv_forecast_objs = TvForecast.objects.filter( Q(date = date),   Q(channel = chid), Q(source =source),  Q(time_hour__gte=23), Q(time_hour__gte=5))
                if tv_forecast_objs.count() != 0:
                    tv_m_qs = TvForecast.objects.filter( Q(date = date),   Q(channel = chid), Q(source =source),  Q(time_hour__gte=23), Q(time_hour__gte=5)).aggregate(Max('id'))
            else:
                tv_m_qs = TvForecast.objects.filter( Q(date = date),   Q(channel = chid), Q(source =source),  Q(time_hour__gte=23), Q(time_hour__gte=5)).aggregate(Max('id'))
        else:
            tv_m_qs = TvForecast.objects.filter( Q(date = date),   Q(channel = chid), Q(source =source), Q(time_minute__lte = cur_minute),  Q(time_hour = cur_hour),).aggregate(Max('id'))    
    
        
        
    try:
        tv_cur_id = tv_m_qs['id__max']
    except:
        tv_cur_id = None
    
    return tv_cur_id


def take_channels_date_channel(request, date, channel_name):
    context = {}
    channel_list = [] #список каналов с актуальными записями
    channel_dictionary = {}
    channel_with_forecast_dict = {}
    select_list_date = [] # даты для select
    cur_time_dict = {} #словарь текущей даты
   
    date_list = []
    date_dictionary = {}
    
    
    #если нет даты дата равна текущей
    if date == "None":
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    #определяем текущее время часы +  минуты (24 часа)
    time = datetime.datetime.now().strftime("%H-%M")
    time_splitted = time.split('-')
    cur_hour = time_splitted[0]
    cur_minute = time_splitted[1]
    if 5<=int(cur_hour)<=23 :
        day_part = 1
    if 0<=int(cur_hour)<5:
        day_part = 2
    

    # нету данных о канале
    if channel_name == "None":
        #теперь берем из модели где каналы
        channel_distinct = TvChannels.objects.all().order_by('id')
        for item in channel_distinct: 
            tv_forecast_objs = TvForecast.objects.filter( date = date,   channel = item.id, source =2).order_by('id') # 2-источник
            
            if tv_forecast_objs.count()==0:
                tv_forecast_objs = TvForecast.objects.filter( date = date,   channel = item.id, source =1).order_by('id') # 1-источник
                source= 1
            else:
                source=2
                
                
            if tv_forecast_objs.count()!=0:
                #канал с программой
                channel_with_forecast_dict[item.id] = tv_forecast_objs 
                #далее выясняем какая запись в каждом qs является текущей относительно настоящего времени
                if date ==  datetime.datetime.now().strftime("%Y-%m-%d"):
                    tv_cur_id = get_current_time_id(day_part, date, item.id, source, cur_minute, cur_hour)
                else:
                    tv_cur_id = None
                channel_list.append( [item.id,tv_cur_id] ) # id канала, id записи с текущеим временем
                
                        
        #делим список каналов на три равных столбца        
        channel_dictionary = breakList(channel_list, 3)
    
    #===========================================================================================================================================================
    # есть данные о канале
    if channel_name !="None":
        channel_obj =  TvChannels.objects.get(channel_name_eng = channel_name)
        #записи по 2 источнику
        tv_dates_distinct = TvForecast.objects.filter(channel = channel_obj, source = 2, date__gte=(datetime.datetime.now()).strftime("%Y-%m-%d")).order_by('date').distinct('date')
        
        #если нет записей  по 2 му источнику
        if tv_dates_distinct.count() == 0:
            tv_dates_distinct = TvForecast.objects.filter(channel = channel_obj, source = 1, date__gte=(datetime.datetime.now()).strftime("%Y-%m-%d")).order_by('date').distinct('date')
            source=1
        else:
            source=2
        
        
        if tv_dates_distinct.count() !=0:
            for item in tv_dates_distinct: #для каждой даты
                tv_forecast_objs = TvForecast.objects.filter(channel=channel_obj,source =source, date=item.date ).order_by('id')
                channel_with_forecast_dict[item.date] = tv_forecast_objs 
                
                #далее выясняем какая запись в каждом qs является текущей относительно настоящего времени если дата равна текущей
                if item.date.strftime("%Y-%m-%d") ==  datetime.datetime.now().strftime("%Y-%m-%d"):
                    tv_cur_id = get_current_time_id(day_part, item.date, channel_obj.id, source, cur_minute, cur_hour)
                else:
                    tv_cur_id = None
                date_list.append([item.date, tv_cur_id]) # [[datetime.datetime(2015, 1, 27, 0, 0), 283391], ...
                

        # channel list толкько distict
        tv_forecast_objs = TvForecast.objects.all().distinct('channel')
        for tv_forecast_obj in tv_forecast_objs:
            channel_list.append(tv_forecast_obj.channel.id)
            

        date_dictionary = breakList(date_list, 3)
    

    select_objs = TvForecast.objects.filter(date__gte=(datetime.datetime.now()).strftime("%Y-%m-%d")).order_by('date').distinct('date')
    select_list_date = []
    for select_obj in select_objs:
        select_list_date.append(select_obj.date)
    
      
    context['channel_with_forecast_dict'] = channel_with_forecast_dict    #SELECT LIST {4: [<TvForecast: TvForecast object>...
    context['select_list_date'] = select_list_date  
    context['channel_objs'] = TvChannels.objects.all().order_by('id') 
    context['channel_list'] = channel_list #для выбора канала в select
    context['now_d'] = datetime.datetime.now().strftime("%Y-%m-%d")
    context['selected_date'] = date
    
    
    if channel_name == "None":
        context['dictionary_param'] = channel_dictionary #{1: [4, 7, 14], 2: [29]}   
        context['channel_exist'] = False


    if channel_name != "None":
        context['dictionary_param'] = date_dictionary   
        context['date_list'] = date_list
        context['channel_exist'] = True
        context['channel_info'] = channel_obj
       
    
    context['tv_forecast'] = True
    context.update(hotspot_identity(request))
    
    return context

         
@render_to('tv_forecast.html')
def tv_forecast_date(request, date):
    context = take_channels_date_channel(request, date, "None")
    return context

@render_to('tv_forecast.html')
def tv_forecast(request):
    context = take_channels_date_channel(request, "None", "None")
    return context

#теперь с определенным каналом на все даты
@render_to('tv_forecast.html')
def tv_forecast_channel(request, channel_name):
    context = take_channels_date_channel(request, "None", channel_name)
    return context