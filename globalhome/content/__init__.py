# coding: utf-8
from django.contrib import admin
# from django.db import models
from django import forms
from lib.utils import get_now
from django.utils.translation import ugettext as _

from django.db.models import ManyToManyField


AV_COLUMNS = (
    # формат: ( показывать по умолчанию?, имя атрибута модели, видимое имя )
    (True, "id", _(u"Id")),  # "Начало звонка"),
    (True, "created_by", _(u"Created by")),
    (True, "created_at", _(u"Created at")),  # "Конец звонка"),
    (True, "modified_at", _(u"Modified at")),  # "Длина сессии<br>в минутах"),
    (True, "name", _(u"Name")),  # "Длина сессии<br>в секундах"),
    (True, "text", _(u"Text")),  # "Вызывающий<br>абонент"),
)

def get_selected_columns():
    s = ""
    for ac in AVAILABLE_COLUMNS:
        if ac[0]:
            s += "1"
        else:
            s += "0"
    return s

class VarSetCheckBoxSelect(forms.CheckboxSelectMultiple):

    def render(self, *args, **kwargs):
        r = super(VarSetCheckBoxSelect, self).render(*args, **kwargs)
        text = _("Show variables in selected variablesets")
        r = ('<a id="show_all_vars_link" href="/content_variables/show_many/">%s</a><br>' % text) + r + '<script type="text/javascript" charset="utf-8" src="/media/js/show_content_vars.js"></script>'
        return r

class BaseContentAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "created_at", "modified_at")
    save_as = True
    date_hierarchy = "created_at"

    formfield_overrides = {
        ManyToManyField: {'widget': VarSetCheckBoxSelect},
    }

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.modified_at = get_now()
        else:
            obj.created_at = obj.modified_at = get_now()
            obj.created_by = request.user

        return super(BaseContentAdmin, self).save_model(request, obj, form, change)

