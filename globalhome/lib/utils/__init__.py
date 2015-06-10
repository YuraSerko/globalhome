# coding: utf-8
from django.utils.translation import ugettext_lazy as _
import datetime

def get_now():
    "Возвращает текущее время без микросекунд"
    now = datetime.datetime.now()
    return datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)

def get_ready_context(request, title, app_section = _(u"Assigned services")):
    context = {}
    context["request"] = request
    context["user"] = request.user
    context["title"] = title
    context["is_popup"] = True if (request.GET and request.GET.get("_popup")) else False
    context["csrf_token"] = request.COOKIES.get("csrftoken")
    context["app_label"] = "services"
    context["app_section"] = app_section
    context["language"] = "ru"
    context["none_value"] = "---" 
    return context

