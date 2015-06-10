# coding: utf-8
#from django.forms import Widget, Select
#from django.forms.widgets import DateInput, FileInput
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.db.models.fields.files import ImageFieldFile

from sorl.thumbnail.main import DjangoThumbnail
from sorl.thumbnail.base import ThumbnailException

class ContentTypeObjectWidget(forms.Widget):
    pass

class JqCalendar(forms.DateInput):

    date_format = 'dd.mm.yy'
    format = '%d.%m.%Y'     # '25.10.2005'

    def __init__(self, attrs=None, format=None, date_format=None):
        super(JqCalendar, self).__init__(attrs=attrs, format=format)
        if date_format:
            self.date_format = date_format

    class Media:
        theme = 'base'
        js = (settings.MEDIA_URL + 'js/jquery/js/ui/ui.datepicker.js',)
        css = { 'all': (settings.MEDIA_URL + 'js/jquery/themes/%s/ui.theme.css' % theme,
                        settings.MEDIA_URL + 'js/jquery/themes/%s/ui.core.css' % theme,
                        settings.MEDIA_URL + 'js/jquery/themes/%s/ui.datepicker.css' % theme,
                        ) }

    def render_js(self, field_id):
        return u'''
            $(document).ready(function(){
                $('#id_%(field)s').datepicker({dateFormat:'%(date_format)s', yearRange:'-60:+10', firstDay: 1, showButtonPanel: true, changeMonth: true, changeYear: true});
              });
        '''%{'field':field_id, 'date_format':self.date_format}

    def render(self, name, value=None, attrs=None):
        return mark_safe( u'''
            <input type="text" name="%(name)s" id="id_%(name)s"  value="%(value)s"/>
            <script type="text/javascript">%(js)s</script>
            ''' % {
                    'name': name,
                    'value': self._format_value(value) or '',
                    'js' : self.render_js(name),
            }
        )

class SorlThumbnailImageInput(forms.FileInput):

    def __init__(self, *args, **kwargs):
        self.size = kwargs.pop('size', (100, 100))
        super(SorlThumbnailImageInput, self).__init__(*args, **kwargs)

    def render(self, name, value=None, attrs=None):
        output = super(SorlThumbnailImageInput, self).render(name, value, attrs)
        if isinstance(value, ImageFieldFile):
            try:
                tmbn = DjangoThumbnail(value.name, self.size)
                img_tag = '<img src="%s" style="float: left; margin: 0 10px 10px 0">' % tmbn.absolute_url
            except ThumbnailException:
                img_tag = ''
            output = mark_safe(u'%s%s' % (img_tag, output))
        return output

class ClearableFileInput(forms.MultiWidget):
    default_file_widget_class = forms.FileInput
    template = '%(input)s<br />%(label)s: %(checkbox)s'

    def __init__(self, file_widget=None,
                 attrs=None, template=None):
        if template is not None:
            self.template = template
        self.value = None
        file_widget = file_widget or self.default_file_widget_class()
        super(ClearableFileInput, self).__init__(
            widgets=[file_widget, forms.CheckboxInput()],
            attrs=attrs)

    def decompress(self, value):
        # the clear checkbox is never initially checked
        self.value = value
        return [value, None]

    def format_output(self, rendered_widgets):
        if self.value:
            return self.template % {'input': rendered_widgets[0],
                                    'checkbox': rendered_widgets[1],
                                    'label': _(u'Delete'),
                                    }
        return rendered_widgets[0]

class ClearableImageInput(ClearableFileInput):
    default_file_widget_class = SorlThumbnailImageInput