# coding: utf-8
from django.contrib import admin
from hotspot.models import Prefecturs, DistrictAdministration, HomeAdministration, HotSpotQueryStatistic, HotSpotComplaint, HotSpotReview, Games, \
    MobiOrganizationsUserChanges, MobiOrganizationsUnique, HotSpot_Bad_Video_Link, Comments_Of_Video, Video, VideoGenre, Video_Rate, ActiveSession
from forms import PrefectursAdminForm, DistrictAdministrationAdminForm, HomeAdministrationAdminForm
from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required
from lib.decorators import render_to, login_required
from django.shortcuts import  HttpResponse
from django.http import Http404
from django.conf import settings
from  yandex_maps import api
import shutil
from time import localtime, strftime
from xml.dom.minidom import parse
from lxml import html, etree
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import subprocess
import os
from djcelery.admin import TaskMonitor
from djcelery.admin_utils import action



class Games_Admin(admin.ModelAdmin):
    list_display = ('game_name', 'banner', 'img', 'http')

class PrefectursAdmin(admin.ModelAdmin):
    form = PrefectursAdminForm
    list_display = ('id', 'name', 'adress', 'x', 'y')
    list_display_links = ('id', 'name',)
    search_fields = ('id', 'name', 'adress', 'x', 'y', 'subway_station',)

class DistrictAdministrationAdmin(admin.ModelAdmin):
    form = DistrictAdministrationAdminForm
    list_display = ('id', 'name', 'adress', 'x', 'y', 'prefecturs',)
    list_display_links = ('id', 'name',)
    search_fields = ('id', 'name', 'adress', 'x', 'y', 'subway_station', 'prefecturs',)

class HomeAdministrationAdmin(admin.ModelAdmin):
    form = HomeAdministrationAdminForm
    list_display = ('id', 'name', 'adress', 'x', 'y', 'district_administration',)
    list_display_links = ('id', 'name',)
    search_fields = ('id', 'name', 'adress', 'x', 'y', 'subway_station', 'district_administration')


class HotSpotQueryStatisticAdmin(admin.ModelAdmin):
    list_display = ('query_string', 'date_time')
    list_display_links = ('query_string',)
    search_fields = ('id', 'query_string', 'date_time')
    list_filter = ('date_time',)

class HotSpotComplaintAdmin(admin.ModelAdmin):
    list_display = ('contact_face', 'telnumber', 'mail', 'date', 'was_treated')
    list_display_links = ('contact_face',)
    search_fields = ('contact_face', 'telnumber', 'mail', 'date', 'was_treated', 'adres')
    list_filter = ('date', 'was_treated')
    exclude = ('type',)

    def queryset(self, request):
        qs = super(HotSpotComplaintAdmin, self).queryset(request)
        return qs.filter(type='complaint')

class HotSpotReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact_face', 'telnumber', 'mail', 'date', 'was_treated')
    list_display_links = ('id', 'contact_face',)
    search_fields = ('contact_face', 'telnumber', 'mail', 'date', 'was_treated', 'adres')
    list_filter = ('date', 'was_treated')
    exclude = ('type',)

    def queryset(self, request):
        qs = super(HotSpotReviewAdmin, self).queryset(request)
        return qs.filter(type='review')

class MobiOrganizationsUserChangesAdmin(admin.ModelAdmin):
    list_display = ('id', 'org_name_original')
    list_filter = ('applied',)
    fields = ('u_org_name', 'u_address', 'u_phone', 'u_url', 'u_hours', 'user_name', 'user_email', 'applied', 'to_del')



    class Media:
        js = ['/media/js/apply_changes_org_admin.js']
    def get_urls(self):
        urls = super(MobiOrganizationsUserChangesAdmin, self).get_urls()
        my_urls = patterns("", (r"^apply_changes/$", apply_changes),
                           (r"^start_scripts/$", start_scripts))
        return my_urls + urls





    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = {}
        self.form.kwargs = {}
        # get mobiorganizationsuserchanges id
        fp = request.get_full_path()
        fpnoslash = fp.split('/')
        lenfpnoslash = len(fpnoslash)
        org_user_change = fpnoslash[lenfpnoslash - 2]

        org_user_change_obj = MobiOrganizationsUserChanges.objects.get(id=org_user_change)
        # передадим в html данные о текущем состоянии организации в базе
        extra_context['cur_org_name'] = org_user_change_obj.org_id.org_name
        extra_context['cur_org_address'] = org_user_change_obj.org_id.address
        extra_context['cur_org_tel'] = org_user_change_obj.org_id.phone
        extra_context['cur_org_url'] = org_user_change_obj.org_id.url
        extra_context['cur_org_hours'] = org_user_change_obj.org_id.hours
        extra_context['deleted'] = org_user_change_obj.org_id.deleted
        return super(MobiOrganizationsUserChangesAdmin, self).change_view(request, object_id, form_url='', extra_context=extra_context)




