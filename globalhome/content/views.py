# coding: utf-8
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from forms import *
from lib.decorators import render_to
from lib.paginator import SimplePaginator
from content.models import Article, News, ButtonPanelUrls, ButtonPanelHref
from models import *
import datetime
import settings
from django.db import connections, transaction
from lib.decorators import render_to, login_required
from django.utils.translation import ugettext_lazy as _
from django.core.mail import EmailMultiAlternatives
from account.models import Profile
from lib.decorators import render_to
from account.forms import UserRegistrationForm
from account.forms import UserLoginForm2, PasswordResetRequestForm
from account.models import *
from billing.models import *
from externalnumbers.consts import *
from django.contrib.auth import authenticate, login as _login, logout as _logout
from lib.helpers import redirect, next
from django.utils.encoding import iri_to_uri, force_unicode
import calendar
from page.views import panel_base_auth
from internet.models import Connection_address
from internet.models import Internet_city
from django.db.models import Q

@render_to("hostel.html")
def hostelinform(request):
    context = {}


    registration_form = UserRegistrationForm()
    class TopErrors(object):
        def __init__(self):
            self._errors = []
        def add(self, error):
            self._errors.append(u'<li>%s</li>' % error)
        def render(self):
            if self._errors:
                return u'<ul class="errorlist">%s</ul>' % '\n'.join(self._errors)
            return u''
    context['bout'] = False
    context['panel'] = False
    context['panel2'] = False
    top_errors = TopErrors()
    form_login = UserLoginForm2()
    form_reg = UserRegistrationForm()
    form_reset = PasswordResetRequestForm()
    context['user_name'] = request.user.username
    try:
        article = Article.frontend_objects.get(slug='about_registration')
    except Article.DoesNotExist:
        article = None
    if request.user.is_anonymous():
        context['bout'] = True
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
                        context['panel'] = True
                if 'registr' in request.POST:
                    form_reg = UserRegistrationForm(request.POST)
                    # log.add("showing user registration page: POST")
                    if form_reg.is_valid():
                        user = form_reg.save()
                        action_key, send_mail = ActionRecord.registrations.create_inactive_user_key(
                            new_user=user,
                            row_password=form_reg.get_row_password(),
                            send_email=True,
                        )
                        context.update({'reg_compite' : True})
                        context['panel'] = True
                    else:
                        context['panel'] = True

                if 'reset_password' in request.POST:
                    form_reset = PasswordResetRequestForm(request.POST)
                    if form_reset.is_valid():
                        user = form_reset.user
                        if user:
                            ActionRecord.resets.create_password_reset([user])
                            context['reset_password_success'] = u'Письмо с инструкциями по смене пароля было выслано Вам по электронной почте.'

                        else:
                            context['reset_password_error'] = u'Пользователя с указанным именем не существует!'
                        context['panel2'] = True
                    else:
                        context['panel2'] = True

        else:
            form_login = UserLoginForm2()
            form_reg = UserRegistrationForm()
            form_reset = PasswordResetRequestForm()
            # log.add("showing user registration page")
        context['form_login'] = form_login
        context['form_reset'] = form_reset
        context['top_errors'] = top_errors.render()
        context['form_reg'] = form_reg





    cur2 = connections[settings.GLOBALHOME_DB2].cursor()
    cur2.execute("SELECT content_hostelinform.id, floor, block, number, short_number, password, ip, status, room, hostel_number, university_name_id, content_universityinform.name FROM content_hostelinform JOIN content_universityinform on(content_hostelinform.university_name_id = content_universityinform.id) WHERE settings = %s ORDER BY floor, block, room;", (True,))
    host = cur2.fetchall()
    transaction.commit_unless_managed(settings.GLOBALHOME_DB2)
    form = SearchHostelForm()
    context["host"] = host
    context['form'] = form
    where = 'settings = True'
    if request.method == 'POST':
        form = SearchHostelForm(request.POST.copy())
        if form.is_valid():
            context['form'] = form
            number = form.cleaned_data["number"]
            hostel_number = form.cleaned_data["hostel_number"]
            floor = form.cleaned_data["floor"]
            room = form.cleaned_data["room"]
            length_choice = form.cleaned_data["length_choice"]
            university_name = form.cleaned_data["university_name"]
            if number:
                if where: where += " AND "
                where += "number = '%s'" % number
            if hostel_number:
                if where: where += " AND "
                where += "hostel_number = '%s'" % hostel_number
            if floor:
                if where: where += " AND "
                where += "floor = '%s'" % floor
            if room:
                if where: where += " AND "
                where += "block = '%s'" % room
            if length_choice:
                if length_choice == '1':
                    if where: where += " AND "
                    where += "status = True"
                if length_choice == '2':
                    if where: where += " AND "
                    where += "status = False"

            if university_name:
                if university_name == '1':
                    if where: where += " AND "
                    where += "content_universityinform.id = '1'"
            print where
            if where:
                cur2.execute("SELECT content_hostelinform.id, floor, block, number, short_number, password, ip, status, room, hostel_number, university_name_id, content_universityinform.name FROM content_hostelinform JOIN content_universityinform on(content_hostelinform.university_name_id = content_universityinform.id) WHERE %s ORDER BY floor, block, room;" % (where))
            else:
                cur2.execute("SELECT content_hostelinform.id, floor, block, number, short_number, password, ip, status, room, hostel_number, university_name_id, content_universityinform.name FROM content_hostelinform JOIN content_universityinform on(content_hostelinform.university_name_id = content_universityinform.id) WHERE settings = %s ORDER BY floor, block, room;" % (True,))

            host = cur2.fetchall()
            transaction.commit_unless_managed(settings.GLOBALHOME_DB2)
            context["host"] = host
        else:
#            request.notifications.add(_(u'Document successfully sent to %s' % email), 'success')
            context.update({'error': True})
            return context

    return context
def check_current_menu(obj):
    def wrapper(conf):
        if not conf.view_name == 'article_by_slug':
            return False
        slug = conf.kwargs['slug']
        if obj.slug and obj.slug == slug:
            return True
        ids = [i['id'] for i in obj.get_ancestors().values('id')]
        return obj.id in ids
    return wrapper

def content_list_base(request, model_class, amount_on_page):
    qs = model_class.frontend_objects.all()
    paginator = SimplePaginator(qs, amount_on_page)
    paginator.set_page(request.GET.get('page', 1))

    objs = paginator.get_page()
    for obj in objs:
        obj.processVars(("text", "summary"), request=request)
    page = None if not(request.GET.has_key('page')) else request.GET['page']
    return {
            'objects': objs,
            'paginator': paginator,
            'page': page,
            }

@render_to('content/article/list.html')
def article_list(request):
    response = content_list_base(request, Article, 10)
    response['meta_title'] = u'Статьи'
    return response



@render_to('content/article/object.html')
def article(request, id):

    if request.user.username:
        profile = request.user.get_profile()
        if not profile.user.is_superuser:
            raise Http404
    else:
        raise Http404
    obj = get_object_or_404(Article, pk=id)
    # вот тут мы подставляем все переменные
    obj.processVars(("text",), request=request)
    context = {}
    context['obj'] = obj
    context['current_view_name'] = check_current_menu(obj)
    return panel_base_auth(request, context)


@render_to('content/article/object.html')
def article_by_slug(request, slug):
    hide_review_slugs = ['payment_methods', 'payment_methods_cards', 'comepay_cards', 'payment_bank', 'mobi', 'comepay', 'mobi_money']
    obj = get_object_or_404(Article, slug=slug, is_published=True)
    # вот тут мы подставляем все переменные
    obj.processVars(("text",), request=request)
    context = {}
    context['obj'] = obj
    context['current_view_name'] = check_current_menu(obj)
    if slug in hide_review_slugs:
        context['hide_review'] = True
    if slug == 'hot_spot':
        coordhotspot = Connection_address.objects.filter(readiness_degree6__exact=1, persons__id=5).all()
        context['coordhotspot'] = coordhotspot
        allcities = Internet_city.objects.all()
        context['allcities'] = allcities
    return panel_base_auth(request, context)

