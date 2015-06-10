# coding: utf-8
from django.db.models import URLField, FileField as DjangoFileField, ImageField as DjangoImageField
from lib.forms.fields import ExtendedURLField as ExtendedURLFormField, ClearableFileField, ClearableImageField

class ExtendedURLField(URLField):
    """
    Поле может содержать как абсолютный, так и относительный url, 
    начинающийся с "/". 
    В последнем случае это должен быть валидный url сайта.
    """
    def formfield(self, **kwargs):
        kwargs['form_class'] = ExtendedURLFormField
        return super(ExtendedURLField, self).formfield(**kwargs)
    
class FileField(DjangoFileField):
    
    def formfield(self, **kwargs):
        defaults = {'form_class': ClearableFileField}
        defaults.update(kwargs)
        defaults.pop('widget', None)
        return super(FileField, self).formfield(**defaults)
            
class ImageField(DjangoImageField):
    
    def formfield(self, **kwargs):
        defaults = {'form_class': ClearableImageField}
        defaults.update(kwargs)
#        defaults.pop('widget', None)
        return super(ImageField, self).formfield(**defaults) 