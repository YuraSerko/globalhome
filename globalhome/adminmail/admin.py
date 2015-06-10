# -*- coding=utf-8 -*-
# $Id$

from django.contrib import admin
from models import Letter, Attachment
from models import get_language_list_status
from django.utils.translation import ugettext_lazy as _

from mails import registry



class AttachmentInline(admin.TabularInline):
    model = Attachment

class LetterAdmin(admin.ModelAdmin):
    # inlines = [
    #    AttachmentInline,
    # ]


#    def changelist_view(self, request, extra_context={}):
#        extra_context['title'] = _(u"Letters")
#        extra_context['cl'] = []
#        for r in registry.items():
#            extra_context['cl'].append((r, get_language_list_status(r.code)))
#        return super(LetterAdmin, self).changelist_view(request, extra_context)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'language_code':
            kwargs['initial'] = kwargs['request'].GET.get('language')
        if db_field.name == 'code':
            kwargs['initial'] = kwargs['request'].GET.get('code')
        return super(LetterAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def add_view(self, request, form_url='', extra_context={}):
        extra_context['mail_class'] = registry.get_by_code(request.GET.get('code'))
        extra_context['title'] = _(u"Create language version")
        return super(LetterAdmin, self).add_view(request, form_url, extra_context)

admin.site.register(Letter, LetterAdmin)