@render_to('content/article/object.html')
def moscow_article_by_slug(request, prefix, slug):
    print 'slug = %s' % slug
    obj = get_object_or_404(Article_moscowdata, prefix__prefix=prefix, slug=slug, is_published=True)
    # вот тут мы подставляем все переменные
    obj.processVars(("text",), request=request)
    context = {}
    context['obj'] = obj
#    context['current_view_name'] = check_current_menu(obj)
#    context['meta_title'] = obj.meta_title or obj.name
#    context['meta_description'] = obj.meta_description or obj.summary
    return panel_base_auth(request, context)


def raw_article_by_slug(request, slug):
    obj = get_object_or_404(Article, slug=slug)
    obj.processVars(("text",), request=request)
    return HttpResponse(obj.text)


@render_to('content/news/list_%s.html' % settings.SITE_ID)
def news_list(request):
    if settings.SITE_ID in (1,):
        response = content_list_base(request, News, 10)
    elif settings.SITE_ID in (2,):
        response = content_list_base(request, News_Moscowdata, 10)
    return panel_base_auth(request, response)


@login_required
@render_to("check_view.html")
def check_view(request, number_id):
    now = datetime.datetime.now()
    start = datetime.datetime(now.year if now.month > 1 else now.year - 1, now.month - 1 if now.month > 1 else 12, 1).date()
#    initial=first_date().strftime("%d.%m.%Y")
#    _(u'Login or pin incorrect card!')
    qwe = start.strftime("%m")
    if qwe == '01':
        month = 'январь'
    elif qwe == '02':
        month = 'февраль'
    elif qwe == '03':
        month = 'март'
    elif qwe == '04':
        month = 'апрель'
    elif qwe == '05':
        month = 'май'
    elif qwe == '06':
        month = 'июнь'
    elif qwe == '07':
        month = 'июль'
    elif qwe == '08':
        month = 'август'
    elif qwe == '09':
        month = 'сентябрь'
    elif qwe == '10':
        month = 'октябрь'
    elif qwe == '11':
        month = 'ноябрь'
    elif qwe == '12':
        month = 'декабрь'
    else:
        month = ''

    end = datetime.datetime(now.year, now.month, 1).date()
    profile = request.user.get_profile()
    if not profile.user.is_superuser:
        raise Http404
    check = Check.objects.get(id=number_id)
    context = {}

    if check.sent:
        context["sent"] = True

    if str(check.created_by.email):
        eemail = str(check.created_by.email)
    else:
        eemail = ''
    data = {'email': eemail, }
    form = CheckForm(data)
    context["form"] = form

    if request.method == 'POST':
        form = CheckForm(request.POST.copy())
        if form.is_valid():

            context["form"] = form
            email = form.cleaned_data['email']

            # создаем письмо
            msg = EmailMultiAlternatives("email subject", "счета за %s месяц" % month, settings.DEFAULT_FROM_EMAIL, [email])
            msg.attach_alternative(check.text, "text/html")
            msg.attach_file('media/check/%s.htm' % check.name)
#            msg.attach_file('media/check/%s.htm' % filename1)
#            msg.attach_file('media/check/%s.htm' % filename2)
            msg.send()
            request.notifications.add(_(u'Document successfully sent to %s' % email), 'success')
            context["close_window"] = True
    context["check"] = check
    return context


def perewod(qqqq):
#        qqqq = '4000.11'
    desjtki_kop1 = ''
    desjtki_kop = ''
    kopeik = ''
    tisacha = ''
    tisacha1 = ''
    sotni = ''
    sotni1 = ''
    desjtki = ''
    desjtki1 = ''
    desjtki_tis = ''
    desjtki_tis1 = ''
    edin = ''
    sotni_tis1 = ''
    tisacha = ''
    sotni_tis = ''
    try:
        qq = qqqq.split('.')
    except Exception, e:
        print e
    try:
        kopeiki1 = qq[1]
    except:
        kopeiki1 = "00"
    try:
        rubli = qq[0]
    except:
        rubli = "0"

    # print len(kopeiki1[len(kopeiki1) - 2]) >= 0 and kopeiki1[len(kopeiki1) - 2] == '1'
    # print

