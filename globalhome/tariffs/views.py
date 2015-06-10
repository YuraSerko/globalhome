# coding: utf-8
from lib.decorators import render_to, login_required
from django.utils.translation import ugettext_lazy as _
from models import TelZoneGroup
#from csv_parse_tariffs import MOBILE_STR, tel_zone_is_mobile, make_mobile_zone_name, make_stat_zone_name
from django.contrib.admin.views.decorators import staff_member_required
from forms import ChangeTelzoneGroupForm
from django.http import HttpResponseRedirect, Http404
from content.models import Article
#from findocs import check_for_sign_applications

@login_required
#@check_for_sign_applications([])
@render_to("show_my_tariffs.html")
def show_my_tariffs(request):
    """
        Показывает список действующих тарифов в личном кабинете пользователя
    """
    context = {}
    # вот тут мы берем содержимое статьи со слагом "user_tariffs" и отображаем его
    article = Article.objects.get(slug = "user_tariffs")
    # подставляем переменные
    #article = ProcessVariables(article, request)
    article.processVars(("text",), request = request)
    context["article"] = article.text
    context["current_view_name"] = "account_show_tariffs"
    return context

@staff_member_required
#@check_for_sign_applications([])
@render_to("change_telzone_group.html")
def change_telzone_group(request):
    """
        Это view-функция для массовой смены телефонной группы зоны у телефонных зон
    """
    context = {}
    context["request"] = request
    context["user"] = request.user
    context["csrf_token"] = request.COOKIES.get("csrftoken")

    from models import TelZone
    context["app_label"] = TelZone._meta.app_label
    context["app_section"] = TelZone._meta.verbose_name_plural
    context["change_telzone_group_title"] = _(u"Change telzone group for selected telzones").__unicode__()
    context["title"] = context["change_telzone_group_title"]

    if request.GET:
        ids_s = request.GET.get("ids")
        if ids_s:
            ids = ids_s.split(",")
            zones = []
            for id in ids:
                zones.append(TelZone.objects.get(id = int(id)))

            context["zones"] = zones
            if request.POST:
                form = ChangeTelzoneGroupForm(request.POST)
                context["form"] = form
                if form.is_valid():
                    ch = request.POST.get("Change")
                    if ch:
                        grp_id = form.cleaned_data.get("telzone_group")
                        if grp_id:
                            t_grp = TelZoneGroup.objects.get(id = int(grp_id))
                            for zone in zones:
                                zone.group = t_grp
                                zone.save()
                            return HttpResponseRedirect("/admin/tariffs/telzone/")
                    else:
                        return HttpResponseRedirect("/admin/tariffs/telzone/")
            else:
                form = ChangeTelzoneGroupForm()
                context["form"] = form
    else:
        raise Http404

    return context
