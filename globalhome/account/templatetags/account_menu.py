# -*- coding=utf-8 -*-
# $Id: account_menu.py 246 2010-12-06 12:06:07Z site $
from django import template
# from django.utils.translation import ugettext_lazy as _
# from django.core.urlresolvers import reverse
# from django.conf import settings
from account.settings import PERSONAL_AREA_MENU, PERSONAL_AREA_STAFF_MENU, PROFILE_MENU_CARD, \
                             PERSONAL_AREA_MENU_CARD, PROFILE_MENU_JURIDICAL_GLOBALHOME, PROFILE_MENU_JURIDICAL_MOSCOWDATA, \
                             PROFILE_MENU_PHISICAL_GLOBALHOME, PROFILE_MENU_PHISICAL_MOSCOWDATA, PROFILE_MENU_JURIDICAL_GLOBALMOBI, PROFILE_MENU_PHISICAL_GLOBALMOBI
from django.http import Http404
register = template.Library()
from django.conf import settings
from page.models import Menu_on_globalhome, Menu_on_moscowdata, Meta_globalhome, \
    Meta_moscowdata
from content.models import Article
from data_centr.models import Data_centr_payment
from django.db.models import Q
import datetime
from billing.models import BillserviceAccount

@register.inclusion_tag('top_menu.html', takes_context=True)
def account_menu(context):
    """
    Show menu for user's "cabinet"
    """
    from lib.menu import Menu, get_reverse_conf
    menu = Menu(context['current_view_name'])
    profile = context["user"].get_profile()

    if not profile.is_card:
        for view_name, verbose_name in PERSONAL_AREA_MENU:

            if view_name[:4] != "slug":
                if view_name != '#':
                    menu.add(view_name, verbose_name)
                else:
                    menu.add('', verbose_name, isCallUs=True)
            else:
                menu.add(get_reverse_conf('article_by_slug', slug=view_name[5:]), verbose_name)
    else:
        for view_name, verbose_name in PERSONAL_AREA_MENU_CARD:

            if view_name[:4] != "slug":
                if view_name != '#':
                    menu.add(view_name, verbose_name)
                else:
                    menu.add('', verbose_name, isCallUs=True)
            else:
                menu.add(get_reverse_conf('article_by_slug', slug=view_name[5:]), verbose_name)

    wip = context.get("window_is_popup", False)
    return { 'menu': menu, "window_is_popup": wip }

@register.inclusion_tag('account/tags/account_profile_menu_%s.html' % settings.CURRENT_SITE, takes_context=True)
def account_profile_menu(context):
    """
    Show right menu in profile page
    """
    from lib.menu import Menu
    menu = Menu(context.get('current_view_name'))

    # for view_name, verbose_name, attrs in (context['user'].get_profile().is_juridical and PROFILE_MENU_JURIDICAL or PROFILE_MENU_PHISICAL or PROFILE_MENU_CARD):

    profile = context["user"].get_profile()
    clist = []
    if not profile.is_juridical and not profile.is_card:
        context['button_card_get'] = True
    if profile.is_juridical:
        if settings.CURRENT_SITE in (1,):
            clist = PROFILE_MENU_JURIDICAL_GLOBALHOME
        elif settings.CURRENT_SITE in (3,):
            clist = PROFILE_MENU_JURIDICAL_GLOBALMOBI
        else:
            clist = PROFILE_MENU_JURIDICAL_MOSCOWDATA

    else:
        if settings.CURRENT_SITE in (1,):
            clist = PROFILE_MENU_PHISICAL_GLOBALHOME
        elif settings.CURRENT_SITE in (3,):
            clist = PROFILE_MENU_PHISICAL_GLOBALMOBI
        else:
            clist = PROFILE_MENU_PHISICAL_MOSCOWDATA

    if profile.is_card:
        clist = PROFILE_MENU_CARD

    if settings.CURRENT_SITE == 1 or settings.CURRENT_SITE == 2:
        for view_name, verbose_name, attrs in clist:
            menu.add(view_name, verbose_name, attrs)


    for men in menu:
#        print 'men = %s' % men
        context[men['name']] = men
#        if men["name"] == 'account_phones_list':
#            context["account_phones_list"] = men
#        if men["name"] == 'account_phones_groups':
#            context["account_phones_groups"] = men
#        if men["name"] == 'external_phones_list':
#            context["external_phones_list"] = men
#        if men["name"] == 'callforwarding_rules_list':
#            context["callforwarding_rules_list"] = men
#        if men["name"] == 'account_fax':
#            context["account_fax"] = men
#        if men["name"] == 'list_getfax':
#            context["list_getfax"] = men
#        if men["name"] == 'list_ivr':
#            context["list_ivr"] = men
#        if men["name"] == 'my_data_centr':
#            context["my_data_centr"] = men
#        if men["name"] == 'demands_dc_archive':
#            context["demands_dc_archive"] = men
#        if men["name"] == 'account_data_centr':
#            context["account_data_centr"] = men
#        if men["name"] == 'list_vm':
#            context["list_vm"] = men
#        if men["name"] == 'transfer_call_help':
#            context["transfer_call_help"] = men
#        if men["name"] == 'vpn_users':
#            context["vpn_users"] = men
#        if men["name"] == 'list_record_talk_tariff':
#            context["list_record_talk_tariff"] = men
#        if men["name"] == 'my_inet':
#            context["my_inet"] = men
#        if men["name"] == 'account_show_internet':
#            context["account_show_internet"] = men
#        if men["name"] == 'hotspot_statistic':
#            context["hotspot_statistic"] = men
#        if men["name"] == 'list_gateway':
#            context["list_gateway"] = men
    return context