#    kopeiki =qqqq[:-2] + qqqq[len(qqqq)-1]
    if (len(kopeiki1) - 2) >= 0 and kopeiki1[len(kopeiki1) - 2] == '1':
        kop = kopeiki1[len(kopeiki1) - 2] + kopeiki1[len(kopeiki1) - 1]
        if kop == '10':
            kopeik = 'десять' + ' копеек'
        if kop == '11':
            kopeik = 'одиннадцать' + ' копеек'
        if kop == '12':
            kopeik = 'двенадцать' + ' копеек'
        if kop == '13':
            kopeik = 'тринадцать' + ' копеек'
        if kop == '14':
            kopeik = 'четырнадцать' + ' копеек'
        if kop == '15':
            kopeik = 'пятнадцать' + ' копеек'
        if kop == '16':
            kopeik = 'шестнадцать' + ' копеек'
        if kop == '17':
            kopeik = 'семнадцать' + ' копеек'
        if kop == '18':
            kopeik = 'восемнадцать' + ' копеек'
        if kop == '19':
            kopeik = 'девятнадцать' + ' копеек'
    elif (len(kopeiki1) - 1) >= 0 and kopeiki1[len(kopeiki1) - 1] != '0':
        if kopeiki1[len(kopeiki1) - 1] == '1':
            kopeik = 'одна' + ' копейка'
        if kopeiki1[len(kopeiki1) - 1] == '2':
            kopeik = 'две' + ' копейки'
        if kopeiki1[len(kopeiki1) - 1] == '3':
            kopeik = 'три' + ' копейки'
        if kopeiki1[len(kopeiki1) - 1] == '4':
            kopeik = 'четыре' + ' копейки'
        if kopeiki1[len(kopeiki1) - 1] == '5':
            kopeik = 'пять' + ' копеек'
        if kopeiki1[len(kopeiki1) - 1] == '6':
            kopeik = 'шесть' + ' копеек'
        if kopeiki1[len(kopeiki1) - 1] == '7':
            kopeik = 'семь' + ' копеек'
        if kopeiki1[len(kopeiki1) - 1] == '8':
            kopeik = 'восемь' + ' копеек'
        if kopeiki1[len(kopeiki1) - 1] == '9':
            kopeik = 'девять' + ' копеек'
    if (len(kopeiki1) - 2) >= 0 and kopeiki1[len(kopeiki1) - 2] != '0' and kopeiki1[len(kopeiki1) - 2] != '1':
        if kopeiki1[len(kopeiki1) - 2] == '2':
            desjtki_kop = 'двадцать'
        if kopeiki1[len(kopeiki1) - 2] == '3':
            desjtki_kop = 'тридцать'
        if kopeiki1[len(kopeiki1) - 2] == '4':
            desjtki_kop = 'сорок'
        if kopeiki1[len(kopeiki1) - 2] == '5':
            desjtki_kop = 'пятьдесят'
        if kopeiki1[len(kopeiki1) - 2] == '6':
            desjtki_kop = 'шестьдесят'
        if kopeiki1[len(kopeiki1) - 2] == '7':
            desjtki_kop = 'семьдесят'
        if kopeiki1[len(kopeiki1) - 2] == '8':
            desjtki_kop = 'восемьдесят'
        if kopeiki1[len(kopeiki1) - 2] == '9':
            desjtki_kop = 'девяносто'
        desjtki_kop1 = desjtki_kop
        if  kopeiki1[len(kopeiki1) - 1] == '0':
            desjtki_kop1 = desjtki_kop + ' копеек'
    if (len(rubli) - 2) >= 0 and rubli[len(rubli) - 2] == '1':
        des = rubli[len(rubli) - 2] + rubli[len(rubli) - 1]
        if des == '10':
            edin = 'десять' + ' рублей'
        if des == '11':
            edin = 'одиннадцать' + ' рублей'
        if des == '12':
            edin = 'двенадцать' + ' рублей'
        if des == '13':
            edin = 'тринадцать' + ' рублей'
        if des == '14':
            edin = 'четырнадцать' + ' рублей'
        if des == '15':
            edin = 'пятнадцать' + ' рублей'
        if des == '16':
            edin = 'шестнадцать' + ' рублей'
        if des == '17':
            edin = 'семнадцать' + ' рублей'
        if des == '18':
            edin = 'восемнадцать' + ' рублей'
        if des == '19':
            edin = 'девятнадцать' + ' рублей'
    elif (len(rubli) - 1) >= 0 and rubli[len(rubli) - 1] != '0':
        if rubli[len(rubli) - 1] == '1':
            edin = 'один' + ' рубль'
        if rubli[len(rubli) - 1] == '2':
            edin = 'два' + ' рубля'
        if rubli[len(rubli) - 1] == '3':
            edin = 'три' + ' рубля'
        if rubli[len(rubli) - 1] == '4':
            edin = 'четыре' + ' рубля'
        if rubli[len(rubli) - 1] == '5':
            edin = 'пять' + ' рублей'
        if rubli[len(rubli) - 1] == '6':
            edin = 'шесть' + ' рублей'
        if rubli[len(rubli) - 1] == '7':
            edin = 'семь' + ' рублей'
        if rubli[len(rubli) - 1] == '8':
            edin = 'восемь' + ' рублей'
        if rubli[len(rubli) - 1] == '9':
            edin = 'девять' + ' рублей'
    if (len(rubli) - 2) >= 0 and rubli[len(rubli) - 2] != '0' and rubli[len(rubli) - 2] != '1':
        if rubli[len(rubli) - 2] == '2':
            desjtki = 'двадцать'
        if rubli[len(rubli) - 2] == '3':
            desjtki = 'тридцать'
        if rubli[len(rubli) - 2] == '4':
            desjtki = 'сорок'
        if rubli[len(rubli) - 2] == '5':
            desjtki = 'пятьдесят'
        if rubli[len(rubli) - 2] == '6':
            desjtki = 'шестьдесят'
        if rubli[len(rubli) - 2] == '7':
            desjtki = 'семьдесят'
        if rubli[len(rubli) - 2] == '8':
            desjtki = 'восемьдесят'
        if rubli[len(rubli) - 2] == '9':
            desjtki = 'девяносто'
        desjtki1 = desjtki
        if  rubli[len(rubli) - 1] == '0':
            desjtki1 = desjtki + ' рублей'
    if (len(rubli) - 3) >= 0 and rubli[len(rubli) - 3] != '0':
        if rubli[len(rubli) - 3] == '1':
            sotni = 'сто'
        if rubli[len(rubli) - 3] == '2':
            sotni = 'двести'
        if rubli[len(rubli) - 3] == '3':
            sotni = 'триста'
        if rubli[len(rubli) - 3] == '4':
            sotni = 'четыреста'
        if rubli[len(rubli) - 3] == '5':
            sotni = 'пятьсот'
        if rubli[len(rubli) - 3] == '6':
            sotni = 'шестьсот'
        if rubli[len(rubli) - 3] == '7':
            sotni = 'семьсот'
        if rubli[len(rubli) - 3] == '8':
            sotni = 'восемьсот'
        if rubli[len(rubli) - 3] == '9':
            sotni = 'девятьсот'
        sotni1 = sotni
        if  rubli[len(rubli) - 1] == '0' and rubli[len(rubli) - 2] == '0':
            sotni1 = sotni + ' рублей'
    if (len(rubli) - 5) >= 0 and rubli[len(rubli) - 5] == '1':
        tis = rubli[len(rubli) - 5] + rubli[len(rubli) - 4]
        if tis == '10':
            tisacha = 'десять' + ' тысяч'
        if tis == '11':
            tisacha = 'одиннадцать' + ' тысяч'
        if tis == '12':
            tisacha = 'двенадцать' + ' тысяч'
        if tis == '13':
            tisacha = 'тринадцать' + ' тысяч'
        if tis == '14':
            tisacha = 'четырнадцать' + ' тысяч'
        if tis == '15':
            tisacha = 'пятнадцать' + ' тысяч'
        if tis == '16':
            tisacha = 'шестнадцать' + ' тысяч'
        if tis == '17':
            tisacha = 'семнадцать' + ' тысяч'
        if tis == '18':
            tisacha = 'восемнадцать' + ' тысяч'
        if tis == '19':
            tisacha = 'девятнадцать' + ' тысяч'
        tisacha1 = tisacha
        if rubli[len(rubli) - 1] == '0' and rubli[len(rubli) - 2] == '0' and rubli[len(rubli) - 3] == '0':
            tisacha1 = tisacha + ' рублей'
    elif (len(rubli) - 4) >= 0 and rubli[len(rubli) - 4] != '0':
        if rubli[len(rubli) - 4] == '1':
            tisacha = 'одна тысяча'
        if rubli[len(rubli) - 4] == '2':
            tisacha = 'две тысячи'
        if rubli[len(rubli) - 4] == '3':
            tisacha = 'три тысячи'
        if rubli[len(rubli) - 4] == '4':
            tisacha = 'четыре тысячи'
        if rubli[len(rubli) - 4] == '5':
            tisacha = 'пять тысяч'
        if rubli[len(rubli) - 4] == '6':
            tisacha = 'шесть тысяч'
        if rubli[len(rubli) - 4] == '7':
            tisacha = 'семь тысяч'
        if rubli[len(rubli) - 4] == '8':
            tisacha = 'восемь тысяч'
        if rubli[len(rubli) - 4] == '9':
            tisacha = 'девять тысяч'
        tisacha1 = tisacha
        if rubli[len(rubli) - 4] == '0' and rubli[len(rubli) - 5] == '0' and rubli[len(rubli) - 6] == '0':
            tisacha1 = tisacha + ' рублей'
    if (len(rubli) - 5) >= 0 and rubli[len(rubli) - 5] != '0' and rubli[len(rubli) - 5] != '1':
        if rubli[len(rubli) - 5] == '2':
            desjtki_tis = 'двадцать'
        if rubli[len(rubli) - 5] == '3':
            desjtki_tis = 'тридцать'
        if rubli[len(rubli) - 5] == '4':
            desjtki_tis = 'сорок'
        if rubli[len(rubli) - 5] == '5':
            desjtki_tis = 'пятьдесят'
        if rubli[len(rubli) - 5] == '6':
            desjtki_tis = 'шестьдесят'
        if rubli[len(rubli) - 5] == '7':
            desjtki_tis = 'семьдесят'
        if rubli[len(rubli) - 5] == '8':
            desjtki_tis = 'восемьдесят'
        if rubli[len(rubli) - 5] == '9':
            desjtki_tis = 'девяносто'
        if rubli[len(rubli) - 4] == '0':
            desjtki_tis = desjtki_tis + ' тысяч'
        desjtki_tis1 = desjtki_tis
        if  rubli[len(rubli) - 4] == '0':
            desjtki_tis1 = desjtki_tis + ' рублей'
    if (len(rubli) - 6) >= 0 and rubli[len(rubli) - 6] != '0':
        if rubli[len(rubli) - 6] == '1':
            sotni_tis = 'сто'
        if rubli[len(rubli) - 6] == '2':
            sotni_tis = 'двести'
        if rubli[len(rubli) - 6] == '3':
            sotni_tis = 'триста'
        if rubli[len(rubli) - 6] == '4':
            sotni_tis = 'четыреста'
        if rubli[len(rubli) - 6] == '5':
            sotni_tis = 'пятьсот'
        if rubli[len(rubli) - 6] == '6':
            sotni_tis = 'шестьсот'
        if rubli[len(rubli) - 6] == '7':
            sotni_tis = 'семьсот'
        if rubli[len(rubli) - 6] == '8':
            sotni_tis = 'восемьсот'
        if rubli[len(rubli) - 6] == '9':
            sotni_tis = 'девятьсот'
        if rubli[len(rubli) - 5] == '0' and rubli[len(rubli) - 4] == '0':
            sotni_tis = sotni_tis + ' тысяч'
        sotni_tis1 = sotni_tis
        if  rubli[len(rubli) - 5] == '0' and rubli[len(rubli) - 4] == '0' and rubli[len(rubli) - 1] == '0' and rubli[len(rubli) - 2] == '0' and rubli[len(rubli) - 3] == '0':
            sotni_tis1 = sotni_tis + ' рублей'
    prrinnt = """
    %(sotni_tis1)s %(desjtki_tis1)s %(tisacha1)s  %(sotni1)s  %(desjtki1)s  %(edin)s %(desjtki_kop1)s %(kopeik)s
    """ % {
            "tisacha1": tisacha1,
            "sotni1": sotni1,
            "desjtki1": desjtki1,
            "edin": edin,
            "desjtki_kop1": desjtki_kop1,
            "kopeik": kopeik,
            "sotni_tis1": sotni_tis1,
            "desjtki_tis1": desjtki_tis1
         }
    return prrinnt