@staff_member_required
def apply_changes(request):
    if not request.POST.has_key('zayavka_id'):
        raise Http404

    zayavka_id = request.POST.get('zayavka_id')

    # находим заявку в базе
    zayavka_obj = MobiOrganizationsUserChanges.objects.get(id=zayavka_id)
    # находим организацию для изменения
    org_obj = MobiOrganizationsUnique.objects.get(id=zayavka_obj.org_id.id)
    # отменить или принять заявку
    action = request.POST.get('action')

    if action == 'ok':  # если применить зафвку
        u_org_name = request.POST.get('u_org_name')
        u_org_address = request.POST.get('u_org_address')
        u_org_phone = request.POST.get('u_org_phone')
        u_org_url = request.POST.get('u_org_url')
        u_org_hours = request.POST.get('u_org_hours')
        to_del = request.POST.get('to_del')

        if to_del == 'on':

            # сохраняем измениния для заявки
            zayavka_obj.u_org_name = u_org_name
            zayavka_obj.u_address = u_org_address
            zayavka_obj.u_phone = u_org_phone
            zayavka_obj.u_url = u_org_url
            zayavka_obj.u_hours = u_org_hours
            zayavka_obj.applied = True
            zayavka_obj.save()
            # удаляем организацию
            org_obj.deleted = True
            org_obj.save()
            str = 'ok'

        else:  # если организация не  помечена к удалению

            if u_org_name != '':
                org_obj.org_name = u_org_name

            # геокодировать новый адрес
            if u_org_address != '':
                org_obj.address = u_org_address
                api_key = settings.YANDEX_MAPS_API_KEY
                # geocoding yandex
                pos = api.geocode(api_key, u_org_address)
                org_obj.x = pos[0]
                org_obj.y = pos[1]

            if u_org_phone != '':
                org_obj.phone = u_org_phone

            if u_org_url != '':
                org_obj.url = u_org_url

            if u_org_hours != '':
                org_obj.hours = u_org_hours

            # сохраняем измениния для заявки

            zayavka_obj.u_org_name = u_org_name
            zayavka_obj.u_address = u_org_address
            zayavka_obj.u_phone = u_org_phone
            zayavka_obj.u_url = u_org_url
            zayavka_obj.u_hours = u_org_hours

            zayavka_obj.applied = True
            zayavka_obj.save()
            # сохраняем изменения для организации
            org_obj.save()
            str = 'ok'

    else:  # если отклонить заявку
        zayavka_obj.applied = True
        zayavka_obj.save()
        str = 'cancel'

    return HttpResponse(str)