@register.inclusion_tag('account/tags/account_top_menu_%s.html' % settings.CURRENT_SITE, takes_context=True)
def account_top_menu(context):
    """
    Show right menu in profile page
    """
    from lib.menu import Menu
    menu = Menu(context.get('current_view_name'))
    # for view_name, verbose_name, attrs in (context['user'].get_profile().is_juridical and PROFILE_MENU_JURIDICAL or PROFILE_MENU_PHISICAL or PROFILE_MENU_CARD):

    profile = context["user"].get_profile()
    if not profile.is_juridical and not profile.is_card:
        context['button_card_get'] = True
    bill_account_obj = BillserviceAccount.objects.get(id=profile.billing_account_id)

    now = datetime.datetime.now()
    payment_qs = Data_centr_payment.objects.filter(Q(bill_account=profile.billing_account) & Q(postdate=False) & Q(payment_date=None))
    print payment_qs
    context['not_paid'] = True if payment_qs else False

    context["not_is_invoice"] = True

    if not profile.is_juridical or not profile.create_invoice:
        context["not_is_invoice"] = False
    clist = []
#    if profile.is_juridical:
#        clist = PROFILE_MENU_JURIDICAL

#    else:
#        clist = PROFILE_MENU_PHISICAL

    if profile.is_card:
        clist = PROFILE_MENU_CARD

    for view_name, verbose_name, attrs in clist:
        menu.add(view_name, verbose_name, attrs)

    for men in menu:
        # print men
        if men["name"] == 'account_profile':
            context["account_profile"] = men
        if men["name"] == 'helpdesk_account_tickets':
            context["helpdesk_account_tickets"] = men
        if men["name"] == 'account_show_tariffs':
            context["account_show_tariffs"] = men

    return context


@register.inclusion_tag('top_menu.html', takes_context=True)
def staff_menu(context):
    """
    Show menu for user's "cabinet" for staff
    """
    from lib.menu import Menu
    menu = Menu(context['current_view_name'])
    for view_name, verbose_name in PERSONAL_AREA_STAFF_MENU:
        menu.add(view_name, verbose_name)

    return {'menu': menu}


@register.inclusion_tag('account/tags/content_menu.html', takes_context=True)
def content_menu(context):
    def create_menu_on_text(Name_class):
        text_url = ''
        spis_menu_obj = []
        menu_qs = Name_class.objects.filter(url=current_url).order_by('id')
        if not menu_qs:
            menu_qs = Name_class.objects.filter(url_name=current_url_name).order_by('id')
        if menu_qs:
            menu_obj = menu_qs[0]
            spis_menu_obj.append(menu_obj)
            while menu_obj.parent:
                menu_obj = menu_obj.parent
                spis_menu_obj.append(menu_obj)
            if len(spis_menu_obj) > 1:
                spis_menu_obj.reverse()
                for i, menu_obj in enumerate(spis_menu_obj):
                    if text_url:
                        text_url += u'<span> &#8594; </span>'
                    text_url += u"<a href='%s'>%s</a>" % (menu_obj.url, menu_obj.name_element) if len(spis_menu_obj) > i + 1 else '%s' % menu_obj.name_element
        return text_url

    current_url = context['request'].path
    from django.core.urlresolvers import resolve
    try:
        current_url_name = resolve(current_url).url_name
    except:
        current_url_name = ''
#    if current_url_name == 'article_by_slug':
#        slug = resolve(current_url).kwargs['slug']
#        article_qs = Article.objects.filter(slug=slug)
#        if article_qs:

    if settings.SITE_ID in (1,):
        text_url = create_menu_on_text(Menu_on_globalhome)
    elif settings.SITE_ID in (2,):
        text_url = create_menu_on_text(Menu_on_moscowdata)
    elif settings.SITE_ID in (3,):
        text_url = create_menu_on_text(Menu_on_globalhome)
    context['text'] = text_url

    return context


@register.inclusion_tag('account/tags/meta_block.html', takes_context=True)
def meta_block(context):
    def get_meta(Name_class, context):
        request = context['request']
        page_title = ''
        if request.path_info == '/content/news/':
            page_title = u''  if not(request.GET.has_key('page')) else u'Страница %s' % (request.GET['page'])
        current_url = context['request'].path
        meta_qs = Name_class.objects.filter(url=current_url)
        if meta_qs:
            meta_obj = meta_qs[0]
            context['meta_description'] = meta_obj.description
            context['meta_keywords'] = meta_obj.keywords
            context['meta_title'] = meta_obj.title
            context['page_title'] = page_title
        return context
    if settings.SITE_ID in (1,):
        context = get_meta(Meta_globalhome, context)
        context['after_title'] = 'Global Home'
    elif settings.SITE_ID in (2,):
        context = get_meta(Meta_moscowdata, context)
        context['after_title'] = 'Moscow Data'
    return context