@login_required
def check_receipt(request):

    profile = request.user.get_profile()
    if not profile.user.is_superuser:
        raise Http404

    #########################################################################

    now = datetime.datetime.now()
    start = datetime.datetime(now.year if now.month > 1 else now.year - 1, now.month - 1 if now.month > 1 else 12, 1).date()
#    initial=first_date().strftime("%d.%m.%Y")
#    _(u'Login or pin incorrect card!')
    qwe = start.strftime("%m")
    if qwe == '01':
        month = 'январь'
    elif qwe == '02':
        month = 'февраль'
    elif qwe == '03':
        month = 'март'
    elif qwe == '04':
        month = 'апрель'
    elif qwe == '05':
        month = 'май'
    elif qwe == '06':
        month = 'июнь'
    elif qwe == '07':
        month = 'июль'
    elif qwe == '08':
        month = 'август'
    elif qwe == '09':
        month = 'сентябрь'
    elif qwe == '10':
        month = 'октябрь'
    elif qwe == '11':
        month = 'ноябрь'
    elif qwe == '12':
        month = 'декабрь'
    else:
        month = ''
    cur = connections[settings.BILLING_DB].cursor()
    cur2 = connections[settings.GLOBALHOME_DB2].cursor()



    end = datetime.datetime(now.year, now.month, 1).date()
    end_date = datetime.datetime(now.year, now.month, 2).date()
    cur2.execute("SELECT created_at FROM content_check WHERE created_at > %s;", (end,))
    datee = cur2.fetchall()

    transaction.commit_unless_managed(settings.BILLING_DB)
    transaction.commit_unless_managed(settings.GLOBALHOME_DB2)

    if datee:
        request.notifications.add(_(u'Documents for the current month have been received!'), 'warning')
        return HttpResponseRedirect('/admin/content/check/')


    cur2.execute("SELECT account_profile.billing_account_id, account_profile.user_id, auth_user.username, account_profile.company_name, auth_user.id, account_profile.id FROM account_profile JOIN auth_user on(account_profile.user_id = auth_user.id) WHERE is_juridical = %s and billing_account_id > %s;", (True, 0))
    for account_id in cur2.fetchall():
        service_1 = 0
        summ_for_service_1 = 0
        NDS_1 = 0
        summa_s_nds_1 = 0
        add_service_1_in_check = ""
        add_service_1_invoice = ""
        add_service_1_in_akt = ""
        service_2 = 0
        summ_for_service_2 = 0
        NDS_2 = 0
        summa_s_nds_2 = 0
        add_service_2_in_check = ""
        add_service_2_invoice = ""
        add_service_2_in_akt = ""
        service_3 = 0
        summ_for_service_3 = 0
        NDS_3 = 0
        summa_s_nds_3 = 0
        add_service_1_in_ak = ""
        add_service_1_invoic = ""
        add_service_1_in_check = ""
        add_service_3_in_check = ""
        add_service_3_invoice = ""
        add_service_3_in_akt = ""
        NDS_tel = 0
        summ_minus_NDS = 0
        add_telemate_in_akt = ""
        add_service_1_in_check1 = ""
        add_service_1_in_akt1 = ""
        add_service_1_invoice1 = ""
        all_summm = 0

        cur2.execute("SELECT account_address.address_line FROM account_profile_addresses JOIN account_address on(account_profile_addresses.address_id = account_address.id) WHERE profile_id = %s ORDER BY address_type;" % (account_id[5],))
        if cur2.fetchone():
            address_for_user = cur2.fetchone()[0]
        else:
            address_for_user = ""



        cur.execute("SELECT summ FROM billservice_phonetransaction WHERE account_id = %s and datetime >= %s and session_end < %s ;", (account_id[0], start, end,))
        the_number_of_calls = 0
        all_summ = 0
        for summa in cur.fetchall():
            the_number_of_calls = the_number_of_calls + 1
            all_summ = all_summ + summa[0]
#    cur.execute("SELECT * FROM billservice_accountaddonservice WHERE account_id = %s and action_status = %s;", (profile.billing_account_id, True,))
        cur.execute("SELECT SUM(summ), service_id, count(service_id) AS count_weq FROM billservice_addonservicetransaction WHERE account_id = %s and created >= %s and created < %s and check_sent = %s GROUP BY service_id;", (account_id[0], start, end_date, False,))
        service_for_ac = cur.fetchall()
        cur.execute("UPDATE billservice_addonservicetransaction SET check_sent = %s WHERE account_id = %s and created >= %s and created < %s and check_sent = %s;", (True, account_id[0], start, end_date, False,))
        if service_for_ac or all_summ > 0:
