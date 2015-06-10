# coding: utf-8

from django.contrib import admin
from page.models import Send_mail, LeftBlockMenuPage
from page.models import Message
from page.forms import message_form, PageForm
from django.forms import ModelForm
from page.models import Sender
from page.models import UserFiles, Menu_on_globalhome, Menu_on_moscowdata, Meta_globalhome, Meta_moscowdata
from django.contrib.admin.actions import delete_selected
from django import forms
import os
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from lib.mail import send_email
from django.conf import settings
from django.contrib import messages
import traceback


class PageAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'parent']
    form = PageForm
admin.site.register(LeftBlockMenuPage, PageAdmin)



class ReadonlyFileInput(forms.Widget):
    def __init__(self, obj, attrs=None):
        self.object = obj
        super(ReadonlyFileInput, self).__init__(attrs)
    def render(self, name, value, attrs=None):
        if value and hasattr(value, "url"):
            return mark_safe(u'<p><a href="%s">%s</a></p>'\
            % (escape(value.url), \
            escape(force_unicode(os.path.basename(value.path)))))
        else:
            return ''

class ModelWithFileFieldForm(forms.ModelForm):
    class Meta:
        model = UserFiles
    def __init__(self, *args, **kwargs):
        super(ModelWithFileFieldForm, self).__init__(*args, **kwargs)
        self.fields['file'].widget = ReadonlyFileInput(self.instance)

class Mail(admin.ModelAdmin):
    list_display = ('email', 'subject', 'message', 'file_link', 'status_mail')
    readonly_fields = ['email', 'subject', 'message', 'user_id', 'date', 'sender_id', 'status_mail', 'file_link']
    exclude = ['spis_file']
    actions = ('send_letter',)
    def send_letter(self, request, ob):
        count_success = 0
        for x in ob:
            try:
                print "=================="
                print count_success
                send_email(x.subject, x.message, settings.DEFAULT_FROM_EMAIL, [x.email])
                count_success += 1
                sending_is_successful = True
            except:
                print traceback.print_exc()
                sending_is_successful = False
        print count_success
        if count_success != 0 and sending_is_successful:
            if count_success > 1:
                if count_success < 5:
                    message = str(count_success)+' сообщения успешно отправлены'+'!'
                else:
                    message = str(count_success)+' сообщений успешно отправлены'+'!'
            else:
                message = 'Сообщение успешно отправлено!'
            messages.add_message(request, messages.INFO, message)
        else:
            message1 = 'Отправлено ' + str(count_success) +' сообщений'
            message = 'Не отправлено ' +str(ob.count() - count_success ) + ' cообщение'
            if ob.count() > 1:
                message1 = 'Отправлено ' + str(count_success) +' сообщений'
                message = 'Не отправлено ' +str(ob.count() - count_success ) + ' cообщения'
            messages.add_message(request, messages.INFO, message1)
            messages.add_message(request, messages.ERROR, message)
    send_letter.short_description = u'Отправитка писем'

    search_fields = ('email', 'user_id')

    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Send_mail, Mail)




class FileInline(admin.TabularInline):
    form = ModelWithFileFieldForm
    model = UserFiles
    extra = 0
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def get_readonly_fields(self, request, obj=None):
        return []

class SendMail(admin.ModelAdmin):
    list_display = ['user_type', 'subject', 'message', 'start_date', 'stop_date', 'files', 'common_message', 'success_message', 'failed_message']
    readonly_fields = ['user_type', 'subject', 'message', 'start_date', 'stop_date', 'user_id', 'common_message', 'success_message', 'failed_message']
    actions = None
    inlines = [
        FileInline,
    ]
    def files(self, obj):
        files = UserFiles.objects.filter(sender_id=obj.id)
        s = []
        for file in files:
            s.append('<a href="/media/' + str(file.file) + '">' + (str(file.file)[str(file.file).rfind('/') + 1:]) + '</a>')
        values = ', '.join(s)
        return values
    files.allow_tags = True
    files.short_description = _(u"spis_file")
    def has_delete_permission(self, request, obj=None):
        return False

class MenuOnUrlAdmin(admin.ModelAdmin):
    list_display = ('url', 'url_name', 'tree_of_parent', 'name_element',)
    search_fields = ('url', 'name_element',)

    def tree_of_parent(self, obj):
        name = '%s' % obj.name_element
        while obj.parent != None:
            name = '%s->%s' % (obj.parent.name_element, name)
            obj = obj.parent
        return name
#    class Media:
#        js = ['https://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js', '/media/js/chosen.jquery.js', '/media/js/my.js']

class MetaAdmin(admin.ModelAdmin):
    list_display = ('url', 'description', 'keywords', 'title',)
    search_fields = ('url', 'description', 'keywords', 'title',)


admin.site.register(Meta_globalhome, MetaAdmin)
admin.site.register(Meta_moscowdata, MetaAdmin)
admin.site.register(Menu_on_globalhome, MenuOnUrlAdmin)
admin.site.register(Menu_on_moscowdata, MenuOnUrlAdmin)
admin.site.register(Sender, SendMail)