#=========================================================================================================
# функция делает xml файл на основе таблицы  MobiOrganizationsUnique
def orgs_to_xml(org_type):
    print 'making xml starts'
    print 'org_type %s' % org_type
    working_time = u'время работы:'
    edit = u'редактировать'
    some_orgs = u'несколько банков'
    tel = u'тел.:'

    f = open("scripts/php_script/myLayer.xml", 'rt')
    data = parseString(f.read())
    f.close()

    org_objs = MobiOrganizationsUnique.objects.filter(org_type=org_type, deleted=False)
    for org_obj in org_objs:
        # для совпадений
        if (org_obj.equal_coord_range != None) and (org_obj.equal_coord_range == 1):
            # объединяем все точки в одну
            # получим список всех объектов с координатми как того что у кот есть запись в таблице
            org_coincidence_objs = org_objs.filter(x=org_obj.x, y=org_obj.y)
            i = 1
            str_ex = ''
            for org_coincidence_obj in org_coincidence_objs:
                str_name = '<font size="3"; color="darkblue">' + org_coincidence_obj.org_name + '</font>'

                if org_coincidence_obj.url != 'nourl':
                    str_url = '<a href ="' + org_coincidence_obj.url + '">' + org_coincidence_obj.url + '</a>'
                if org_coincidence_obj.url == 'nourl':
                    str_url = ' '
                if org_coincidence_obj.hours != 'nohours':
                    str_hours = working_time + org_coincidence_obj.hours
                if org_coincidence_obj.hours == 'nohours':
                    str_hours = ' '

                str_info = '<div class = "last_params"><li>' + tel + org_coincidence_obj.phone + ' ' + str_url + '</li>' + '<li>' + str_hours + '</li></div>'
                str_ex = str_ex + '<ul class="org_param"><class="number_coincidence">' + str(i) + ')' + ' ' + '<font class = "org_name">' + str_name + "</font></div>" \
                    + '<div class = "coincidence_params"><li>' \
                    + org_coincidence_obj.address + '</li>' + str_info + '</div></ul>' \
                    + '<div id = "but' + str(i) + '"><a href = "#edit_all" class = "edit_button" onclick = "fun_edit_click(' + str(org_coincidence_obj.id) + ',' + str(i) + ')">' + edit + '</a></div></ul>'
                i = i + 1

            # добавим еще один GeoObjectCollection
            newScript = data.createElement("GeoObjectCollection")
            temp_elem_GeoObjectCollection = data.getElementsByTagName('GeoObjectCollection')[0].getElementsByTagName('gml:featureMembers')[0].appendChild(newScript)

            # добавим Style
            newScript = data.createElement("style")  # стиль для картинок
            newScriptText = data.createTextNode('#1')
            newScript.appendChild(newScriptText)
            temp_elem_GeoObjectCollection.appendChild(newScript)

            newScript = data.createElement("gml:featureMembers")
            newScriptText = data.createTextNode('temporary value1 not needed then')
            newScript.appendChild(newScriptText)
            temp_elem_featureMembers = temp_elem_GeoObjectCollection.appendChild(newScript)

            # добавим GeoObject
            newScript = data.createElement("GeoObject")
            newScriptText = data.createTextNode('temporary value2 not needed then')
            newScript.appendChild(newScriptText)
            temp_elem_GeoObject = temp_elem_featureMembers.appendChild(newScript)

            newScript = data.createElement("gml:hintContent")
            newScriptText = data.createTextNode(some_orgs)
            newScript.appendChild(newScriptText)
            temp_elem_GeoObject.appendChild(newScript)
            #
            newScript = data.createElement("gml:balloonContentBody")
            newScriptText = data.createTextNode(str_ex)
            newScript.appendChild(newScriptText)
            temp_elem_GeoObject.appendChild(newScript)
            #
            newScript = data.createElement("gml:balloonContentHeader")
            newScriptText = data.createTextNode('')
            newScript.appendChild(newScriptText)
            temp_elem_GeoObject.appendChild(newScript)
            #
            newScript = data.createElement("gml:balloonContentFooter")
            newScriptText = data.createTextNode('')
            newScript.appendChild(newScriptText)
            temp_elem_GeoObject.appendChild(newScript)

            # добавим gml:Point
            newScript = data.createElement("gml:Point")
            newScriptText = data.createTextNode('temporary value4 not needed then')
            newScript.appendChild(newScriptText)
            temp_elem_Point = temp_elem_GeoObject.appendChild(newScript)

            # добавим gml:pos
            newScript = data.createElement("gml:pos")
            newScriptText = data.createTextNode(str(org_coincidence_obj.x) + ' ' + str(org_coincidence_obj.y))
            newScript.appendChild(newScriptText)
            temp_elem_Point.appendChild(newScript)
        # если точка по заданным координатам одна
        if (org_obj.equal_coord_range == None):
            newScript = data.createElement("GeoObjectCollection")
            temp_elem_GeoObjectCollection = data.getElementsByTagName('GeoObjectCollection')[0].getElementsByTagName('gml:featureMembers')[0].appendChild(newScript)

            # добавим Style
            newScript = data.createElement("style")  # стиль для картинок
            newScriptText = data.createTextNode('#1')
            newScript.appendChild(newScriptText)
            temp_elem_GeoObjectCollection.appendChild(newScript)


            newScript = data.createElement("gml:featureMembers")
            newScriptText = data.createTextNode('temporary value1 not needed then')
            newScript.appendChild(newScriptText)
            temp_elem_featureMembers = temp_elem_GeoObjectCollection.appendChild(newScript)

            # добавим GeoObject
            newScript = data.createElement("GeoObject")
            newScriptText = data.createTextNode('temporary value2 not needed then')
            newScript.appendChild(newScriptText)
            temp_elem_GeoObject = temp_elem_featureMembers.appendChild(newScript)

            newScript = data.createElement("gml:hintContent")
            newScriptText = data.createTextNode(org_obj.org_name)
            newScript.appendChild(newScriptText)
            temp_elem_GeoObject.appendChild(newScript)
            #
            newScript = data.createElement("gml:balloonContentBody")
            if org_obj.url != 'nourl':
                # org_obj.url
                str_url = '<a href ="' + org_obj.url + '">' + org_obj.url + '</a>'
            if org_obj.url == 'nourl':
                str_url = ' '
            if org_obj.hours != 'nohours':
                str_hours = '<li>' + working_time + org_obj.hours + '</li>'
            if org_obj.hours == 'nohours':
                str_hours = ' '
            str_info = '<div class = "last_params"><li>' + tel + org_obj.phone + ' ' + str_url + '</li>' + str_hours + '</div>'
            str_ex = '<ul class = "org_param"><a href = "#"; return false();><font class = "org_name">' + org_obj.org_name + '</font></a>'\
                + '<li>' + org_obj.address + '</li>' + str_info \
                + '<div id = "but"><a href="#edit_all" class="edit_button" onclick = "fun_edit_click(' + str(org_obj.id) + ')">' + edit + '</a></div></ul>'
            newScriptText = data.createTextNode(str_ex)
            newScript.appendChild(newScriptText)
            temp_elem_GeoObject.appendChild(newScript)
            #
            newScript = data.createElement("gml:balloonContentHeader")
            newScriptText = data.createTextNode('')
            newScript.appendChild(newScriptText)
            temp_elem_GeoObject.appendChild(newScript)
            #
            # в футер информацию не помещали
            newScript = data.createElement("gml:balloonContentFooter")
            newScriptText = data.createTextNode('')
            newScript.appendChild(newScriptText)
            temp_elem_GeoObject.appendChild(newScript)

            # добавим gml:Point
            newScript = data.createElement("gml:Point")
            newScriptText = data.createTextNode('temporary value4 not needed then')
            newScript.appendChild(newScriptText)
            temp_elem_Point = temp_elem_GeoObject.appendChild(newScript)

            # добавим gml:pos
            newScript = data.createElement("gml:pos")
            newScriptText = data.createTextNode(str(org_obj.x) + ' ' + str(org_obj.y))
            newScript.appendChild(newScriptText)
            temp_elem_Point.appendChild(newScript)

    f = open("scripts/php_script/myLayer.xml", 'wt')
    f.write(data.toxml('utf-8'))
    f.close()

    print 'xml made %s' % org_type