#            print service_for_ac
            for service_for_account in service_for_ac:
                print service_for_account[0]
                summ_for_service_1 = summ_for_service_1 + (float(service_for_account[0]) / 1.18)
                NDS_1 = (float(service_for_account[0]) / 1.18) * 0.18
                NDS_2 = NDS_2 + NDS_1
                summa_s_nds_1 = (float(service_for_account[0]) / 1.18) + NDS_1
                summm = (float(service_for_account[0]) / 1.18) / float(service_for_account[2])
                all_summm += summm
                cur.execute("SELECT name FROM billservice_addonservice WHERE id = %s;", (service_for_account[1],))
                service_name = cur.fetchone()[0]
                add_service_1_in_check = """
                                        <tr>
                                            <th align="left">%(service_name)s за %(month)s  %(yahr)s</th>
                                            <th>шт</th>
                                            <th>%(service_1)s</th>
                                            <th>%(service_for_account)s</th>
                                            <th>%(summ_for_service_1)s</th>
                                        </tr>
                """ % {
                        "service_name": service_name.encode('utf-8'),
                        "service_1": service_for_account[2],
                        "service_for_account": summm,
                        "summ_for_service_1": round(float(service_for_account[0]) / 1.18, 2),
                        "month": month,
                        "yahr": now.year,
                    }

                add_service_1_in_ak = """
                                        <tr>
                                            <th align="left">%(service_name)s за %(month)s  %(yahr)s</th>
                                            <th>%(service_1)s</th>
                                            <th>шт</th>
                                            <th>%(service_for_account)s</th>
                                            <th>%(summ_for_service_1)s</th>
                                        </tr>
                """ % {
                        "service_1": service_for_account[2],
                        "service_for_account": summm,
                        "service_name": service_name.encode('utf-8'),
                        "summ_for_service_1": round(float(service_for_account[0]) / 1.18, 2),
                        "month": month,
                        "yahr": now.year,
                    }
                add_service_1_invoic = """

                                    <tr>
                                        <th>%(service_name)s</th>
                                        <th>шт</th>
                                        <th>%(service_1)s</th>
                                        <th>%(service_for_account)s</th>
                                        <th>%(summ_for_service_1)s</th>
                                        <th>---</th>
                                        <th>---</th>
                                        <th>---</th>
                                        <th>18% %</th>
                                        <th>%(NDS_1)s</th>
                                        <th>%(summa_s_nds_1)s</th>
                                    </tr>
                                    """ % {
                                            "service_1": service_for_account[2],
                                            "service_for_account": summm,
                                            "summ_for_service_1": round(float(service_for_account[0]) / 1.18, 2),
                                            "NDS_1": round(NDS_1, 2),
                                            "service_name": service_name.encode('utf-8'),
                                            "summa_s_nds_1": summa_s_nds_1,
                                        }



                add_service_1_in_check1 = add_service_1_in_check1 + add_service_1_in_check
                add_service_1_in_akt1 = add_service_1_in_akt1 + add_service_1_in_ak
                add_service_1_invoice1 = add_service_1_invoice1 + add_service_1_invoic

            if all_summ > 0:

                summ_minus_NDS = float(all_summ) / 1.18
                NDS_tel = float(all_summ) - summ_minus_NDS
                add_telemate_in_check = """
                                        <tr>
                                            <th align="left">Телематические услуги за %(month)s  %(yahr)s</th>
                                            <th>шт</th>
                                            <th>1</th>
                                            <th>%(summ_minus_NDS)s</th>
                                            <th>%(summ_minus_NDS)s</th>
                                        </tr>
                """ % {
                        "month": month,
                        "yahr": now.year,
                        "summ_minus_NDS": round(summ_minus_NDS, 2),
                    }
                add_telemate_in_akt = """
                                        <tr>
                                            <th align="left">Телематические услуги за %(month)s  %(yahr)s</th>
                                            <th>1</th>
                                            <th>шт</th>
                                            <th>%(summ_minus_NDS)s</th>
                                            <th>%(summ_minus_NDS)s</th>
                                        </tr>
                """ % {
                        "month": month,
                        "yahr": now.year,
                        "summ_minus_NDS": round(summ_minus_NDS, 2),
                    }
                add_telemate_in_invoice = """

                                        <tr>
                                            <th>Телематические услуги за %(month)s  %(yahr)s</th>
                                            <th>796</th>
                                            <th>шт</th>
                                            <th>1</th>
                                            <th>%(summ_minus_NDS)s</th>
                                            <th>%(summ_minus_NDS)s</th>
                                            <th>---</th>
                                            <th>18% %</th>
                                            <th>%(NDS)s</th>
                                            <th>%(all_summ)s</th>
                                        </tr>

                """ % {
                        "month": month,
                        "yahr": now.year,
                        "all_summ": round(all_summ, 2),
                        "summ_minus_NDS": round(summ_minus_NDS, 2),
                        "NDS": round(NDS_tel, 2)
                    }
                add_telemate_in_check
            else:
                add_telemate_in_check = ""
                add_telemate_in_invoice = ""
                add_telemate_in_akt = ""
                add_service_1_in_ak = ""
                add_service_1_invoic = ""
                add_service_1_in_check = ""



