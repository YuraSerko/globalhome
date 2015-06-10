#!/usr/bin/python
# coding: utf-8
from lib.decorators import render_to
from django.contrib.admin.views.decorators import staff_member_required
from account.forms import UserRegistrationForm
from account.forms import UserLoginForm2, PasswordResetRequestForm
from django.http import HttpResponseRedirect
from account.models import ActionRecord, get_base_url
from django.core.urlresolvers import reverse
from billing.models import *
from django.contrib.auth import login as _login, logout as _logout, authenticate
from lib.helpers import redirect
from django.utils.translation import ugettext_lazy as _  # @UnusedImport
from django.utils.translation import ugettext as _
import log
from django.http import Http404
from django.contrib.auth.models import User
from account.models import Profile
from page.models import Send_mail, LeftBlockMenuPage
from django.core.mail import send_mail
import datetime
from django.conf import settings
# from django.core.mail import EmailMessage#, SMTPConnection
from content.models import  News
# from django.core.mail import send_mail as _send_mail


def get_left_block():
    data = list(LeftBlockMenuPage.objects.all().order_by('position'))

    def sort_tree(parent):
        result = []
        objects = filter(lambda x: x.parent_id == parent, data)
        for ob in objects:
            children = sort_tree(ob.id)
            result.append({'multiple': True if children else False, 'url':ob.url, 'name':ob.name, 'childs':children})
        return result


    return sort_tree(None)
     


def panel_base_auth(request, context):
    class TopErrors(object):
        def __init__(self):
            self._errors = []
        def add(self, error):
            self._errors.append(u'<li>%s</li>' % error)
        def render(self):
            if self._errors:
                return u'<ul class="errorlist">%s</ul>' % '\n'.join(self._errors)
            return u''

    if not context.has_key('objects'):
        context['news_win'] = True
        from content.views import content_list_base
        news = content_list_base(request, News, 4)
        context.update(news)
    else:
        context['news_win'] = False
    top_errors = TopErrors()
    form_login = UserLoginForm2()
    form_reg = UserRegistrationForm()
    form_reset = PasswordResetRequestForm()
    if request.user.is_anonymous():
        if 'login_m' in request.POST or 'registr' in request.POST or 'reset_password' in request.POST:
            if request.POST:
                if 'login_m' in request.POST:
                    form_login = UserLoginForm2(request.POST)
                    if form_login.is_valid():
                        user = form_login.user
                        if user:
                            if user.is_active:
                                _login(request, user)
                                return HttpResponseRedirect(redirect(request, next_only=get_base_url(user)))
                            else:
                                try:
                                    action = ActionRecord.objects.get(user=user, type='A')
                                except:
                                    action = None
                                if not action or action.expired:
                                    context.update({'not_active' : True})
                                    context['panel'] = True
                                    top_errors.add(u'''
                                                    Учётная запись не активирована.
                                                    Возможно, Вы не прошли по ссылке в письме,
                                                    присланном Вам после регистрации.
                                                    <br/>
                                                    Если Вы не получали письма, или код активации просрочен, Вы можете
                                                    <a class="bold" href="%s?user=%s">получить код активации заново</a>.
                                    ''' % (reverse('resend_activation_code'), form_login.cleaned_data['username']))
                    else:
                        context.update({'error_login' : True})
                        context['login_er'] = True
                if 'registr' in request.POST:
                    form_reg = UserRegistrationForm(request.POST)
                    if form_reg.is_valid():
                        user = form_reg.save()   
                        action_key, send_mail = ActionRecord.registrations.create_inactive_user_key(# @UnusedVariable
                            new_user=user,
                            #row_password=form_reg.get_row_password(),
                            row_password = user.password,  
                            send_email=True,
                        )
                        context.update({'reg_compite' : True})
                        #context['reg_er'] = True  //не выводим окно если рег успешна
                    else:
                        context['reg_er'] = True
                if 'reset_password' in request.POST:
                    form_reset = PasswordResetRequestForm(request.POST)
                    if form_reset.is_valid():
                        user = form_reset.user
                        if user and user.is_active:
                            ActionRecord.resets.create_password_reset([user])
                            context['reset_password_success'] = u'Письмо с инструкциями по смене пароля было выслано Вам по электронной почте.'
                        else:
                            context['reset_password_error'] = u'Пользователя с указанным именем не существует!'
                    context['reset_er'] = True
        else:
            form_login = UserLoginForm2()
            form_reg = UserRegistrationForm()
            form_reset = PasswordResetRequestForm()
            # log.add("showing user registration page")
        context['form_login'] = form_login
        context['form_reset'] = form_reset
        context['top_errors'] = top_errors.render()
        context['form_reg'] = form_reg
    from reviews.views import write_review
    if (request.path_info != '/' and request.path_info != ''):
        context.update(write_review(request))
    context['user_name'] = request.user.username
    context['left_block'] = get_left_block()
    from hotspot.views import hotspot_identity
    context['site'] = settings.CURRENT_SITE
    context['article_page_on_hotspot'] = True
    context.update(hotspot_identity(request))
    return context