#=========================================================================================================
# функция для запуска 2 скриптов
def start_scripts(request):
    print 'run2scrpts'
    try:
        # получаем заявку
        if not request.POST.has_key('zayavka_id'):
            raise Http404

        zayavka_id = request.POST.get('zayavka_id')

        # находим заявку в базе
        zayavka_obj = MobiOrganizationsUserChanges.objects.get(id=zayavka_id)
        # находим организацию для изменения
        org_obj = MobiOrganizationsUnique.objects.get(id=zayavka_obj.org_id.id)
        org_type = org_obj.org_type

        # копируем эталон xml потом расскаментировать
        shutil.copy('scripts/php_script/model.xml', 'scripts/php_script/myLayer.xml')
        # делаем xml
        orgs_to_xml(org_type)  #!!! раскоментировать!!!

        # меняем дерикторию для сохранения фаийликов
        f = open("scripts/php_script/index.php", "r+")
        text = f.read()
        f.close()

        str_beg = text.find('directory')
        str_p1 = text[0:str_beg - 1]  # до имзеняемой строки

        str_p1_to_end = text[str_beg - 1:len(text)]  # со строкой и до конца

        # находим конец искомой строки
        end_str_p2 = str_p1_to_end.find(',')
        str_p3 = text[end_str_p2 + 1 + len(str_p1):len(text)]  # после изменяемой строки

        # изменяемая строка
        str_p2 = text[str_beg - 1:end_str_p2 + 1 + len(str_p1) ]  # изменяемая строка
        str_p2_minus3 = str_p2[0:len(str_p2) - 3]

        # находим последний обратный слеш
        lastsl = str_p2_minus3.rfind('/')
        str_before_type = str_p2_minus3[0:lastsl + 1]

        # искомая строка
        str_p2 = str_before_type + str(org_type) + "/',"
        text_to_write = str_p1 + str_p2 + str_p3

        f = open("scripts/php_script/index.php", "w")
        text = f.write(text_to_write)
        f.close()

        print 'start_php for %s ' % str(org_obj.org_type)
        # запускаем php скрипт
        subprocess.call(['/usr/bin/php', 'scripts/php_script/index.php'])  #заменить перед коммитом!!!!!!!!!!!!!!!!!!!!
        #subprocess.call(['c:/php/php.exe', 'scripts/php_script/index.php'])  #!!! раскоментировать !!!
        print 'end_php for %s ' % str(org_obj.org_type)
    except Exception, e:
        print 'ERROR IN RUNNING SCRIPT ORGS'
        print e
        print 'END ERROR IN RUNNING SCRIPT ORGS'

    return HttpResponse('str')


