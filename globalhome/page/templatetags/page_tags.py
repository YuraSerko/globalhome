# coding: utf-8
import os
from random import randint
from django.conf import settings
from django.template import Library
from django.utils.translation import ugettext as _
register = Library()


@register.inclusion_tag('top_menu.html', takes_context = True)
def top_menu(context): # верхрее меню
    from lib.menu import Menu, get_reverse_conf
    menu = Menu(context.get('current_view_name'))
    menu.add('activationcard', _(u'Activate card'))
    menu.add(get_reverse_conf('article_by_slug', slug = 'service_list'), _(u'Services'))
#    menu.add(get_reverse_conf('news_list'), _(u'News'))
    menu.add(get_reverse_conf('article_by_slug', slug = 'feedback'), _(u'Feedback'))
    menu.add(get_reverse_conf('article_by_slug', slug = 'how_to_use'), _(u'How to use<br>our services'))
    menu.add(get_reverse_conf('article_by_slug', slug = 'tariffs'), _(u'Tariffs'))
    
    menu.add(get_reverse_conf('article_by_slug', slug = "payment_methods"), _(u'Payment<br>methods'))
#    menu.add(get_reverse_conf('article_by_slug', slug='call-us-button'), _(u'Call us<br>online'), isCallUs = True)
#    menu.add(get_reverse_conf('helpdesk_account_tickets'), _(u'Support'))
    user = context['user']

    if user.is_anonymous():
        menu.add('account_login', _(u'Log in'))
    elif user.is_staff:
        menu.add('helpdesk_dashboard', u'<span class="">%s:</span> %s' % (user.username, _(u'Management')))
    else:
        menu.add('account_profile', u'<span class="">%s:</span> %s' % (user.username, _(u'Personal area')))
    return {
            'menu': menu,
            }

@register.simple_tag
def homapage_header_img():
    path = os.path.abspath(os.path.join(settings.MEDIA_ROOT, 'img/layout/people'))
    files = filter(lambda x: x.lower().endswith(('.gif', '.jpg', '.jpeg', '.png')), os.listdir(path))
    if len(files) > 0:
        return '<img id="homepage-header-img" src="%simg/layout/people/%s" alt="">' % (settings.MEDIA_URL, files[randint(0, len(files) - 1)])
    return ''