#            add_service_1_in_check1 = add_service_1_in_check1 + add_service_1_in_check
#            add_service_1_in_akt1 = add_service_1_in_akt1 + add_service_1_in_ak
#            add_service_1_invoice1 = add_service_1_invoice1 + add_service_1_invoic
            NDS_all = NDS_tel + NDS_2 + NDS_3
            summ_for_service_all = float(summ_for_service_1) + float(summ_for_service_2) + float(summ_for_service_3) + float(summ_minus_NDS) + NDS_all
            summ_for_service_minus_NDS = summ_for_service_all - NDS_all
        #    print round(summ_for_service_all, 2)
        #    qqqq = str(round(summ_for_service_all, 2))
            qqqq = str(round(summ_for_service_all, 2))
            slowa_dlj_itogo = perewod(qqqq)
            filename = "check_for_" "%s" % account_id[2] + "_at_" + "%s" % start
            filename1 = "check_invoice_for_" "%s" % account_id[2] + "_at_" + "%s" % start
            filename2 = "akt_for_" "%s" % account_id[2] + "_at_" + "%s" % start
            cur2.execute("SELECT max(number) FROM content_check;")
            max_number = cur2.fetchone()
            print max_number
            cur2.execute("INSERT INTO content_check(created_by_id, created_at, modified_at, name, type, number) VALUES(%s, %s, %s, %s, %s, %s) RETURNING id;", (account_id[4], now, now, filename, 'check', (max_number[0] + 1)))
            id_from_check = cur2.fetchone()
            number_check = max_number[0] + 1
            cur2.execute("INSERT INTO content_check(created_by_id, created_at, modified_at, name, type, number) VALUES(%s, %s, %s, %s, %s, %s) RETURNING id;", (account_id[4], now, now, filename1, 'invoice', (max_number[0] + 1)))
            id_from_check_invoice = cur2.fetchone()
            number_check_invoice = max_number[0] + 1
            cur2.execute("INSERT INTO content_check(created_by_id, created_at, modified_at, name, type, number) VALUES(%s, %s, %s, %s, %s, %s) RETURNING id;", (account_id[4], now, now, filename2, 'act', (max_number[0] + 1)))
            id_from_akt = cur2.fetchone()
            number_akt = max_number[0] + 1
            cur2.execute("SELECT id FROM fin_docs_signeds WHERE signed_by_id = %s and findoc_id = %s;", (account_id[1], 1,))
            id_findoc = cur2.fetchone()
            profff = Profile.objects.get(id=account_id[5])
            now_date = datetime.date.today()
            invoice_date = now_date.replace(month=now_date.month - 1, day=calendar.mdays[now_date.month - 1])

            text = """
            <html>
             <head>
              <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
              <title>Счет № %(id_from_check)s на основании договора № %(id_findoc)s</title>
             </head>
             <body>
            <table>
            <thead>
                    <tr>
                    <th>
              <div align="left"><strong>Организация: ООО "Телеком-ВИСТ"</strong></div>
              <hr/>
              <div align="left"><address>Адрес: 125367, г. Москва, Врачебный проезд, д.10, офис 1</address></div>
                &nbsp;&nbsp;&nbsp;&nbsp;
                <table style="color:#black" border="1" cellpadding="4" cellspacing="0">
                <thead>
                            <tr bgcolor="#FBF0DB">
                                <th colspan="4">Образец заполнения платежного поручения</th>
                            </tr>
                </thead>
                            <tbody>
                                <tr>
                                   <th><h5>ИНН 7733720884 </h5></th>
                                   <th> <h5>КПП 773301001 </h5></th>
                                    <th><h5> &nbsp</h5></th>
                                     <th> <h5>&nbsp</h5></th>
                                </tr>
                                <tr>
                                    <th colspan="2"><h5> Получатель
                                     OOO "Телеком-ВИСТ"</h5></th>
                                    <th><h5> Сч. №</h5></th>
                                   <th><h5>40702810019001003512</h5></th>

                                </tr>
                                <tr>
                                    <th rowspan="2" colspan="2"> <div><h5>Банк получателя</h5></div>
                                    <div><h5>ОАО "Уралсиб" Московская обл. дирекция</h5></div> </th>
                                    <th><h5> БИК</h5></th>
                                   <th><h5>044552545</h5></th>

                                </tr>
                                <tr>

                                    <th><h5> Сч. №</h5></th>
                                   <th><h5>30101810500000000545</h5></th>

                                </tr>
                            </tbody>
                </table>
                <div >&nbsp </div>
               <h3 align="left"><strong>СЧЕТ №  %(id_from_check)s от %(date_check)s на основании договора № %(id_findoc)s</strong></h3>

                  <div align="left"> Поставщик: ИНН 7733720884 КПП 773301001 Общество с ограниченной ответственностью
                                    "Телеком-ВИСТ" 125367, Москва г, Врачебный проезд, д. 10, кв. 1, тел. (495) 785-64-89</div>
                  <hr />
                 <div align="left"> Покупатель: %(profile.company_name)s</div>
                 <div align="left"> Адрес: %(address_for_user)s</div>
                 <div align="left"> ИНН/КПП покупателя: %(inn)s/%(kpp)s</div>
                 <hr />


               <table style="color:#black" border="1" cellpadding="4" cellspacing="0">
                            <thead>
                                        <tr bgcolor="#FBF0DB">
                                            <th>Наименование</th>
                                            <th>Ед. изм.</th>
                                            <th>Количество</th>
                                            <th>Цена (Руб)</th>
                                            <th>Сумма (Руб)</th>
                                        </tr>
                            </thead>
                            <tbody>
                                        %(add_service_3_in_check)s
                                        %(add_service_1_in_check)s
                                        %(add_service_2_in_check)s
                                        %(add_summ_in_check)s
                                        <tr>
                                            <th>&nbsp</th>
                                            <th>&nbsp</th>
                                            <th>&nbsp</th>
                                            <th>&nbsp</th>
                                            <th>&nbsp</th>
                                        </tr>
                                        <tr>
                                            <th colspan="4" align="right">НДС 18% %</th>
                                            <th>%(NDS_all)s</th>
                                        </tr>
                                        <tr>
                                            <th colspan="4" align="right">Итого:</th>
                                            <th>%(summ_for_service_all)s</th>
                                        </tr>
                            </tbody>
                   </table>
                   <div>&nbsp;&nbsp;&nbsp;&nbsp;</div>
                         <h4 align="left"><address> Всего наименований %(count_naimen)s, на сумму: %(summ_for_service_all)s руб.</address><hr/><h4>
                         <h4 align="left"><address> %(slowa_dlj_itogo)s </address><hr/><h4>
                         <table>
                         <tr>

                             <th align="left"><h4>Руководитель предприятия </h4></th>
                             <th><h4>&nbsp&nbsp&nbsp&nbsp&nbsp </h4></th>
                             <th><h4>_______________(Локтишов И.М.)</h4></th>
                         </tr>
                         <tr>

                             <th align="left"><h4>Главный бухгалтер </h4></th>
                             <th><h4>&nbsp&nbsp&nbsp&nbsp&nbsp </h4></th>
                             <th><h4>_______________(Локтишов И.М.)</h4></th>
                         </tr>
                         </table>
              </th>
                    </tr>
                </thead>
                </table>
              </body>
              </html>
              """ % {
                        "profile.company_name": account_id[3].encode('utf-8'),
                        "add_summ_in_check": add_telemate_in_check,
                        "add_service_1_in_check": add_service_1_in_check1,
                        "add_service_2_in_check": add_service_2_in_check,
                        "add_service_3_in_check": add_service_3_in_check,
                        "NDS_all": round(NDS_all, 2),
                        "summ_for_service_all": round(summ_for_service_all, 2),
                        "id_from_check": "%s/1" % number_check,
                        "id_findoc": id_findoc[0],
                        "date_check": datetime.datetime.now().strftime("%d.%m.%Y"),
                        "count_naimen": all_summm + 1,
                        "slowa_dlj_itogo": slowa_dlj_itogo,
                        "address_for_user": address_for_user.encode('utf-8'),
                        "inn": profff.bank_address.encode('utf-8'),
                        "kpp": (str(profff.kpp)).encode('utf-8'),
                    }


            text2 = """
            <html>
            <head>
              <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
              <title>Счет-фактура № %(id_from_check)s на основании договора № %(id_findoc)s</title>
            </head>
            <body>
                <table >
                <thead>
                    <tr>
                    <th align="right">
                    Приложение N 1
к постановлению Правительства Российской Федерации
от 26 декабря 2011 г. N 1137


                       <h6> <div> Приложение N 1 </div>
                        <div> к постановлению Правительства Российской Федерации </div>
                        <div> от 26 декабря 2011 г. N 1137 </div>
                       </h6>
                    </th>
                    </tr>
                    <tr>
                    <th align="left">
                                        СЧЕТ-ФАКТУРА № %(id_from_check)s от %(date_invoice)s на основании договора № %(id_findoc)s
                        <h6> <div>Продавец: Общество с ограниченной ответственностью "Телеком-ВИСТ" (ООО "Телеком-ВИСТ")</div>
                        <div>Адрес: 125367, Москва г, Врачебный проезд, д. 10, кв. 1</div>
                        <div>ИНН/КПП продавца: 7733720884/773301001</div>
                        <div>Грузоотправитель и его адрес: ----</div>
                        <div>Грузополучатель и его адрес:----</div>
                        <div>К платежно-расчетному документу______________от____________</div>
                        <div>Покупатель: %(profile.company_name)s</div>
                        <div>Адрес: %(address_for_user)s</div>
                        <div>ИНН/КПП покупателя: %(inn)s/%(kpp)s</div></h6>
                        <div>Валюта: наименование, код  Российский рубль, 810</div>
                    <table style="color:#black" border="1" cellpadding="4" cellspacing="0">
                    <thead>
                                        <tr bgcolor="#FBF0DB">
                                            <th rowspan=2><h5>Наименование товара (описание выполненных работ, оказанных услуг), имущественного права</h5></th>
                                            <th colspan=2><h5>Единица измерения</h5></th>
                                            <th rowspan=2><h5>Количество (объем)</h5></th>
                                            <th rowspan=2><h5>Цена (тариф) за единицу измерения</h5></th>
                                            <th rowspan=2><h5>Стоимость товаров (работ, услуг), имущественных прав, всего без налога - всего</h5></th>
                                            <th rowspan=2><h5>В том числе акциз</h5></th>
                                            <th rowspan=2><h5>Налоговая ставка</h5></th>
                                            <th rowspan=2><h5>Сумма налога, предъявляемая покупателю</h5></th>
                                            <th rowspan=2><h5>Стоимость товаров (работ, услуг), имущественных прав, всего с налогом - всего</h5></th>
                                            <th colspan=2><h5>Страна происхождения товара</h5></th>
                                            <th rowspan=2><h5>Номер таможенной декларации</h5></th>
                                        </tr>
                                        <tr bgcolor="#FBF0DB">
                                        <th><h5>Код</h5></th>
                                        <th><h5>Условное обозначение (национальное)</h5></th>
                                        <th><h5>Цифровой код</h5></th>
                                        <th><h5>Краткое наименование</h5></th>
                                        </tr>

                                        <tr bgcolor="#FBF0DB">
                                        <th><h5>Код</h5></th>
                                        <th><h5>Условное обозначение (национальное)</h5></th>
                                        <th><h5>Цифровой код</h5></th>
                                        <th><h5>Краткое наименование</h5></th>
                                        </tr>

                    </thead>
                    <tbody>
                                        %(add_service_3_invoice)s
                                        %(add_service_1_invoice)s
                                        %(add_service_2_invoice)s
                                        %(add_telemate_in_invoice)s
                                        <tr>
                                            <td>&nbsp;</td>
                                            <td>&nbsp;</td>
                                            <td>&nbsp;</td>
                                            <td>&nbsp;</td>
                                            <td>&nbsp;</td>
                                            <td>&nbsp;</td>
                                            <td>&nbsp;</td>
                                            <td>&nbsp;</td>
                                            <td>&nbsp;</td>
                                            <td>&nbsp;</td>
                                            <td>&nbsp;</td>

                                        </tr>
                                        <tr>
                                            <td colspan="8"><strong>Всего к оплате</strong></td>
                                            <th>%(NDS_all)s</th>
                                            <th>%(summ_for_service_all)s</th>
                                        </tr>
                    </tbody>
                   </table>
                   <div>&nbsp;</div>
                   <div>&nbsp;</div>
                   <table>
                   <thead>
                   <tr>
                        <td>Руководитель организации</td>
                        <td>&nbsp;&nbsp;</td>
                        <td>_______________</td>
                        <td>&nbsp;</td>
                        <td>(Локтишов И.М.)</td>
                        <td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
                        <td>Главный бухгалтер </td>
                        <td>&nbsp;&nbsp;</td>
                        <td>_______________</td>
                        <td>&nbsp;</td>
                        <td>(Локтишов И.М.)</td>
                    </tr>
                    <tr>
                        <td><h6>&nbsp;</h6></td>
                        <td><h6>&nbsp;&nbsp;</h6></td>
                        <td align="center"><h6>(подпись)</h6></td>
                        <td><h6>&nbsp;</h6></td>
                        <td align="center">&nbsp;</td>
                        <td>&nbsp;</td>
                        <td>&nbsp;</td>
                        <td>&nbsp;</td>
                        <td align="center"><h6>(подпись)</h6></td>
                        <td><h6>&nbsp;</h6></td>
                        <td align="center">&nbsp;</td>
                    </tr>
                    <tr>
                        <td><h6>&nbsp;</h6></td>
                    </tr>
                    <tr>
                        <td>Индивидуальный предприниматель</td>
                        <td>&nbsp;&nbsp;</td>
                        <td>_______________</td>
                        <td>&nbsp;</td>
                        <td>_______________</td>
                        <td>&nbsp;</td>
                        <td>&nbsp;</td>
                        <td>&nbsp;</td>
                        <td colspan="3">________________________________</td>
                    </tr>
                    <tr>
                        <td><h6>&nbsp;</h6></td>
                        <td><h6>&nbsp;</h6></td>
                        <td align="center"><h6>(подпись)</h6></td>
                        <td><h6>&nbsp;</h6></td>
                        <td align="center"><h6>(ф.и.о.)</h6></td>
                        <td>&nbsp;</td>
                        <td>&nbsp;</td>
                        <td>&nbsp;</td>
                        <td colspan="3" align="center"><h6><div>(реквизиты свидетельства о государственной</div>
                                            <div>регистрации индивидуального предпринимателя)</div></h6></td>
                    </tr>
                   </thead>
                   </table>
                      <h6> ПРИМЕЧАНИЕ. Первый экземпляр - покупателю, второй экземпляр - продавцу</h6>
                </thead>
                </table>
            </body>
            </html>
            """ % {"add_telemate_in_invoice": add_telemate_in_invoice,
                "profile.company_name": account_id[3].encode('utf-8'),
                "add_service_1_invoice": add_service_1_invoice1,
                "add_service_2_invoice": add_service_2_invoice,
                "add_service_3_invoice": add_service_3_invoice,
                "NDS_all": round(NDS_all, 2),
                "summ_for_service_all": round(summ_for_service_all, 2),
                "id_from_check": "%s/2" % number_check,
                "id_from_check_invoice": number_check_invoice,
                "id_findoc": id_findoc[0],
                "address_for_user": address_for_user.encode('utf-8'),
                "inn": profff.bank_address.encode('utf-8'),
                "kpp": (str(profff.kpp)).encode('utf-8'),
                "date_invoice": invoice_date,
                }
            text3 = """
            <html>
            <head>
              <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
              <title>Акт № %(id_from_check)s на основании договора № %(id_findoc)s</title>
            </head>
            <body>
                <table>
                <thead>
                    <tr><th>&nbsp;</th></tr>
                    <tr>
                    <th align="left"><h3>Акт № %(id_from_check)s от %(date_invoice)s на основании договора № %(id_findoc)s<h3><hr/></th>
                    </tr>

                    <tr>
                    <th align="left">
                    <table>
                        <tr>
                        <td align="left"><h4>Исполнитель:</h4></td>
                        <td><h4>&nbsp;</h4></td>
                        <td align="left"><h4>Общество с ограниченной ответственностью "Телеком-ВИСТ" 125367, Москва г, Врачебный проезд, д. 10, кв. 1</h4></td>
                        </tr>
                        <tr>
                        <td align="left"><h4>Заказчик:</h4></td>
                        <td><h4>&nbsp;</h4></td>
                        <td align="left"><h4>%(profile.company_name)s %(address_for_user)s</h4></td>
                        </tr>
                    </table>
                    <tr><th>&nbsp;</th></tr>
                    <tr><th>&nbsp;</th></tr>
                    </th>
                    </tr>

                    <tr>
                    <th>
                                <table style="color:#black" border="1" cellpadding="4" cellspacing="0">
                                                    <thead>
                                                                        <tr bgcolor="#FBF0DB">
                                                                        <td><h4>Услуга</h4> </td>
                                                                        <td><h4>Кол-во </h4> </td>
                                                                        <td><h4>Ед.</h4> </td>
                                                                        <td><h4>Цена </h4> </td>
                                                                        <td><h4>Сумма </h4> </td>
                                                                        </tr>
                                                    </thead>
                                                    <tbody>

                                                                        %(add_service_3_in_akt)s
                                                                        %(add_service_1_in_akt)s
                                                                        %(add_service_2_in_akt)s
                                                                        %(add_telemate_in_akt)s
                                                                        <tr>
                                                                            <td>&nbsp;</td>
                                                                            <td>&nbsp;</td>
                                                                            <td>&nbsp;</td>
                                                                            <td>&nbsp;</td>
                                                                            <td>&nbsp;</td>
                                                                        </tr>
                                                                        <tr>
                                                                            <th colspan="4" align="right"><strong>Итого:</strong></th>
                                                                            <th>%(summ_for_service_all)s</th>
                                                                        </tr>
                                                                        <tr>
                                                                            <th colspan="4" align="right"><strong>В том числе НДС:</strong></th>
                                                                            <th>%(NDS_all)s</th>
                                                                        </tr>

                                                    </tbody>
                               </table>
                   </tr>
                   </th>
                   <tr><th>&nbsp;</th></tr>
                   <tr><th>&nbsp;</th></tr>
                   <tr align="left"><th>Всего оказано услуг на сумму: %(slowa_dlj_itogo)s, в т.ч. НДС - %(slowa_dlj_nds)s </th></tr>
                   <tr><th>&nbsp;</th></tr>
                   <tr align="left"><th>Вышеперечисленные услуги выполнены полностью и в срок. Заказчик претензий по объему, качеству и срокам оказания услуг не имеет.</th></tr>
                   <tr><th>&nbsp;</th></tr>
                   <tr><th>&nbsp;</th></tr>
                   <tr><th>&nbsp;</th></tr>
                        <table>
                             <tr>

                                 <th align="left"><h4>Исполнитель </h4></th>
                                 <th><h4>&nbsp&nbsp&nbsp&nbsp&nbsp </h4></th>
                                 <th><h4>_______________</h4></th>
                                 <th><h4>(Локтишов И.М.) </h4></th>
                                 <th><h4>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp </h4></th>
                                 <th><h4>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp </h4></th>
                                 <th><h4>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp </h4></th>
                                 <th align="left"><h4>Заказчик </h4></th>
                                 <th><h4>&nbsp&nbsp&nbsp&nbsp&nbsp </h4></th>
                                 <th><h4>_______________</h4></th>
                                 <th><h4>&nbsp&nbsp&nbsp</h4></th>
                                 <th><h4>_______________</h4></th>
                             </tr>

                            <tr><td>&nbsp;</td></tr>
                            <tr><td>&nbsp;</td></tr>
                            <tr><th>&nbsp;</th></tr>
                            <tr><th>&nbsp;</th></tr>
                            <tr><th>&nbsp;</th></tr>
                            <tr>
                                    <td>&nbsp;</td>
                                    <td>&nbsp;</td>
                                    <td align="center"><h3>М.П.</h3></td>
                                    <td>&nbsp;</td>
                                    <td>&nbsp;</td>
                                    <td>&nbsp;</td>
                                    <td>&nbsp;</td>
                                    <td>&nbsp;</td>
                                    <td>&nbsp;</td>
                                    <td align="center"><h3>М.П.</h3></td>
                                    <td>&nbsp;</td>
                                </tr>
                             </table>
                </thead>
                </table>
            </body>
            </html>
            """ % {
                "profile.company_name": account_id[3].encode('utf-8'),
                "add_service_1_in_akt": add_service_1_in_akt1,
                "add_service_2_in_akt": add_service_2_in_akt,
                "add_service_3_in_akt": add_service_3_in_akt,
                "add_telemate_in_akt": add_telemate_in_akt,
                "summ_for_service_minus_NDS": round(summ_for_service_minus_NDS, 2),
                "NDS_all": round(NDS_all, 2),
                "slowa_dlj_itogo": slowa_dlj_itogo,
                "summ_for_service_all": round(summ_for_service_all, 2),
                "id_from_akt": number_akt,
                "id_findoc": id_findoc[0],
                "id_from_check": "%s/3" % number_check,
                "date_invoice": invoice_date,
                "address_for_user": address_for_user.encode('utf-8'),
                "slowa_dlj_nds": perewod(str(round(NDS_all, 2))),
                }


            cur2.execute("UPDATE content_check SET text = %s WHERE id = %s;", (text, id_from_check))
            cur2.execute("UPDATE content_check SET text = %s WHERE id = %s;", (text2, id_from_check_invoice))
            cur2.execute("UPDATE content_check SET text = %s WHERE id = %s;", (text3, id_from_akt))


            import gzip, zipfile, zlib, shutil, os

            log.add("filename1=%s" % filename1)
            out_f1 = open('%s.htm' % filename1, 'w')
            out_f1.write(text2)
            out_f1.close()
            shutil.move('%s.htm' % filename1, 'media/check/%s.htm' % filename1)

            out_f = open('%s.htm' % filename, 'w')
            out_f.write(text)
            out_f.close()
            shutil.move('%s.htm' % filename, 'media/check/%s.htm' % filename)

            out_f = open('%s.htm' % filename2, 'w')
            out_f.write(text3)
            out_f.close()
            shutil.move('%s.htm' % filename2, 'media/check/%s.htm' % filename2)
        #    os.remove('%s.htm' % filename)
        #    context["display"] = filename

            transaction.commit_unless_managed(settings.GLOBALHOME_DB2)
            transaction.commit_unless_managed(settings.BILLING_DB)
        else:
            pass


    #########################################################################