class Admin_HotSpot_Bad_Video_Link(admin.ModelAdmin):
    list_display = ('id', 'contact_face', 'mail', 'text', 'broken_video_id')


class Video_Admin(admin.ModelAdmin):
    list_display = ('id', 'title', 'orig_title')
    search_fields = ('id', 'title', 'orig_title')


class Comments_Of_Video_Admin(admin.ModelAdmin):
    list_display = ('id', 'name_film', 'commentator_name', 'comment_content', 'add_to_site')
    def name_film(self, obj):
        objec = Video.objects.get(comments_m2m=obj.id)
        if objec.title:
            return Video.objects.get(comments_m2m=obj.id).title
        else:
           return Video.objects.get(comments_m2m=obj.id).orig_title
    name_film.short_description = u"Комментарий к фильму"
    name_film.allow_tags = True


class VideoGenre_Admin(admin.ModelAdmin):
    list_display = ('id', 'genre', 'translit_genre')


class Video_Rate_Admin(admin.ModelAdmin):
    list_display = ('id', 'name_films', 'rating_votes', 'rating_score')
    def name_films(self, obj):
        objec = Video.objects.get(id=obj.id)
        if objec.title:
            title = objec.title
        else:
           title = objec.orig_title
        return title
    name_films.short_description = u"Название фильма"
    name_films.allow_tags = True


TaskMonitor.actions.append('patch')
def decorated_new_function(fn):
    @action(u'Запустить задание заново')
#    def new_method(*args, **kwargs):
    def new_method(self, request, queryset):
        # fn(*args, **kwargs)
        # Получаем имя выбранного задания
        for q in queryset:
            task_name = q.name
            lst = task_name.split('.')
            module = lst[0] + '.' + lst[1]
            funct = lst[2]
            # print "q.args='%s'" % q.args
            args = q.args.replace('(', '').replace(')', '')
            kwargs = q.kwargs.replace('{', '').replace('}', '').replace(':', '=').replace("'", '')
            exec 'from %s import %s' % (module, funct) in globals(), locals()
            if kwargs:
                # print "%s.delay(%s, %s)" % (funct, args, kwargs)
                exec "%s.delay(%s, %s)" % (funct, args, kwargs) in globals(), locals()
            else:
                # print "%s.delay(%s)" % (funct, args)
                exec "%s.delay(%s)" % (funct, args) in globals(), locals()
    return new_method
TaskMonitor.patch = decorated_new_function(TaskMonitor.kill_tasks)


class ActiveSession_Admin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False
    fields = ActiveSession._meta.get_all_field_names()
    list_display = ('id', 'account', 'subaccount', 'sessionid', 'date_start', 'date_end', 'framed_ip_address', 'bytes_in', 'bytes_out', 'session_time', 'interrim_update', 'caller_id', 'nas_id', 'nas_int', 'framed_protocol', 'session_status', 'speed_string', 'acct_terminate_cause') 
    readonly_fields = [x  for x in fields if not x == 'date_end']
    search_fields = ('account__username', 'subaccount__username', 'sessionid', 'framed_ip_address', 'nas_int__name')
    
#=========================================================================================================
admin.site.register(Prefecturs, PrefectursAdmin)
admin.site.register(HomeAdministration, HomeAdministrationAdmin)
admin.site.register(DistrictAdministration, DistrictAdministrationAdmin)
admin.site.register(HotSpotQueryStatistic, HotSpotQueryStatisticAdmin)
admin.site.register(HotSpotComplaint, HotSpotComplaintAdmin)
admin.site.register(HotSpotReview, HotSpotReviewAdmin)
admin.site.register(Games, Games_Admin)
admin.site.register(MobiOrganizationsUserChanges, MobiOrganizationsUserChangesAdmin)
admin.site.register(HotSpot_Bad_Video_Link, Admin_HotSpot_Bad_Video_Link)
admin.site.register(Comments_Of_Video, Comments_Of_Video_Admin)
admin.site.register(Video, Video_Admin)
admin.site.register(VideoGenre, VideoGenre_Admin)
admin.site.register(Video_Rate, Video_Rate_Admin)
admin.site.register(ActiveSession, ActiveSession_Admin)

















