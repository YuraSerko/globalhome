# -*- coding: utf-8 -*-
from django.forms import widgets
from django.utils.html import format_html, mark_safe
from django.utils.encoding import force_text

class NotClearableFileInput(widgets.FileInput):
    '''
    ClearableFileInput без checkbox`а
    '''
    initial_text = u'На данный момент'
    input_text = u'Изменить'
    template_with_initial = '%(initial_text)s: %(initial)s <br />%(input_text)s: %(input)s'
    url_markup_template = '<a href="{0}">{1}</a>'

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
        }
        template = '%(input)s'
        substitutions['input'] = super(NotClearableFileInput, self).render(name, value, attrs)
        if value and hasattr(value, "url"):
            template = self.template_with_initial
            substitutions['initial'] = format_html(self.url_markup_template,
                                               value.url,
                                               force_text(value))
        return mark_safe(template % substitutions)