#    qqqq = '10000.0'
#    slowa_dlj_itogo = perewod(qqqq)
    transaction.commit_unless_managed(settings.BILLING_DB)
    transaction.commit_unless_managed(settings.GLOBALHOME_DB2)
    request.notifications.add(_(u'Documents created successfully'), 'success')
    return HttpResponseRedirect('/admin/content/check/')


@login_required
@render_to("check_send_to_emai.html")
def send_to_emai(request, number_id):

    profile = request.user.get_profile()
    if not profile.user.is_superuser:
        raise Http404
    check = Check.objects.get(id=number_id)


    context = {}
    self.user = request.user

    sort = request.GET.get("sort")
    order = request.GET.get("order")

    form = CheckForm(request.GET)
    date_from = first_date()
    date_to = last_date()
    caller_number = ""
    called_number = ""
    account_id = 0
    called_account_id = 0
    length_choice = 0
    check_choice = 0
    context["form"] = form

    if form.is_valid():
        context["form"] = form
        caller_number = form.cleaned_data["caller_number"]


    context["check"] = check
    return context


@render_to('content/news/object.html')
def news(request, id):
    context = {}
    obj = get_object_or_404(News, pk=id)
    obj.processVars(("text", "summary"), request=request)
    context['obj'] = obj
#    context['meta_title']=obj.meta_title or obj.name
#    context['meta_description']=obj.meta_description or obj.summary
    return panel_base_auth(request, context)



