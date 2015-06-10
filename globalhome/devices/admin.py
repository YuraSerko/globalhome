# coding: utf-8
from django.contrib import admin
from devices.models import Devices
from lib.decorators import render_to
from django.views.decorators.csrf import csrf_protect 
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from content import BaseContentAdmin

#@render_to("admin/tt2.html")


class DevicesAdmin(BaseContentAdmin):
    
    list_display = ('name', 'url', 'img', 'text', 'initial_fee', 'abonent_fee')  # отображаем калонками
    list_display_links = ('name',) # какие поля доступны для изменения
    search_fields = ('name',)  # вверху  поиск
    #list_filter = ('name',)  # справа  фильтр 
#    date_hierarchy = 'time' # вверху  новая панель по выбору месяца 
#    ordering = ('-time',) # сартировка по дате 

    actions = ["change"] # добавляет  поле в  всплывающий список  для  редактирование  выбранных  обьектов
    
    
    '''
    def change(self, request, queryset):
        """
            Админское действие - массовая смена группы телефонной зоны у выбранных зон
        """
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect("/change/?ids=%s" % ",".join(selected))
    change.short_description = _(u"Dobawili pole")
    
    add_form_template = "admin/tt2.html"
    '''
    

    #запретить добавление
    #def has_add_permission(self, request):
    #    return False
    # запретить удаление
#    def has_delete_permission(self, request, obj=None): 
#        return False
    
#    fields = ('name', 'text', 'time',) # в каком порядке отображать поля (почемуто неработает)
#    filter_horizontal = ('text',) # выбор несколких  через Ctrl (только с ManyToManyField)
#    raw_id_fields = ('name',) # добавляет иконку с увеличительным стеклом для поиска по выбранному id (только с ForeignKey)  
     
    
        
    
admin.site.register(Devices, DevicesAdmin)

