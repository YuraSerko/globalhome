# coding: utf-8
from shortcuts import clean
from django.conf import settings
from lib.db.models.fields import HtmlField

def clean_html_fields(sender, **kwargs):
    instance = kwargs.get('instance')
    for field in instance._meta.fields:
        if isinstance(field, HtmlField):
            text = clean(getattr(instance, field.name))
            setattr(instance, field.name, text)