@render_to('homepage.html')
def homepage(request):
    context = {}
    return panel_base_auth(request, context)


@render_to('search.html')
def search(request):
    context = {}
    return panel_base_auth(request, context)


def view_user(request, name_user):
    profile = request.user.get_profile()
    if not profile.user.is_superuser:
        raise Http404
    _logout(request)
    user_obj_temp = User.objects.get(username=name_user)
    user_obj = authenticate(username=user_obj_temp.username, password=user_obj_temp.password)
    _login(request, user_obj)
    return HttpResponseRedirect(reverse('service_choice'))


from page.forms import message_form
from django.shortcuts import render_to_response
from lib.mail import  send_mass_mail_threaded
from page.forms import UploadForm
from page.models import UserFiles
from page.models import Sender
from django.contrib import messages
from django.template import Template, Context
from django.contrib.sites.models import Site



@staff_member_required
def send_msg(request):
    dictionary = {'domain': 'Доменное имя Сайта', 'username': 'Имя пользователя'}
    if request.method == 'POST':
        if request.POST.get("add"):
            form_client = message_form(request.POST)
            form = UploadForm(request.FILES)
            if form_client.is_valid():
                user_emails = []
                userlist = form_client.cleaned_data['users_type']
                if userlist == 'active':
                    activ = User.objects.filter(is_active=True)
                    for u in activ:
                        user_emails.append((u.email, u.username))
                elif userlist == 'juridical':
                    activ = Profile.objects.select_related()
                    for p in activ:
                        if p.user.is_active and p.is_juridical == True:
                            user_emails.append((p.user.email, p.user.username))
                elif userlist == 'individual':
                    activ = Profile.objects.select_related()
                    for p in activ:
                        if p.user.is_active and p.is_juridical == False:
                            user_emails.append((p.user.email, p.user.username))
                elif userlist == 'admins' :
                    activ = User.objects.filter(is_active=True, is_superuser=True, is_staff=True)
                    for u in activ:
                        user_emails.append((u.email, u.username))
                else:
                    user_emails = []
                subject = request.POST.get("subject")
                current_domain = Site.objects.get_current().domain
                message = request.POST.get("message")

                user_id = request.user.id
                mail_obj = Sender(
                    subject=subject,
                    message=message,
                    start_date=datetime.datetime.now(),
                    user_id=user_id,
                    user_type=userlist,
                    )
                mail_obj.save()
                attachments = []
                if 'file' in request.FILES:
                    files = request.FILES.getlist('file', [])
                    for name_file in files:
                        newdoc = UserFiles(file=name_file, sender_id=mail_obj.id)
                        newdoc.save()
                        attachments.append(unicode(newdoc.file))
                mailstuple = []
                html = None
                for email, username in user_emails:
                    context = {'username': username,  # user here
                           'domain': '%s://%s/' % (settings.SITE_PROTOCOL, current_domain)
                           }
                    subj = Template(subject).render(Context(context))
                    msg = Template(message).render(Context(context))
                    mail_obj.subject = subj
                    mail_obj.message = msg
                    mail_obj.save()
                    mailstuple.append((subj, msg, settings.EMAIL_HOST_USER, email, attachments, html))
                send_mass_mail_threaded(mailstuple, user_id, mail_obj.id, fail_silently=False)
                messages.add_message(request, messages.SUCCESS, u'Сообщение отправлено')
                return HttpResponseRedirect('../')

        if request.POST.get("cancel"):
            return HttpResponseRedirect("../")
    else:
        form_client = message_form()
        form = UploadForm()

    return render_to_response('send_msg.html', {'form': form, 'form_client': form_client, 'd':dictionary})

from django.http import HttpResponse
from models import Menu_on_globalhome, Menu_on_moscowdata
def add_name_to_url(request):
    menu_gl_qs = Menu_on_globalhome.objects.all()
    from django.core.urlresolvers import resolve
    for menu_gl_obj in menu_gl_qs:
        try:
            current_url_name = resolve(menu_gl_obj.url).url_name
            menu_gl_obj.url_name = current_url_name
            menu_gl_obj.save()
            print ' - - - - - - - - - - - - - - '
            print menu_gl_obj.url
            print current_url_name
            print ' - - - - - - - - - - - - - - '
        except:
            print '----- bad_url -----'
            continue
        print
    return HttpResponse("Good!")

