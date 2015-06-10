# coding: utf-8
from urlparse import urlparse
from django import forms
#from django.forms import Field, ChoiceField, CharField, URLField, ValidationError, MultiValueField, MultiWidget, Select, TextInput
from django.core.urlresolvers import resolve, Resolver404

from lib.forms.widgets import ClearableFileInput, SorlThumbnailImageInput
from lib.utils.translation import filename

class ExtendedURLField(forms.URLField):
    """
    Поле для отображения абсолютных
    и относительных url.
    Для относительных url производится валидация
    на предмет существования этого url на сайте.
    """

    def clean(self, value):
        if isinstance(value, basestring):
            value = value.strip()
            if value.startswith('/'): # relative url
                try:
                    resolve(urlparse(value)[2])
                except Resolver404:
                    raise forms.ValidationError(_(u'Relative url is not valid on this site.'))
                else:
                    return value
        return super(ExtendedURLField, self).clean(value)

class ContentTypeObjectWidget(forms.MultiWidget):

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        widgets = [forms.Select(choices=choices), forms.TextInput()]
        super(ContentTypeObjectWidget, self).__init__(widgets, *args, **kwargs)

    def decompress(self, value):
        if value is None:
            value = [None for i in self.widgets]
        return value

class ContentTypeObjectField(forms.MultiValueField):
    widget = ContentTypeObjectWidget

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        fields = [forms.ChoiceField(choices=choices), forms.CharField()]
        self.widget = ContentTypeObjectWidget(choices=choices)
        super(ContentTypeObjectField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        return data_list

class FileField(forms.FileField):

    def clean(self, data, initial=None):
        if data:
            try:
                data.name = filename(data.name)
            except AttributeError:
                pass
        f = super(FileField, self).clean(data, initial)
        return f

class ImageField(FileField):
    widget = SorlThumbnailImageInput

class FakeEmptyFieldFile(object):
    """
    A fake FieldFile that will convice a FileField model field to
    actually replace an existing file name with an empty string.

    FileField.save_form_data only overwrites its instance data if the
    incoming form data evaluates to True in a boolean context (because
    an empty file input is assumed to mean "no change"). We want to be
    able to clear it without requiring the use of a model FileField
    subclass (keeping things at the form level only). In order to do
    this we need our form field to return a value that evaluates to
    True in a boolean context, but to the empty string when coerced to
    unicode. This object fulfills that requirement.

    It also needs the _committed attribute to satisfy the test in
    FileField.pre_save.

    This is, of course, hacky and fragile, and depends on internal
    knowledge of the FileField and FieldFile classes. But it will
    serve until Django FileFields acquire a native ability to be
    cleared (ticket 7048).

    """
    def __unicode__(self):
        return u''
    _committed = True

class ClearableFileField(forms.MultiValueField):
    default_file_field_class = FileField
    widget = ClearableFileInput

    def __init__(self, file_field=None, template=None, *args, **kwargs):
        file_field = file_field or self.default_file_field_class(*args,
                                                                  **kwargs)
        kwargs.pop('max_length', None)
        fields = (file_field, forms.BooleanField(required=False))
        kwargs['required'] = file_field.required
        kwargs['widget'] = self.widget(file_widget=file_field.widget,
                                       template=template)
        super(ClearableFileField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list[1] and not data_list[0]:
            return FakeEmptyFieldFile()
        return data_list[0]

class ClearableImageField(ClearableFileField):
    default_file_field_class = ImageField