@render_to('content/news/type_service_%s.html' % settings.SITE_ID)
def type_service(request):
    context = {'hide_review': True}
    return panel_base_auth(request, context)


@render_to('content/news/data_centr_%s.html' % settings.SITE_ID)
def data_centr(request):
    context = {}
    return panel_base_auth(request, context)


@render_to('content/news/sim_card.html')
def sim_card(request):
    context = {}
    return panel_base_auth(request, context)


@render_to('content/news/phone_service.html')
def phone_service(request):
    context = {}
    return panel_base_auth(request, context)


@render_to('content/news/payment_%s.html' % settings.SITE_ID)
def payment(request):
    context = {}
    context['hide_review'] = True
    return panel_base_auth(request, context)


@render_to('content/news/webphone.html')
def webphone(request):
    context = {}
    context['ws_servers'] = settings.WS_SERVERS
    return panel_base_auth(request, context)

def pannel_construct(request):
    pannel = ''
    but_panel = None
    if request.POST and request.POST.has_key("key"):
        key = request.POST["key"]
        try:
            but_panel = ButtonPanelHref.objects.get(key=key)
        except ButtonPanelHref.DoesNotExist:
            but_panel = None
    if not but_panel:
        default_url = request.META['PATH_INFO']
        try:
            url_obj = ButtonPanelUrls.objects.get(urls=default_url)
            key = url_obj.key_id
            but_panel = ButtonPanelHref.objects.get(key=key)
        except ButtonPanelUrls.DoesNotExist:
            but_panel = None
    if but_panel:
        href_obj_key = [but_panel.description_key, but_panel.how_much_key, but_panel.how_to_connect_key, but_panel.where_to_go_key]
        act_but_obj = [but_panel.description_action, but_panel.how_much_action, but_panel.how_to_connect_action, but_panel.where_to_go_action]
        param_list = [1, 1, 1, 1]
        try:
            param_list[act_but_obj.index(request.META['PATH_INFO'])] = 0
        except:
            pass
        value_list = [u'Описание', u'Сколько стоит', u'Как подключить', u'Куда обратиться']
        i = 0
        table = u''
        for sel in param_list:
            if sel == 0:
                table += u'''
                        <td id="activ_td_4link">%s</td>
                ''' % (value_list[i])
            if sel == 1:
                table += u'''
                        <td id="td_4link_1">
                        <form action="%s" id="form_descr" method="POST" name="form_hidden_field">
                        <input name="key" type="hidden" value="%s" >

                        <input  name="sub" type="submit" value='%s' >
                        </form>
                        </td>
                    ''' % (act_but_obj[i], href_obj_key[i], value_list[i])
            i += 1
        pannel = u''' <table align="center" class="quick_links" width="100%%">
                <tbody>
                    <tr>
                        %s
                     </tr>
                   </tbody>
                 </table>
                ''' % table
    return pannel
