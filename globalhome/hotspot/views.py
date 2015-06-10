# coding: utf-8

from lib.decorators import render_to, login_required
from django.http import HttpResponseRedirect, Http404
from hotspot.forms import DepositsHotSpot, HotSpotReviewForm, HotSpotComplaintForm
from cards.models import BillserviceCard
# from billing.models import BillserviceAccount
from decimal import Decimal
from account.models import Profile
import datetime
from time import strftime, localtime
from django.shortcuts import  HttpResponse
from django.utils.translation import ugettext_lazy as _
from hotspot.models import ActiveSession, HotSpotQueryStatistic, HotSpotRate, HotSpotReview, MainNews, Nas  # , HotSpotWeatger
# from datetime import timedelta
from types import NoneType
from payment.models import Billservice_transaction
# from cards.models import *
# from internet.models import Connection_address
from installed_mikrotiks.models import Mikrotik
# from  yandex_maps import api
from django.conf import settings
# from dateutil.relativedelta import relativedelta
# import pycurl
import urllib, sys, urllib2  # , cookielib
import re
from django.db.models import Max
from hotspot.models import Games, Games_Section
from django.db.models import Q
import base64
from  hotspot.models import MobiOrganizationsUnique
from django.shortcuts import get_object_or_404
from content.models import Article
from hotspot.models import MobiOrganizationsUserChanges
from hotspot.models import Video, VideoGenre, Comments_Of_Video, Video_Rate  # , Category, Tags, Get_SubEvent
# from django import template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from django.shortcuts import render_to_response
from django.db import transaction
from data_centr.models import Tariff
import psycopg2
from settings import DATABASES  # Может быть и локальное
from BeautifulSoup import BeautifulSoup
import requests, json
#from hotspot.models import TvChannels, TvForecastSources, TvForecast



HOTSPOT_SPEED = 15
AUTH_URL = 'http://globalhome.mobi/'
# AUTH_URL = 'http://192.168.137.1/'
AUTH_URL2 = 'http://gh.mobi/'
# AUTH_URL = 'http://192.168.0.214/'


def error_translate(error):
    AUTH_ERRORS = {'invalid username or password': u'Неправильный логин или пароль',
                   'RADIUS server is not responding': u'Ошибка авторизации, попробуйте повторить через минуту',
                   }


    if error.startswith('no more sessions are allowed for user'):
        return u'Превышено количество сессий для пользователя ' + error.split()[7]
    else:
        if error and not AUTH_ERRORS.has_key(error):
            print "AUTH_ERRORS: '%s'" % error
        return AUTH_ERRORS.get(error, error)


from django.contrib.auth import authenticate, login as _login, logout as _logout
from lib.helpers import redirect
from account.views import get_base_url
from django.core.urlresolvers import reverse
def hotspot_identity(request):
    context = {}
    def find_price_internet(iden):
        cost = ''
        name = iden
        tarif_id = None
        try:
            cost = Nas.objects.get(name=iden).data_centr_tarif.price_id.cost
            return cost
        except Nas.DoesNotExist:
            send_email(u'Нет значения в таблице "nas_nas"', "hotspot.views.find_price_internet: Нет такого значения 'name' равного '%s' в таблице БД Nas('nas_nas') " % (str(iden)), settings.DEFAULT_FROM_EMAIL, ["Zz1n@globalhome.su", 'sales@globalhome.su', 'noc@globalhome.su'])
            return 10


    context['cost_connection'] = 10
    # context['message_obshaga'] = "Внимание! С 31.09.2014 по 08.10.2014 года в общежитии будут проводиться технические работы по улучшению качества Wi-Fi покрытия, в связи с этим возможны перебои в предоставлении услуг доступа к интернет. Приносим свои извинения за предоставленные неудобства."

    identity = request.POST.get('identity') or request.COOKIES.get('identity')
    if identity == 'GH2' or identity == 'GH1':
        context['message_obshaga'] = """\
        Вниманию пользователей общежития!
        Информируем вас, что, начиная с 27 октября 2014г., будет предоставлена возможность подключения по технологии Ethernet. Приобретённые ранее карты HotSpot-доступа могут быть использованы как для авторизации в сети Wi-Fi общежития, так и для технологии Ethernet
        """
    if request.POST.has_key('identity'):
        if request.POST.get('identity'):
            context['cost_connection'] = find_price_internet(request.POST.get('identity'))
    elif request.COOKIES.has_key('identity'):
        if request.COOKIES.get('identity'):
            context['cost_connection'] = find_price_internet(request.COOKIES.get('identity'))

    if request.GET.has_key('q'):
        context['search_submit'] = True

    context['rew_form'] = HotSpotReviewForm()
    context['comp_form'] = HotSpotComplaintForm()
    context['auth_url'] = AUTH_URL
    context['hotspot_speed'] = HOTSPOT_SPEED

    reg_b = re.compile(r"(android|bb\\d+|meego).+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino", re.I | re.M)
    reg_v = re.compile(r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\\-|your|zeto|zte\\-", re.I | re.M)
    if request.META.has_key('HTTP_USER_AGENT'):
        user_agent = request.META['HTTP_USER_AGENT']
        b = reg_b.search(user_agent)
        v = reg_v.search(user_agent[0:4])
        if b or v:
            context['mobile'] = True
        else:
            context['mobile'] = False
    context['linkorig'] = AUTH_URL2
    if request.POST.has_key('identity') or request.COOKIES.has_key('identity'):
        if request.POST.has_key('identity'):
            ident = request.POST.get('identity')
        elif request.COOKIES.has_key('identity'):
            ident = urllib.unquote(request.COOKIES.get('identity'))
        trial = False
        if ident:
            try:
                print 'ident = "%s"' % ident
                installed_location = Mikrotik.objects.get(name_of_mikrotik=ident)
                context['address'] = installed_location.get_address()
                time_free = installed_location.last_day_of_test - datetime.datetime.now().date()
                trial = time_free.days
                # trial = True
                if trial <= 0:
                    trial = False
                context['cur_microtik_coordinates'] = str(installed_location.get_address().x) + ':' + str(installed_location.get_address().y) + ':' + str(installed_location.get_address())
            except Mikrotik.DoesNotExist:
                trial = 30
        # except Exception:
        #    trial = 30

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # trial = 30
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!

        if trial == False:
            context['event'] = True
            # context['free_internet'] = True # Ключ для бесплатного интернета
        if request.POST.has_key('identity'):
            # print "post=%s" % request.POST
            # print request.POST.get('chap-id')
            # print request.POST.get('chap-challenge')
            context['trial'] = trial
            context['mac'] = request.POST.get('mac')
            context['ip'] = request.POST.get('ip')
            context['username'] = request.POST.get('username')
            context['linklogin'] = request.POST.get('link-login')
            context['linkorig'] = AUTH_URL2  # request.POST.get('link-orig')
            context['error'] = error_translate(request.POST.get('error', ''))
            context['chapid'] = request.POST.get('chap-id')
            context['chapchallenge'] = request.POST.get('chap-challenge')
            context['linkloginonly'] = request.POST.get('link-login-only')  # linkloginonly),
            context['linkorigesc'] = AUTH_URL2  # request.POST.get('link-orig-esc'),
            context['identity'] = request.POST.get('identity')
            context['macesc'] = request.POST.get('mac-esc')
            context['link'] = 'http://news.yandex.ru/Belgium/index5.utf8.js'
            context['chapidenc'] = base64.b64encode(request.POST.get('chap-id', ''))
            context['chapchallengeenc'] = base64.b64encode(request.POST.get('chap-challenge', ''))
            context['identity_clear_log_off'] = True
            context['content_trafic'] = False


        elif request.COOKIES.get('identity'):
            # print "cook=%s" % request.COOKIES
            # print request.COOKIES.get('chapid', '')
            # print urllib.unquote(request.COOKIES.get('chapid', ''))
            # print urllib.unquote(request.COOKIES.get('chapchallenge', ''))
            context['trial'] = trial
            context['mac'] = urllib.unquote(request.COOKIES.get('mac', ''))
            context['ip'] = urllib.unquote(request.COOKIES.get('ip', ''))
            context['username'] = urllib.unquote(request.COOKIES.get('username', ''))
            context['linklogin'] = urllib.unquote(request.COOKIES.get('linklogin', ''))
            context['linkorig'] = AUTH_URL2  # request.POST.get('link-orig')
            context['error'] = error_translate(urllib.unquote(request.COOKIES.get('error', '')))
            context['identity_clear_log_off'] = True
            context['chapidenc'] = urllib.unquote(request.COOKIES.get('chapidenc', ''))
            context['chapchallengeenc'] = urllib.unquote(request.COOKIES.get('chapchallengeenc', ''))


            try:
                chapid = urllib.unquote(request.COOKIES.get('chapidenc', ''))
                context['chapid'] = base64.b64decode(chapid)
            except:
                print "chapid='%s'" % request.COOKIES.get('chapidenc', '')
                print "chapid_unq='%s'" % urllib.unquote(request.COOKIES.get('chapidenc', ''))
                context['chapid'] = ''
                context['chapidenc'] = ''
            try:
                chapchallenge = urllib.unquote(request.COOKIES.get('chapchallengeenc', ''))
                context['chapchallenge'] = base64.b64decode(chapchallenge)
            except:
                print "chapchallenge='%s'" % request.COOKIES.get('chapchallengeenc', '')
                print "chapchallenge_unq='%s'" % urllib.unquote(request.COOKIES.get('chapchallengeenc', ''))
                context['chapchallenge'] = ''
                context['chapchallengeenc'] = ''
            context['linkloginonly'] = urllib.unquote(request.COOKIES.get('linkloginonly', ''))  # linkloginonly),
            context['linkorigesc'] = AUTH_URL2  # request.POST.get('link-orig-esc'),
            context['identity'] = urllib.unquote(request.COOKIES.get('identity', ''))
            context['macesc'] = urllib.unquote(request.COOKIES.get('macesc', ''))
            context['link'] = 'http://news.yandex.ru/Belgium/index5.utf8.js'


        else:
            context['no_content'] = True

            # context['trial'] = False
    else:
        context['no_content'] = True  #Изменить на True перед заливкой!!!!!
    # context['no_content'] = False
    # context['trial'] = True
    if request.GET.has_key('bytes-in-nice'):
            context['bytesinnice'] = request.GET.get('bytes-in-nice')
            context['username'] = request.GET.get('username')
            context['linkadvert'] = request.GET.get('link-advert')
            context['hotspot_advert'] = request.GET.get('hotspot_advert')
            context['linklogout'] = request.GET.get('link-logout')
            context['loginby'] = request.GET.get('login-by')
            context['ip'] = request.GET.get('ip')
            context['sessiontimeleft'] = request.GET.get('session-time-left')
            context['uptime'] = request.GET.get('uptime')
            context['blocked'] = request.GET.get('blocked')
            context['refreshtimeout'] = request.GET.get('refresh-timeout')
            context['bytesoutnice'] = request.GET.get('bytes-out-nice')
            context['hostname'] = request.GET.get('hostname')
            context['content_trafic'] = True

    elif request.COOKIES.has_key('bytesinnice'):
        context['bytesinnice'] = urllib.unquote(request.COOKIES.get('bytesinnice', ''))
        context['username'] = urllib.unquote(request.COOKIES.get('username', ''))
        context['linkadvert'] = urllib.unquote(request.COOKIES.get('linkadvert', ''))
        context['hotspot_advert'] = urllib.unquote(request.COOKIES.get('hotspot_advert', ''))
        context['linklogout'] = urllib.unquote(request.COOKIES.get('linklogout', ''))
        context['loginby'] = urllib.unquote(request.COOKIES.get('loginby', ''))
        context['ip'] = urllib.unquote(request.COOKIES.get('ip', ''))
        context['sessiontimeleft'] = urllib.unquote(request.COOKIES.get('sessiontimeleft', ''))
        context['uptime'] = urllib.unquote(request.COOKIES.get('uptime', ''))
        context['blocked'] = urllib.unquote(request.COOKIES.get('blocked', ''))
        context['refreshtimeout'] = urllib.unquote(request.COOKIES.get('refreshtimeout', ''))
        context['bytesoutnice'] = urllib.unquote(request.COOKIES.get('bytesoutnice', ''))
        context['hostname'] = urllib.unquote(request.COOKIES.get('hostname', ''))
        context['content_trafic'] = True

    else:
        context['content_trafic'] = False  # Изменить на False перед заливкой

    # login

    if request.GET.has_key('username'):
        username = request.GET.get('username')
        password = request.GET.get('password2')
        user = authenticate(username=username, password=password)
        try:
            if user.is_authenticated():
                if user.is_active:
                    _login(request, user)
        except:
            pass

    # Выбор поиска
    context['yandex'] = True
    # context['google'] = True

    if not(request.COOKIES.has_key('bytesinnice')) and not request.GET.has_key('bytes-in-nice') and not request.COOKIES.get('identity') and not request.POST.has_key('identity'):
        context['no_microtic'] = True
    # Определение принадлежности к жилому сектору или общежитию
    if request.POST.get('identity') == 'mikluho-maklaya23' or request.COOKIES.get('identity') == 'mikluho-maklaya23':
        context['hostel'] = True
    else:
        context['residential_sector'] = True
    now = datetime.datetime.now()
    context['now'] = now.strftime('%Y-%m-%d')
    context['first_page_date'] = (now - datetime.timedelta(31)).strftime('%Y-%m-%d')
    return context


# myimports
from hotspot.models import MobiWeather
from hotspot.models import WeatherCountries
from xml.dom.minidom import *



@login_required
@render_to("payment_hotspot.html")
def payment_hotspot(request):
    context = {}
    context['title'] = u"Пополнение счёта с помощью hotspot карты"
    if request.method == 'POST':
        form = DepositsHotSpot(request.POST.copy())
        if form.is_valid():
            now = datetime.datetime.now()
            form_login = form.cleaned_data.get('login')
            form_pin = form.cleaned_data.get('pin')
            try:  # get
                card = BillserviceCard.objects.get(login=form_login, pin=form_pin)
                print "card: %s" % card
                print "card.date %s" % card.end_date
                # Если номинал карточки равен нулю, то карточка уже использовалась.
                if card.nominal == 0:
                    context['form'] = DepositsHotSpot()
                    request.notifications.add(u'Данная комбинация логина и пароля активирована ранее', 'error')
                    return context
                # Если срок использования карточки истёк
                if card.end_date < now:
                    print "date"
                    context['form'] = DepositsHotSpot()
                    request.notifications.add(u'Истёк срок использования карточки', 'error')
                    return context

            except BillserviceCard.DoesNotExist:
                print "except billservice card"
                form = DepositsHotSpot()
                context['form'] = form
                request.notifications.add(u'Данная комбинация логина или пароля не найдена', 'error')
                return context

            profile = Profile.objects.get(user=request.user)
            now = datetime.datetime.now()
            ins = Billservice_transaction(
                                          bill=u'Пополнение счёта картой экспресc оплаты',
                                          account_id=profile.billing_account.id, type_id="ACCESS_CARD_PAY",
                                          approved=True, summ=card.nominal , created=now,
                                          description=u'Пополнение счёта картой доступа %s' % card.login,
                                          )
            ins.save()
            card.nominal = Decimal(0)
            card.activated = now
            card.activated_by_id = profile.billing_account_id
            card.save()
            request.notifications.add(u'Пополнение счета завершено.', 'success')

    else:
        form = DepositsHotSpot()
    context['form'] = form
    return context


@login_required
@render_to("hotspot_statistic.html")
def hotspot_statistic(request):
    from hotspot.forms import DateFilterForm
    from lib.paginator import SimplePaginator
    from lib.http import get_query_string
    context = {}
    context['current_view_name'] = "hotspot_statistic"
    context['hotspot_statistic'] = True
    context['title'] = u"История hotspot сессии"
    profile = Profile.objects.get(user=request.user)
    if 'filter' in request.GET:
        form = DateFilterForm(request.GET)
    else:
        form = DateFilterForm()

    if form.is_valid():
        # print "valid"
        date_from = form.cleaned_data["date_from"]
        date_to = form.cleaned_data["date_to"]
        # print date_from, type(date_to)
        if date_from and date_to:
            if date_from > date_to:
                request.notifications.add(_(u"You have selected an incorrect date interval!"), "warning")
                return HttpResponseRedirect("/account/internet/hotspot/statistic")
            else:
                if date_to - date_from > datetime.timedelta(days=91):
                    request.notifications.add("Разница между 'дата с' и  'дата по' должна быть неболее чем 90 дней!", "warning")
                    context['form'] = form
                    return context
                    # return HttpResponseRedirect("/account/internet/hotspot/statistic")

        active_session = ActiveSession.objects.filter(account_id=profile.billing_account_id , date_start__range=[date_from, date_to], date_end__range=[date_from, date_to])
        sum_time = sum_input = sum_output = 0
        for s in active_session:
            if type(s.bytes_in) == NoneType:
                s.bytes_in = int(0)
            if type(s.bytes_out) == NoneType:
                s.bytes_out = int(0)
            sum_input = sum_input + (s.bytes_in)
            sum_output = sum_output + (s.bytes_out)
            sum_time = sum_time + s.session_time
            s.session_time = datetime.timedelta(seconds=s.session_time)
        sum_all = sum_input + sum_output
        context['sum_time'] = datetime.timedelta(seconds=sum_time)
        context['sum_input'] = sum_input
        context['sum_all'] = sum_all
        context['sum_output'] = sum_output

        query = get_query_string(request, exclude=("page",))
        paginator = SimplePaginator(active_session, 25, "?page=%%s&%s" % query)
        paginator.set_page(request.GET.get("page", 1))
        context['active_session'] = paginator.get_page()
        context['paginator'] = paginator

    context['form'] = form
    context['statistic'] = True
    return context


@render_to("hotspot_login.html")
def hotspot_login(request):
    context = {}
    context['placement'] = 1
    # context['search_query'] = "fffff"

    # if request.POST.has_key('query'):
    #    context['search_query'] = request.POST.get('query')
    #    print "==============================="
    #    print request.POST.get('query')
    #    print "======================="

    # if request.GET.has_key('q'):
    #    context['query'] = True
    context['login_page'] = True
    context['date_d'] = strftime("%d-%m-%Y", localtime())
    context['news_bunner'] = MainNews.objects.filter(date_get_news__gte=datetime.datetime.today().date()).order_by("?")[:7]
    transaction.commit_unless_managed(using=settings.BILLING_DB)

    # print 'context=%s' % context

    # if request.POST.has_key('hidden_form'):
        # print request.POST['hidden_form']

    # For Google Search
    if request.GET.has_key('cx') and request.GET.get('q'):
        query_obj = HotSpotQueryStatistic(query_string=request.GET.get('q'))
        query_obj.save()
        context['search'] = True
        context['query'] = request.GET.get('q')

    # For Yandex Search
    if (request.GET and 'query' in request.GET) or ('query' in request.COOKIES and request.COOKIES.has_key('popup')) :
        context['search'] = True
        if request.GET and request.GET['query'] == '' :
            context['emp'] = True
        else:
            if request.GET.get('query'):
                query_obj = HotSpotQueryStatistic(query_string=request.GET.get('query'))
                query_obj.save()

            from lib.ya_s_xml.search import YaSearch
            # from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
            reload(sys)
            sys.setdefaultencoding('utf8')
            y = YaSearch(settings.XML_YANDEX_API_USER, settings.XML_YANDEX_API_KEY)
            if request.GET and request.GET.has_key("query") :
                qury_str, page = request.GET.get('query').encode('utf-8'), request.GET.get('page', 1)
            elif request.COOKIES and request.COOKIES.has_key("query"):
                qury_str, page = urllib.unquote(request.COOKIES.get('query')).encode('utf-8'), 1  # request.COOKIES.get('page')
            try:
                results = y.search(qury_str, int(page))
#                 try:
#                     results = y.search(urllib.unquote(request.COOKIES['query']).encode('utf-8'),page=1)#, page=int(request.GET.get('page', 1)))
#                 except Exception, e:
#                     print e
                if results and results.error is None:
                    res_list = []
                    range = int(request.GET.get('page', 1))
                    if int(range) == 1:
                        pass
                        t = 0
                        mun = range
                    else:
                        mun = (range - 1) * 10
                        t = 1
                        max_range = (range - 1) * 10 + 1
                        context['m_r'] = range - 1
                        for i in xrange(1, max_range):
                            res_list.append({})
                    for result in results.items:

                        if result.headline != '':
                            snip = result.headline
                        else:
                            snip = result.snippet
                        res_obj_dict = {'href': result.url,
                                        'title': result.title,
                                        'snip':snip,
                                         'num':mun + t}
                        res_list.append(res_obj_dict)
                        t += 1
                    len(res_list)
                    for i in xrange(1, 71):
                            res_list.append({})
                    paginator = Paginator(res_list, 10)  # Show 10 contacts per page
                    page = request.GET.get('page', 1)
                    try:
                        res_list = paginator.page(page)
                    except PageNotAnInteger:
                        res_list = paginator.page(1)
                    except EmptyPage:
                        res_list = paginator.page(paginator.num_pages)
                    context['ya_res'] = res_list
                    context['ya_spr'] = '<a href = "http://www.yandex.ru/" class = "ya_sprite">нашёл %s страниц </a>' % results.pages.numerator
                    context['begun'] = True
                    try:
                        context['query'] = request.GET['query']
                    except:
                        context['query'] = request.COOKIES['query']
                        context['popup'] = True
                else:
                    if results.error:
                        print unicode(results.error.code) + ' ' + results.error.description.encode('utf-8')
                    context['ya_res'] = [{'title': "К сожалению данных не найдено"}]

            except:
                context['ya_res'] = [{'title': "К сожалению данных не найдено"}]

    else:
        pass
        # print "ya_error"



    sRevDate_now = strftime("%Y-%m-%d", localtime())

    try:
        rate_object = HotSpotRate.objects.filter(date=sRevDate_now)
        rate_list = []
        for rate in rate_object:
            if rate.char_code == 'EUR' or rate.char_code == 'USD'or rate.char_code == 'GBP':
                rate_list.append(rate)
        context['rate_list'] = rate_list
    except Exception, e:
        print e
#     погода
#     try:
#         wether_object = HotSpotWeatger.objects.all().aggregate(Max('id'))
#         wether_object_top = HotSpotWeatger.objects.filter(date=sRevDate_now).aggregate(Max('id'))
#         wether_object = HotSpotWeatger.objects.get(id=wether_object_top['id__max'])
#         context['wether'] = wether_object
#     except Exception, e:
#         print e
#
#
#     передадим актуальную погоду по москве
#     записываем в базу погоду если надо обновить данные
#    take_weather(35)
#    weather_list = get_weather_context_main_page(35)
#    if weather_list:
#        context['current_weather_list'] = weather_list

    context.update(hotspot_identity(request))



    return context



def ajax_hotspot_information(request):

    def table_builder(inf_object, adres_str, map_id):

        if inf_object.x and inf_object.y:
            manuf_adr = str(inf_object.x) + ', ' + str(inf_object.y)
        try:
            table_result = u'''<div id = 'table'>
                                    <h5>%(name)s</h5>
                                    <ul class ='tr'><li class='th'>%(lable_adress)s</li><li class='td'>%(adres)s</li></ul>
                                    <ul class ='tr'><li class='th'>%(lable_phone)s</li><li class='td'>%(phone)s</li></ul> 
                            '''
            if inf_object.subway_station != '':
                table_result += u''' <ul class ='tr'><li class='th'>%(lable_subway_station)s</li><li class='td'>%(subway_station)s</li></ul>'''
            if inf_object.web_site != '':
                table_result += u''' <ul class ='tr'><li class='th'>%(lable_web)s</li><li class='td'>%(web)s</li></ul>'''
            if inf_object.email != '':
                table_result += u''' <ul class ='tr'><li class='th'>%(lable_email)s</li><li class='td'>%(email)s</li></ul>'''
            if inf_object.fax != '':
                table_result += u''' <ul class ='tr'><li class='th'>%(lable_fax)s</li><li class='td'>%(fax)s</li></ul>'''
            if inf_object.add_information != '':
                table_result += u''' <ul class ='tr'><li class='th'>%(lable_add_information)s</li><li class='td'>%(add_information)s</li></ul>'''
            table_result += u'''<input type = 'button' value = 'Показать на карте' OnClick='show_map(this,"%(adres_str)s","%(manuf_adr)s")'>
                                <div id = 'ya_map' style="display:none; ">
                                <div id="%(map_id)s" style="width: 750px; height: 400px"></div>
                                </div>
                                </div>
                                '''

            table_result = table_result % { 'name':u'%s' % inf_object.name,
                                            'adres':u'%s' % inf_object.adress,
                                            'lable_adress':u'%s' % u'Адрес:',
                                            'phone':u'%s' % inf_object.tel_numbers,
                                            'lable_phone':u'%s' % u'Номер телефона:',
                                            'subway_station':u'%s' % inf_object.subway_station,
                                            'lable_subway_station':u'%s' % u'Станция метро:',
                                            'web':u'%s' % inf_object.web_site,
                                            'lable_web':u'%s' % u'Сайт организации:',
                                            'email':u'%s' % inf_object.email,
                                            'lable_email':u'%s' % u'Адрес электронной почты:',
                                            'fax':u'%s' % inf_object.fax,
                                            'lable_fax':u'%s' % u'Факс:',
                                            'add_information':u'%s' % inf_object.add_information,
                                            'lable_add_information':u'%s' % u'Время работы:',
                                            'map_id': u'%s' % map_id,
                                            'x':u'%s' % inf_object.x,
                                            'y':u'%s' % inf_object.y,
                                            'adres_str':u'%s' % adres_str,
                                            'manuf_adr':u'%s' % manuf_adr,

                                            }

        except Exception, e:
            import os, sys
            print "Exception in write_off_of_money: '%s'" % e
            exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print "Exception in write_off_of_money: file:%s line:%s" % (fname, exc_tb.tb_lineno)

        return  table_result





    if request.POST and request.POST.has_key('type') and request.POST.has_key('identity'):
            tables = u"К сожалению данных не найдено"

            try:
                # 13-yaparkovaya20k1
                # if request.POST.has_key('identity_adm'):
                #    installed_location = Mikrotik.objects.get(name_of_mikrotik=request.POST['identity_adm'])
                # elif request.COOKIES.has_key('identity_adm'):
                #    installed_location = Mikrotik.objects.get(name_of_mikrotik=request.COOKIES['identity_adm'])
                installed_location = Mikrotik.objects.get(name_of_mikrotik=request.POST['identity'])
                # installed_location = Mikrotik.objects.get(name_of_mikrotik='13-yaparkovaya20k1')

            except Mikrotik.DoesNotExist:
                return HttpResponse(tables)
            adres_obj = installed_location.get_address()

            if request.POST['type'] == 'admin':
                try:
                    adres_str = str(adres_obj.y) + ', ' + str(adres_obj.x)
                    if adres_obj.home_administration.all()[0].district_administration.prefecturs:
                        tables = table_builder(adres_obj.home_administration.all()[0].district_administration.prefecturs, adres_str, 'map_1')
                    if adres_obj.home_administration.all()[0].district_administration:
                        tables += table_builder(adres_obj.home_administration.all()[0].district_administration, adres_str, 'map_2')
                    if adres_obj.home_administration.all():
                        i = 3
                        for tablel in adres_obj.home_administration.all():
                            tables += table_builder(tablel, adres_str, 'map_%s' % i)
                            i += 1

                except:
                    return HttpResponse(tables)
            if request.POST['type'] == 'manufactures':
                pass


    else:
        raise Http404

    return HttpResponse(tables)


@render_to("rate_date.html")
def finance_history(request):
    context = {}
    context['placement'] = 15
    context['rate_data'] = True
    now = datetime.datetime.now()
    context['now'] = now.strftime('%Y-%m-%d')
    context['first_page_date'] = (now - datetime.timedelta(31)).strftime('%Y-%m-%d')
    context['rate_date_now'] = now.strftime('%d.%m.%Y')
    context['first_date'] = (now - datetime.timedelta(31)).strftime('%d.%m.%Y')
    select_date = None
    if request.GET.has_key('select_date'):
        select_date = request.GET.get('select_date')
        print select_date
    else:
        select_date = context['first_page_date']
    context['select_date'] = select_date
    # context['name'] = request.GET.get('name')
    second_date = None
    if request.GET.has_key('second_date'):
        second_date = request.GET.get('second_date')
        print second_date
    else:
        second_date = context['now']
    context['second_date'] = second_date
    calendr = []
    calendr2 = []
    try:
        calendr = select_date.split('-')[2] + "." + select_date.split('-')[1] + "." + select_date.split('-')[0]
        calendr2 = second_date.split('-')[2] + "." + second_date.split('-')[1] + "." + second_date.split('-')[0]
    except:
        pass
    context['calendr'] = calendr
    context['calendr2'] = calendr2
    if request.GET.has_key('char_code'):
        char_code = request.GET.get('char_code')
        try:
            context['name'] = HotSpotRate.objects.filter(char_code=char_code)[0].name
        except Exception, ex:
            print ex
            raise Http404
        context['char_code'] = char_code
        context['date_select'] = date_select = HotSpotRate.objects.filter(Q(char_code=char_code))  # & Q(date = select_date))
        context['date_select_second'] = date_select = HotSpotRate.objects.filter(Q(char_code=char_code)).order_by('-date')
        try:
            context['select_char_code'] = HotSpotRate.objects.exclude(char_code=char_code).filter(date=datetime.datetime.now())
        except Exception, ex:
            print ex
            raise Http404
        try:
            context['ob_code'] = HotSpotRate.objects.filter(char_code=char_code, date__range=[select_date, second_date]).order_by('-date')  # [:31]
        except Exception, ex:
            raise Http404
    else:
        raise Http404
        # context['ob_code'] = HotSpotRate.objects.filter(char_code=char_code).order_by('-date')[:31]
    context.update(hotspot_identity(request))
    return context



@render_to("hotspot_rate.html")
def hotspot_rate(request):
    context = {}
    context['placement'] = 15
    context['rate_page'] = True
    now = datetime.datetime.now()
    context['now'] = now.strftime('%Y-%m-%d')
    context['first_page_date'] = (now - datetime.timedelta(31)).strftime('%Y-%m-%d')
    yesterday = datetime.datetime.today().date() - datetime.timedelta(1)
    tomorrow = datetime.datetime.today().date() + datetime.timedelta(1)
    global_quotes_tomorrow = HotSpotRate.objects.filter((Q(char_code='GBP') | Q(char_code='USD') | Q(char_code='EUR')) & Q(date=tomorrow)).order_by('name')
    global_quotes_yesterday = HotSpotRate.objects.filter((Q(char_code='GBP') | Q(char_code='USD') | Q(char_code='EUR')) & Q(date=yesterday)).order_by('name')
    global_quotes = HotSpotRate.objects.filter((Q(char_code='GBP') & Q(date=datetime.datetime.today().date()) | Q(char_code='USD') & Q(date=datetime.datetime.today().date()) | Q(char_code='EUR') & Q(date=datetime.datetime.today().date()))).order_by('name')
    side_quotes = HotSpotRate.objects.filter((Q(char_code='CNY') | Q(char_code='UAH') | Q(char_code='BYR')) & Q(date=datetime.datetime.today().date())).order_by('-name')
    side_quotes_yesterday = HotSpotRate.objects.filter((Q(char_code='CNY') | Q(char_code='UAH') | Q(char_code='BYR')) & Q(date=yesterday)).order_by('-name')
    side_quotes_tomorrow = HotSpotRate.objects.filter((Q(char_code='CNY') | Q(char_code='UAH') | Q(char_code='BYR')) & Q(date=tomorrow)).order_by('-name')
    other_quotes = HotSpotRate.objects.exclude((Q(char_code='BYR') | Q(char_code='GBP') | Q(char_code='EUR') | Q(char_code='USD') | Q(char_code='CNY') | Q(char_code='UAH'))).filter(Q(date=datetime.datetime.today().date()))
    other_quotes_yesterday = HotSpotRate.objects.exclude((Q(char_code='BYR') | Q(char_code='GBP') | Q(char_code='EUR') | Q(char_code='USD') | Q(char_code='CNY') | Q(char_code='UAH'))).filter(Q(date=yesterday))
    other_quotes_tomorrow = HotSpotRate.objects.exclude((Q(char_code='BYR') | Q(char_code='GBP') | Q(char_code='EUR') | Q(char_code='USD') | Q(char_code='CNY') | Q(char_code='UAH'))).filter(Q(date=tomorrow))
    context['zip_g'] = zip(global_quotes, global_quotes_yesterday)  # , global_quotes_tomorrow
    context['zip'] = zip(other_quotes, other_quotes_yesterday)  # , other_quotes_tomorrow
    context['zip_s'] = zip(side_quotes, side_quotes_yesterday)  # , side_quotes_tomorrow
    context.update(hotspot_identity(request))
    return context



def ajax_hotspot_review(request):
    if not request.POST.has_key('ident_field'):
        raise Http404
    # print request.POST
    if request.POST.get('ident_field') == 'complaint' or request.POST.get('ident_field') == 'review':
        subj_dict = {'complaint':u'Новая жалоба',
                     'review':u'Новый отзыв'
                     }

        form = HotSpotReviewForm(request.POST)
        if form.is_valid():
            subj = subj_dict[request.POST.get('ident_field')]
            complaint_object = HotSpotReview(
                                         contact_face=request.POST.get('contact_face'),
                                         adres=request.POST.get('adres'),
                                         mail=request.POST.get('mail'),
                                         telnumber=request.POST.get('telnumber'),
                                         text=request.POST.get('text'),
                                         type=request.POST.get('ident_field')
                                         )
            complaint_object.save()
            complaint_object.send_info_mail(subj)
            return HttpResponse(u'Компнаия Globalhome благодарит вас за Ваше участие!!!')
        else:
            error_string = u'%s' % form.errors
            result = error_string[56:99]
            return HttpResponse(result)
    else:
        return HttpResponse(u'В данный момент сервис не доступен')


@render_to("not_aval.html")
def not_aval_func(request):
    context = {}
    context['hotspot_speed'] = HOTSPOT_SPEED
    # print request.GET

    if request.GET.has_key('opt'):
        option = u'%s' % (request.GET['opt'])
        if (option == u'Аптеки'):
            context['title'] = u'Аптеки рядом с вами'
            context['description'] = u'Адреса аптек которые находятся недалеко от Вас.'
            context['keywords'] = u'аптеки, адреса, рядом с вами'

        elif(option == u'Банки'):
            context['title'] = u'Банки рядом с вами'
            context['description'] = u'Адреса банков которые находятся недалеко от Вас.'
            context['keywords'] = u'банки, адреса, рядом с вами'

        elif(option == u'Рестораны'):
            context['title'] = u'Рестораны рядом с вами'
            context['description'] = u'Адреса ресторанов которые находятся недалеко от Вас.'
            context['keywords'] = u'рестораны, адреса, рядом с вами'

        elif(option == u'Бытовые услуги'):
            context['title'] = u'Бытовые услуги рядом с вами'
            context['description'] = u'Адреса бытовых услуг которые находятся недалеко от Вас.'
            context['keywords'] = u'бытовые услуги, адреса, рядом с вами'

        elif(option == u'Медицина'):
            context['title'] = u'Медицинские учреждения рядом с вами'
            context['description'] = u'Адреса медицинских учреждений которые находятся недалеко от Вас.'
            context['keywords'] = u' медицинские учреждения, адреса, рядом с вами'

        elif(option == u'Продуктовые магазины'):
            context['title'] = u'Продуктовые магазины рядом с вами'
            context['description'] = u'Адреса продуктовых магазинов которые находятся недалеко от Вас.'
            context['keywords'] = u'продуктовые магазины, адреса, рядом с вами'

        elif(option == u'Парикмахерские и салоны красоты'):
            context['title'] = u'Парикмахерские и салоны красоты рядом с вами'
            context['description'] = u'Адреса парикмахерских и салонов красоты которые находятся недалеко от Вас.'
            context['keywords'] = u'парикмахерские, салоны красоты, адреса, рядом с вами'

        elif(option == u'Спорт'):
            context['title'] = u'Спортивные учреждения рядом с вами'
            context['description'] = u'Адреса спортивные учреждения которые находятся недалеко от Вас.'
            context['keywords'] = u'спортивные учреждения, адреса, рядом с вами'

        elif(option == u'Торговые центры'):
            context['title'] = u'Торговые центры рядом с вами'
            context['description'] = u'Адреса торговых центров которые находятся недалеко от Вас.'
            context['keywords'] = u'торговые центры, адреса, рядом с вами'

        elif(option == u'Кинотеатры'):
            context['title'] = u' Кинотеатры рядом с вами'
            context['description'] = u'Адреса кинотеатров которые находятся недалеко от Вас.'
            context['keywords'] = u' кинотеатры, адреса, рядом с вами'

        elif(option == u'Достопримечательности'):
            context['title'] = u'Достопримечательности рядом с вами'
            context['description'] = u'Адреса достопримечательностей которые находятся недалеко от Вас.'
            context['keywords'] = u'достопримечательности, адреса, рядом с вами'

        elif(option == u'Заправки'):
            context['title'] = u' Заправки рядом с вами'
            context['description'] = u'Адреса парикмахерских и салонов красоты которые находятся недалеко от Вас.'
            context['keywords'] = u'заправки, адреса, рядом с вами'

        elif(option == u'Форум вашего дома'):
            context['title'] = u'Форум вашего дома'
            context['description'] = u'Списки форумов жилых домов по адресу.'
            context['keywords'] = u'форум дома, форум жилого дома, дом'

        elif(option == u'Работа'):
            context['title'] = u'Поиск вакансий'
            context['description'] = u'Актуальные вакансии для работодателей и соискателей.'
            context['keywords'] = u'работа, вакансии, поиск работы'
        context['main_title'] = request.GET.get('opt')
    return context


@render_to("page_news.html")
def all_news(request):
    context = {}
    context['placement'] = 13
    news_obj = MainNews.objects.filter(date_get_news__gte=datetime.datetime.today().date())
        # context['it'] = 'all_news'
    context['title'] = 'Новости. Ленты новостей'
    context['description'] = 'Все самые актуальные новости и события в одной ленте.'
    context['keywords'] = 'новости, актуальные новости, лента новостей'
    context['news'] = True
    context['news_page'] = True
    if request.GET.has_key('out'):
        out = request.GET.get('out')
        context['linked_news_object'] = MainNews.objects.get(id=out)
        news_obj = news_obj.exclude(id=out)
    context['news_obj'] = news_obj.order_by("?")[:6]
    context.update(hotspot_identity(request))
    return context


@render_to("page_news.html")
def main_news(request, slug):
    context = {}
    context['placement'] = 13
    if (slug == 'politics'):
        context['title'] = 'Новости политики'
        context['description'] = 'Самые актуальные новости и события из мира политики.'
        context['keywords'] = 'новости, события, политика'

    elif (slug == 'culture'):
        context['title'] = 'Новости культуры'
        context['description'] = 'Самые актуальные новости и события из мира культуры.'
        context['keywords'] = 'новости, события, культура'

    elif (slug == 'economy'):
        context['title'] = 'Новости экономики'
        context['description'] = 'Самые актуальные новости и события из мира экономики.'
        context['keywords'] = 'новости, события, экономика'

    elif (slug == 'science'):
        context['title'] = 'Новости науки и техники'
        context['description'] = 'Самые актуальные новости и события из мира науки и техники.'
        context['keywords'] = 'новости, события, наукаб техника'

    elif (slug == 'sport'):
        context['title'] = 'Новости спорта'
        context['description'] = 'Самые актуальные новости и события из мира спорта.'
        context['keywords'] = 'новости, события, спорт'

    elif (slug == 'rus'):
        context['title'] = 'Новости России'
        context['description'] = 'Самые актуальные новости и события в России.'
        context['keywords'] = 'новости, события, россия'

    elif (slug == 'world'):
        context['title'] = 'Новости в мире'
        context['description'] = 'Самые актуальные новости и события в мире.'
        context['keywords'] = 'новости, события, мир'

    elif (slug == 'auto'):
        context['title'] = 'Новости авто'
        context['description'] = 'Самые актуальные новости и события из мира авто.'
        context['keywords'] = 'новости, события, авто'

    elif (slug == 'latest'):
        context['title'] = 'Новости в России и мире'
        context['description'] = 'Самые актуальные новости и события в России и мире.'
        context['keywords'] = 'новости, события, мир, россия'
    else:
        raise Http404

    if slug == 'latest':
        types_obj = MainNews.objects.filter(date_get_news=datetime.datetime.now().date()).distinct('news_type')
        news_obj = []
        for type in types_obj:
            lat_news = MainNews.objects.filter(date_get_news=datetime.datetime.now().date(), news_type=type.news_type).order_by("-id")[:1]
            news_obj.append(lat_news[0])
    else:
        news_obj = MainNews.objects.filter(date_get_news=datetime.datetime.now().date(), news_type=slug).order_by("?")[:6]
        context['it'] = slug

#    elif request.GET and request.GET.has_key('out'):
#        news_obj = []
#        try:
#            out_news = MainNews.objects.get(id=request.GET.get('out'))
#        except MainNews.DoesNotExist:
#            raise Http404
#        # print out_news.news_type
#        context['it'] = out_news.news_type
#        news_obj.append(out_news)
#        dop_news = MainNews.objects.filter(date_get_news=datetime.datetime.now().date(), news_type=out_news.news_type).order_by("?")[:5]
#        for new in dop_news:
#            news_obj.append(new)

    # else:
    #    news_obj = MainNews.objects.filter(date_get_news__gte=datetime.datetime.today().date()).order_by("?")[:6]
    #    #context['it'] = 'all_news'

    context['news_page'] = True
    context['news_obj'] = news_obj
    context.update(hotspot_identity(request))
    return context

@render_to("view_administration.html")
def view_administration(request):
    context = {}
    context['placement'] = 11
    if request.POST:  # .has_key('identity_administration'):
        context['submit'] = True

    context['administration_page'] = True
    context.update(hotspot_identity(request))
    # ajax_hotspot_information(request)
    def table_builder(inf_object, adres_str, map_id):

        if inf_object.x and inf_object.y:
            manuf_adr = str(inf_object.x) + ', ' + str(inf_object.y)
        try:
            table_result = u'''<div id = 'table'>
                                    <h5>%(name)s</h5>
                                    <ul class ='tr'><li class='th'>%(lable_adress)s</li><li class='td'>%(adres)s</li></ul>
                                    <ul class ='tr'><li class='th'>%(lable_phone)s</li><li class='td'>%(phone)s</li></ul> 
                            '''
            if inf_object.subway_station != '':
                table_result += u''' <ul class ='tr'><li class='th'>%(lable_subway_station)s</li><li class='td'>%(subway_station)s</li></ul>'''
            if inf_object.web_site != '':
                table_result += u''' <ul class ='tr'><li class='th'>%(lable_web)s</li><li class='td'>%(web)s</li></ul>'''
            if inf_object.email != '':
                table_result += u''' <ul class ='tr'><li class='th'>%(lable_email)s</li><li class='td'>%(email)s</li></ul>'''
            if inf_object.fax != '':
                table_result += u''' <ul class ='tr'><li class='th'>%(lable_fax)s</li><li class='td'>%(fax)s</li></ul>'''
            if inf_object.add_information != '':
                table_result += u''' <ul class ='tr'><li class='th'>%(lable_add_information)s</li><li class='td'>%(add_information)s</li></ul>'''
            table_result += u'''<input type = 'button' value = 'Показать на карте' OnClick='show_map(this,"%(adres_str)s","%(manuf_adr)s")'>
                                <div id = 'ya_map' style="display:none; ">
                                <div id="%(map_id)s" style="width: 750px; height: 400px"></div>
                                </div>
                                </div>
                                '''

            table_result = table_result % { 'name':u'%s' % inf_object.name,
                                            'adres':u'%s' % inf_object.adress,
                                            'lable_adress':u'%s' % u'Адрес:',
                                            'phone':u'%s' % inf_object.tel_numbers,
                                            'lable_phone':u'%s' % u'Номер телефона:',
                                            'subway_station':u'%s' % inf_object.subway_station,
                                            'lable_subway_station':u'%s' % u'Станция метро:',
                                            'web':u'%s' % inf_object.web_site,
                                            'lable_web':u'%s' % u'Сайт организации:',
                                            'email':u'%s' % inf_object.email,
                                            'lable_email':u'%s' % u'Адрес электронной почты:',
                                            'fax':u'%s' % inf_object.fax,
                                            'lable_fax':u'%s' % u'Факс:',
                                            'add_information':u'%s' % inf_object.add_information,
                                            'lable_add_information':u'%s' % u'Время работы:',
                                            'map_id': u'%s' % map_id,
                                            'x':u'%s' % inf_object.x,
                                            'y':u'%s' % inf_object.y,
                                            'adres_str':u'%s' % adres_str,
                                            'manuf_adr':u'%s' % manuf_adr,

                                            }

        except Exception, e:
            import os, sys
            print "Exception in write_off_of_money: '%s'" % e
            exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print "Exception in write_off_of_money: file:%s line:%s" % (fname, exc_tb.tb_lineno)

        return table_result
    tables = u"К сожалению данных не найдено"
    context['tables'] = tables
    if request.COOKIES.has_key('administration'):  # request.POST and  and request.POST.has_key('type') #original

            tables = u"К сожалению данных не найдено"
            try:
                installed_location = Mikrotik.objects.get(name_of_mikrotik=request.COOKIES['administration'])
                adres_obj = installed_location.get_address()
            except Mikrotik.DoesNotExist:
                context['tables'] = tables




            # if request.POST['type'] == 'admin':
            try:
                adres_str = str(adres_obj.y) + ', ' + str(adres_obj.x)
                if adres_obj.home_administration.all()[0].district_administration.prefecturs:
                    tables = table_builder(adres_obj.home_administration.all()[0].district_administration.prefecturs, adres_str, 'map_1')
                    context['tables'] = tables
                if adres_obj.home_administration.all()[0].district_administration:
                    tables += table_builder(adres_obj.home_administration.all()[0].district_administration, adres_str, 'map_2')
                    context['tables'] = tables
                if adres_obj.home_administration.all():
                    i = 3
                    for tablel in adres_obj.home_administration.all():
                        tables += table_builder(tablel, adres_str, 'map_%s' % i)
                        context['tables'] = tables
                        i += 1
            except:
                pass

    return context

@render_to("page_view_games.html")
def view_games(request, section):
    context = {}
    context['placement'] = 16
    try:
        # g_sec = Games_Section.objects.get(name=section)
        g_sec = Games_Section.objects.get(short_name=section)
    except Games_Section.DoesNotExist:
        raise Http404
    games = Games.objects.filter(section_game__short_name=section)
    context['header_games_title'] = g_sec

    context[g_sec.short_name] = True
    context['enumerate'] = enumerate(games)
    context['enumer'] = enumerate(games)
    context['games'] = True
    context['date_d'] = strftime("%d-%m-%Y", localtime())
    context.update(hotspot_identity(request))
    return context


#=======================================================================================
# функция автоматизации забора погоды с ресурса openweather
def openweatherfun(time_part, ddt, i, city_weather_id=35):
    if i.nodeName == 'time' and (time_part in str(i.getAttribute('from'))):
                day = i.getAttribute('from')[0:int(i.getAttribute('from').find('T'))]

                for j in i.childNodes:
                    if (j.nodeName == 'symbol'):
                        precipitation = j.getAttribute('name')
                    if (j.nodeName == 'clouds'):
                        cloud = j.getAttribute('value')
                        if precipitation != cloud:
                            cloud = cloud + ' ' + precipitation
                    if (j.nodeName == 'temperature'):
                        temp_from = j.getAttribute('min')
                        temp_to = j.getAttribute('max')
                    if (j.nodeName == 'windSpeed'):
                        wind_speed = j.getAttribute('mps')
                    if (j.nodeName == 'windDirection'):
                        wind_dir = j.getAttribute('code')
                    if (j.nodeName == 'pressure'):
                        pressure = j.getAttribute('value')
                    if (j.nodeName == 'humidity'):
                        humidity = j.getAttribute('value')

                mw = MobiWeather(source_name='openweathermap.org',
                              taking_date=datetime.datetime.now(),
                              date=day,
                              date_date_time=ddt,
                              cloud=cloud,
                              temp_from=temp_from,
                              temp_to=temp_to,
                              wind_speed=wind_speed,
                              wind_dir=wind_dir,
                              pressure=pressure,
                              humidity=humidity,
                              city_weather_id=WeatherCountries.objects.get(id=city_weather_id),

                             )
                mw.save()
# ======================================================================================
# забираем с openweather
def take_from_open_weather(city_weather_id):
    weathercountries_obj = WeatherCountries.objects.get(id=city_weather_id)
    ADRESS = 'http://api.openweathermap.org/data/2.5/forecast?q=' + weathercountries_obj.openweathermap_name + '&mode=xml'  # for mosow only
    file = urllib2.urlopen(ADRESS)
    data = file.read()
    file.close()
    doc = parseString(data)
    root = doc.documentElement
    # создадим по 4 записи в таблицу в бд на каждый день
    for q in root.childNodes:
        if q.nodeName == 'forecast':
            for i in q.childNodes:
                openweatherfun('T06:00:00', 1, i, city_weather_id)
                openweatherfun('T12:00:00', 2, i, city_weather_id)
                openweatherfun('T18:00:00', 3, i, city_weather_id)
                openweatherfun('T21:00:00', 4, i, city_weather_id)

#=======================================================================================
def take_from_yandex(city_weather_id):
    weathercountries_obj = WeatherCountries.objects.get(id=city_weather_id)
    # берем с yandex погода 10 дней
    ADRESS = 'http://export.yandex.ru/weather-ng/forecasts/' + str(weathercountries_obj.yandex_city_id) + '.xml'  # for mosow only
    file = urllib2.urlopen(ADRESS)
    data = file.read()
    file.close()
    doc = parseString(data)
    root = doc.documentElement
    # создадим по 4 записи в таблицу в бд на каждый день (это все для скриптоса)
    for q in root.childNodes:
        if q.nodeName == 'day':
            day = q.getAttribute('date')  # это день
            for i in q.childNodes:
                if (i.nodeName == 'day_part') and ((i.getAttribute('type') == 'morning') or (i.getAttribute('type') == 'day') or (i.getAttribute('type') == 'evening')or(i.getAttribute('type') == 'night')):  # первый тип времени дня
                    for j in i.childNodes:
                        if (j.nodeName == 'weather_type'):  # облачность
                            cloud = j.childNodes[0].nodeValue
                        if (j.nodeName == 'temperature_from'):
                            temp_from = j.childNodes[0].nodeValue  # температура от
                        if (j.nodeName == 'temperature_to'):
                            temp_to = j.childNodes[0].nodeValue  # температура от
                        if (j.nodeName == 'wind_speed'):
                            wind_speed = j.childNodes[0].nodeValue  # скорость ветра
                        if (j.nodeName == 'wind_direction'):  # направление ветра
                            wind_dir = j.childNodes[0].nodeValue
                        if (j.nodeName == 'mslp_pressure'):  # давление
                            pressure = j.childNodes[0].nodeValue
                        if (j.nodeName == 'humidity'):  # влажность
                            humidity = j.childNodes[0].nodeValue

                    if ((i.getAttribute('type') == 'morning')):
                        ddt = 1
                    elif ((i.getAttribute('type') == 'day')):
                        ddt = 2
                    elif ((i.getAttribute('type') == 'evening')):
                        ddt = 3
                    elif ((i.getAttribute('type') == 'night')):
                        ddt = 4
                    mw = MobiWeather(source_name='yandex',
                                      taking_date=datetime.datetime.now(),
                                      date=day,
                                      date_date_time=ddt,
                                      cloud=cloud,
                                      temp_from=temp_from,
                                      temp_to=temp_to,
                                      wind_speed=wind_speed,
                                      wind_dir=wind_dir,
                                      pressure=pressure,
                                      humidity=humidity,
                                      city_weather_id=WeatherCountries.objects.get(id=city_weather_id)
                                    )
                    mw.save()
        # окончание забора с yandex
#================================================================================================================
# забираем погоду
def take_weather(city_weather_id):
    # находим город
    weathercountries_obj = WeatherCountries.objects.get(id=city_weather_id)
    # проверим последнюю сессию по городу по яндексу если ей болшье четырех часов обновляем если нет берем ее как есть
    # последняя запись по yndex
    last_w_yandex_id = 0
    w_obj_yandex_slice = MobiWeather.objects.filter(source_name='yandex', city_weather_id=weathercountries_obj).order_by('-taking_date')[:1]
    for wy in w_obj_yandex_slice:
        last_w_yandex_id = wy.id
    if last_w_yandex_id != 0:
        m_w_obj_y = MobiWeather.objects.get(id=last_w_yandex_id)
        last_time_y = m_w_obj_y.taking_date
    else:
        # искутвенно старим дату если по фильтру ничего не вернулось(города нет в базе)
        last_time_y = datetime.datetime.now() - datetime.timedelta(days=1000)
    if last_time_y < datetime.datetime.now() - datetime.timedelta(hours=4):  # заменить  потом на (hours=4)

        # ЗАПИСЫВАЕМ ПОГОДУ В ТАБЛИЦУ(деаем по три попытки получить данные)
        times = 3
        while times != 0:
            try:
                take_from_yandex(city_weather_id)
                times = 0
            except:
                times = times - 1


    # проверим последнюю сессию по городу по openweather если ей болшье четырех часов обновляем если нет берем ее как есть
    # последняя запись
    last_w_openweather_id = 0
    w_obj_openw_slice = MobiWeather.objects.filter(source_name='openweathermap.org', city_weather_id=weathercountries_obj).order_by('-taking_date')[:1]
    for wo in w_obj_openw_slice:
        last_w_openweather_id = wo.id
    if last_w_openweather_id != 0:
        m_w_obj_o = MobiWeather.objects.get(id=last_w_openweather_id)
        last_time_o = m_w_obj_o.taking_date
    else:
        # искутвенно старим дату если по фильтру ничего не вернулось(города нет в базе)
        last_time_o = datetime.datetime.now() - datetime.timedelta(days=1000)

    if last_time_o < datetime.datetime.now() - datetime.timedelta(hours=4):  # заменить  потом на (hours=4)
        # ЗАПИСЫВАЕМ ПОГОДУ В ТАБЛИЦУ(деаем по три попытки получить данные)
        times = 3
        while times != 0:
            try:
                take_from_open_weather(city_weather_id)
                times = 0
            except:
                times = times - 1
#======================================================================================
# для картинок
def set_weather_picture_y(y):
    cloud_type = ''
    if  y.cloud == u'облачно':
        cloud_type = 'cloudy'
    if y.cloud == u'ясно':
        cloud_type = 'clear'
    if y.cloud == u'облачно с прояснениями':
        cloud_type = 'cloudy_clear'
    if y.cloud == u'малооблачно':
        cloud_type = 'little_cloudy'
    if y.cloud == u'облачно с прояснениями, временами снег':
        cloud_type = 'cloudy_clearings_times_snow'
    if (y.cloud == u'облачно с прояснениями, небольшой дождь'):
        cloud_type = 'cloudy_clearings_small_rain'
    if ((y.cloud == u'облачно с прояснениями, небольшой дождь') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_small_rain_night'
    if y.cloud == u'облачно, небольшой дождь':
        cloud_type = 'cloudy_small_rain'
    if ((y.cloud == u'облачно с прояснениями') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_clear_night'
    if ((y.cloud == u'облачно, небольшой дождь') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_small_rain_night'
    if ((y.cloud == u'ясно') and (y.date_date_time == 4)) :
        cloud_type = 'night'
    if  ((y.cloud == u'облачно') and (y.date_date_time == 4)) :
        cloud_type = 'cloudy_night'
    if ((y.cloud == u'малооблачно') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_clear_night'
    if y.cloud == u'переменная облачность':
        cloud_type = 'partly cloudy'
    if y.cloud == u'облачно, временами снег':
        cloud_type = 'cloudy_times_snow'
    if ((y.cloud == u'облачно, временами снег') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_times_snow_night'
    if (y.cloud == u'облачно, дождь'):
        cloud_type = 'cloudy_rain'
    if ((y.cloud == u'облачно, дождь') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_rain_night'
    if y.cloud == u'облачно, дождь со снегом':
        cloud_type = 'cloudy_rain_snow'
    if ((y.cloud == u'облачно, дождь со снегом') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_rain_snow_night'
    if (y.cloud == u'облачно с прояснениями, небольшой снег'):
        cloud_type = 'cloudy_clearings_small_snow'
    if ((y.cloud == u'облачно с прояснениями, небольшой снег') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_clearings_small_snow_night'
    if (y.cloud == u'облачно, небольшой снег'):
        cloud_type = 'cloudy_clearings_small_snow'
    if ((y.cloud == u'облачно, небольшой снег') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_clearings_small_snow_night'
    if (y.cloud == u'переменная облачность, небольшой снег'):
        cloud_type = 'cloudy_clearings_small_snow'
    if ((y.cloud == u'переменная облачность, небольшой снег') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_clearings_small_snow_night'
    if y.cloud == u'облачно, временами дождь со снегом':
        cloud_type = 'cloudy_rain_snow'
    if ((y.cloud == u'облачно, временами дождь со снегом') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_rain_snow_night'
    if (y.cloud == u'переменная облачность, возможен дождь, гроза'):
        cloud_type = 'cloudy_clearing_thunder_storm'
    if ((y.cloud == u'переменная облачность, возможен дождь, гроза') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_clearing_thunder_storm_night'
    if (y.cloud == u'облачно с прояснениями, временами дождь'):
        cloud_type = 'cloudy_rain'
    if ((y.cloud == u'облачно с прояснениями, временами дождь') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_rain_night'
    if (y.cloud == u'облачно, снег'):
        cloud_type = 'cloudy_times_snow'
    if ((y.cloud == u'облачно, снег') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_times_snow_night'
    if (y.cloud == u'облачно, дождь, гроза'):
        cloud_type = 'cloudy_clearing_thunder_storm'
    if ((y.cloud == u'облачно, дождь, гроза') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_clearing_thunder_storm_night'
    if (y.cloud == u'переменная облачность, временами дождь'):
        cloud_type = 'cloudy_rain'
    if ((y.cloud == u'переменная облачность, временами дождь') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_rain_night'
    if (y.cloud == u'облачно с прояснениями, временами дождь со снегом'):
        cloud_type = 'cloudy_rain_snow'
    if ((y.cloud == u'облачно с прояснениями, временами дождь со снегом') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_rain_snow_night'
    if (y.cloud == u'облачно, временами дождь'):
        cloud_type = 'cloudy_small_rain'
    if ((y.cloud == u'облачно, временами дождь') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_rain_night'
    if y.cloud == u'малооблачно, без существенных осадков':
        cloud_type = 'little_cloudy'
    if ((y.cloud == u'малооблачно, без существенных осадков') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_clear_night'
    if y.cloud == u'облачно с прояснениями, дождь, гроза':
        cloud_type = 'cloudy_clearing_thunder_storm'
    if ((y.cloud == u'облачно с прояснениями, дождь, гроза') and (y.date_date_time == 4)):
        cloud_type = 'cloudy_clearing_thunder_storm_night'
    if cloud_type == '':  # дополнить все варианты
        cloud_type = 'cloudy_clear'
    return cloud_type
#=======================================================================================
# словарь для openweather.org определения облачности
weather_pic_openweather = {'few clouds':{1:'little_cloudy', 4:'cloudy_clear_night'},
                           'sky is clear':{1:'clear', 4:'cloudy_clear_night'},
                           'broken clouds':{1:'cloudy_clear', 4:'cloudy_clear_night'},
                           'overcast clouds':{1:'cloudy', 4:'cloudy_night'},
                           'overcast clouds moderate rain':{1:'cloudy_rain', 4:'cloudy_rain_night'},
                           'scattered clouds':{1:'little_cloudy', 4:'cloudy_clear_night'},
                           'sky is clear light rain':{1:'cloudy_small_rain', 4:'cloudy_rain_night'},
                           'scattered clouds moderate rain':{1:'cloudy_rain', 4:'cloudy_rain_night'},
                           'overcast clouds light rain':{1:'cloudy_small_rain', 4:'cloudy_small_rain_night'},
                           'scattered clouds light rain':{1:'cloudy_clearings_small_rain', 4:'cloudy_small_rain_night'},
                           'broken clouds moderate rain':{1:'cloudy_small_rain', 4:'cloudy_small_rain_night'},
                                }
weather_cloud_openweather = {'few clouds':'малооблачно', 'sky is clear':'облачно', 'broken clouds':'переменная облачность',
                             'overcast clouds': 'облачно', 'overcast clouds moderate rain':'облачно, дождь',
                             'scattered clouds': 'малооблачно',
                             'sky is clear light rain':'облачно с прояснениями, небольшой дождь',
                             'scattered clouds moderate rain': 'малооблачно, временами дождь',
                             'overcast clouds light rain':'облачно, небольшой дождь',
                             'scattered clouds light rain':'малооблачно, небольшой дождь',
                             'broken clouds moderate rain':'облачно, небольшой дождь',
                             }
#=======================================================================================
# определим направление ветра
weather_dir_openweather = {'W':'западный', 'WNW':'западный', 'NW': 'северо-западный', 'NNW': 'северо-западный',
                           'N': 'северный', 'NNE': 'северный',
                           'NE':'северо-восточный', 'ENE':'северо-восточный', 'E':'восточный',
                           'ESE':'восточный', 'SE': 'юго-восточный', 'SSE':'юго-восточный',
                           'S': 'южный', 'SSW': 'южный', 'SW':'юго-западный', 'WSW':'западный'}
#======================================================================================
def set_weather_time_of_day(h):
    if h.date_date_time == 1:
        d_type = 'утро'
    if h.date_date_time == 2:
        d_type = 'день'
    if h.date_date_time == 3:
        d_type = 'вечер'
    if h.date_date_time == 4:
        d_type = 'ночь'
    return d_type
#=======================================================================================
def set_weather_wind_dir_y(y):
    if y.wind_dir == 's':
        wind_dir_name = 'южный'
    if y.wind_dir == 'sw':
        wind_dir_name = 'юго-западный'
    if y.wind_dir == 'n':
        wind_dir_name = 'северный'
    if y.wind_dir == 'ne':
        wind_dir_name = 'северо-восточный'
    if y.wind_dir == 'e':
        wind_dir_name = 'восточный'
    if y.wind_dir == 'w':
        wind_dir_name = 'западный'
    if y.wind_dir == 'nw':
        wind_dir_name = 'северо-западный'
    if y.wind_dir == 'se':
        wind_dir_name = 'юго-восточный'
    return wind_dir_name
#======================================================================================
def get_weather_time_pattern(current_date):
    current_time = current_date.strftime("%H")
    if 4 < int(current_time) < 12:
        time_pattern = 1
    if 0 <= int(current_time) <= 4:
        time_pattern = 4
    if 12 <= int(current_time) < 17:
        time_pattern = 2
    if 17 <= int(current_time) <= 24:
        time_pattern = 3
    return time_pattern
#======================================================================================
def temperature(h):
    temp_from = h.temp_from
    if temp_from > 0:
        temp_from_string = '+' + str(int(temp_from))
    else:
        temp_from_string = str(int(temp_from))
    temp_to = h.temp_to
    if temp_to > 0:
        temp_to_string = '+' + str(int(temp_to))
    else:
        temp_to_string = str(int(temp_to))
    return temp_from_string, temp_to_string
#======================================================================================
def temperature_average(y, o):
    temp_from = int(round((o.temp_from + y.temp_from) / 2))
    if temp_from > 0:
        temp_from_string = '+' + str(temp_from)
    else:
        temp_from_string = str(temp_from)
    temp_to = int(round((o.temp_to + y.temp_to) / 2))
    if temp_to > 0:
        temp_to_string = '+' + str(temp_to)
    else:
        temp_to_string = str(temp_to)
    wind_speed = int(round((o.wind_speed + y.wind_speed) / 2))
    pressure = int(round((o.pressure + y.pressure) / 2))
    humidity = int(round((o.humidity + y.humidity) / 2))
    return temp_from_string, temp_to_string, wind_speed, pressure, humidity

#======================================================================================
def get_weather_context(city_weather_id):
    # находим город
    weathercountries_obj = WeatherCountries.objects.get(id=city_weather_id)
    weather_list = []
    check_time_pattern_passed = False
    weather_dict = {}
    iter_w = 1
    q_y = True  #  записи по yandex
    q_o = True  #  записи по openweather.org

    # последняя запись по yndex
    last_w_yandex_id = 0
    w_obj_yandex_slice = MobiWeather.objects.filter(source_name='yandex', city_weather_id=weathercountries_obj).order_by('-taking_date')[:1]
    for wy in w_obj_yandex_slice:
        last_w_yandex_id = wy.id
    # если по данному городу нету записей в базе
    if last_w_yandex_id == 0:
        q_y = False
    else:
        w_obj_yandex_last = MobiWeather.objects.get(id=last_w_yandex_id)
        # если послдняя бралась больше дня назад false
        if w_obj_yandex_last.taking_date < datetime.datetime.now() - datetime.timedelta(days=1):
            q_y = False
        # получаем quaryset за последнюю сессию по yandex
        w_quaryset_yandex = MobiWeather.objects.filter(source_name='yandex', city_weather_id=weathercountries_obj, \
                             taking_date__contains=w_obj_yandex_last.taking_date.strftime("%Y-%m-%d %H:%M")).order_by('date', 'date_date_time').distinct('date', 'date_date_time')


    # последняя запись по openweathermap.org
    last_w_openweathermap_id = 0
    w_obj_openweathermap_slice = MobiWeather.objects.filter(source_name='openweathermap.org', city_weather_id=weathercountries_obj).order_by('-taking_date')[:1]
    for wo in w_obj_openweathermap_slice:
        last_w_openweathermap_id = wo.id
    # если по данному городу нету записей в базе
    if  last_w_openweathermap_id == 0:
        q_o = False
    else:
        w_obj_openweathermap_last = MobiWeather.objects.get(id=last_w_openweathermap_id)
        # если послдняя бралась больше дня назад false
        if w_obj_openweathermap_last.taking_date < datetime.datetime.now() - datetime.timedelta(days=1):
            q_o = False
        # получаем quaryset за последнюю сессию по openweathermap.org
        w_quaryset_openweathermap = MobiWeather.objects.filter(source_name='openweathermap.org', city_weather_id=weathercountries_obj, \
                             taking_date__contains=w_obj_openweathermap_last.taking_date.strftime("%Y-%m-%d %H:%M")).order_by('date', 'date_date_time').distinct('date', 'date_date_time')

    # разобъем сутки на части, чтобы была возможность сравнить date_date_time на соответствие текущему времени дня (утро, день, вечер, ночь)
    current_date = datetime.datetime.now()
    time_pattern = get_weather_time_pattern(current_date)


    # СЛУЧАЙ 1 - есть две последние в обоих источниках и им не больше суток
    if q_o and q_y :
        # перебираем quaryset openweathermap.org (он меньше при совпадении даты и типа суток c yndex считаем среднее и записываем в словарь)
        # даннные которые не усредняются берем из yandex
        for o in w_quaryset_openweathermap:
            for y in w_quaryset_yandex:
                if ((o.date == y.date) and (o.date_date_time == y.date_date_time)):
                    # берем среднее (остальное yandex)
                    temp_from_string, temp_to_string, wind_speed, pressure, humidity = temperature_average(y, o)
                    # берем с yandex
                    # определим облачность
                    cloud_type = set_weather_picture_y(y)
                    # время дня
                    d_type = set_weather_time_of_day(y)
                    # направление ветра
                    wind_dir_name = set_weather_wind_dir_y(y)


                    weather_list = [y.date, d_type, y.cloud, temp_from_string, temp_to_string,
                                     wind_speed, wind_dir_name,
                                     pressure, humidity, cloud_type]
                    # если совпали id части суток и датой (без времени) то записываем данные в словарь нет - не записываем. проверяем только пока не совпадет с эталоном
                    if check_time_pattern_passed:
                        weather_dict[iter_w] = weather_list
                        iter_w = iter_w + 1
                    if not check_time_pattern_passed:
                        if time_pattern == y.date_date_time and current_date.strftime("%d.%m.%Y") == y.date.strftime("%d.%m.%Y"):
                            weather_dict[iter_w] = weather_list
                            iter_w = iter_w + 1
                            check_time_pattern_passed = True  # больше проверку не выполнеям


    # СЛУЧАЙ 2 если есть актуальные записи только yandex
    if q_y and not q_o:
        # перебираем quaryset yandex берем все с yndex
        for y in w_quaryset_yandex:
            # температура
            temp_from_string, temp_to_string = temperature(y)
            cloud_type = set_weather_picture_y(y)
            # время дня
            d_type = set_weather_time_of_day(y)
            # направление ветра
            wind_dir_name = set_weather_wind_dir_y(y)

            weather_list = [y.date, d_type, y.cloud, temp_from_string, temp_to_string,
                             y.wind_speed, wind_dir_name,
                             int(y.pressure), int(y.humidity), cloud_type]
            # если совпали id части суток и датой (без времени) то записываем данные в словарь нет - не записываем. проверяем только пока не совпадет с эталоном
            if check_time_pattern_passed:
                weather_dict[iter_w] = weather_list
                iter_w = iter_w + 1
            if not check_time_pattern_passed:
                if time_pattern == y.date_date_time and current_date.strftime("%d.%m.%Y") == y.date.strftime("%d.%m.%Y"):
                    weather_dict[iter_w] = weather_list
                    iter_w = iter_w + 1
                    check_time_pattern_passed = True  # больше проверку не выполнеям

    # случай 3: есть актуальные записи только по openweather
    if q_o and not q_y:
        # перебираем quaryset
        for o in w_quaryset_openweathermap:
            # температура
            temp_from_string, temp_to_string = temperature(o)
            # определим класс для облочности(картинка)
            cloud_type = ''
            cloud_type_t = weather_pic_openweather[o.cloud]
            if (o.date_date_time == 4):
                cloud_type = cloud_type_t[4]
            else:
                cloud_type = cloud_type_t[1]
            if cloud_type == '':  # дополнить все варианты
                cloud_type = 'cloudy_clear'
            # определим время дня
            d_type = set_weather_time_of_day(o)
            # определим направление ветра
            wind_dir_name = weather_dir_openweather[o.wind_dir]
            # облачность
            cloud_name = weather_cloud_openweather[o.cloud]

            weather_list = [o.date, d_type, cloud_name, temp_from_string, temp_to_string,
                             int(o.wind_speed), wind_dir_name,
                             int(o.pressure), int(o.humidity), cloud_type]
            # если совпали id части суток и датой (без времени) то записываем данные в словарь нет - не записываем. проверяем только пока не совпадет с эталоном
            if check_time_pattern_passed:
                weather_dict[iter_w] = weather_list
                iter_w = iter_w + 1
            if not check_time_pattern_passed:
                if time_pattern == o.date_date_time and current_date.strftime("%d.%m.%Y") == o.date.strftime("%d.%m.%Y"):
                    weather_dict[iter_w] = weather_list
                    iter_w = iter_w + 1
                    check_time_pattern_passed = True  # больше проверку не выполнеям

    # функция возвращает только словарь
    if weather_dict == {}:
        return False
    return weather_dict

#=======================================================================================
# функция для забора текущей погоды на главную страницу
def get_weather_context_main_page(city_weather_id):
    # текущий город
    weathercountries_obj = WeatherCountries.objects.get(id=city_weather_id)
    q_y = True  #  записи по yandex
    q_o = True  #  записи по openweather.org
    weather_list = []
    # определим текущее время суток(1-4)
    current_date = datetime.datetime.now()  # Текущая дата со временем
    time_pattern = get_weather_time_pattern(current_date)

    # находим в базе запись у которой совпадает дата и врмемя суток с текущей и берем последнне значение (max)
    # yandex

    w_obj_yandex = MobiWeather.objects.filter(source_name='yandex', city_weather_id=weathercountries_obj, \
                                              date_date_time=time_pattern, date=datetime.date.today()).all().aggregate(Max('id'))

    if w_obj_yandex['id__max'] == None:  # если нету такой записи
        q_y = False
    else:
        w_obj_yandex_last = MobiWeather.objects.get(id=w_obj_yandex['id__max'])
        # если ей не больше 1 дня
        if w_obj_yandex_last.taking_date < datetime.datetime.now() - datetime.timedelta(days=1):
            q_y = False

    # openweatherorg
    w_obj_openweather = MobiWeather.objects.filter(source_name='openweathermap.org', city_weather_id=weathercountries_obj, \
                                              date_date_time=time_pattern, date=datetime.date.today()).all().aggregate(Max('id'))
    if w_obj_openweather['id__max'] == None:  # если нету такой записи
        q_o = False
    else:
        w_obj_openweather_last = MobiWeather.objects.get(id=w_obj_openweather['id__max'])
        # если ей не больше 1 дня
        if w_obj_openweather_last.taking_date < current_date - datetime.timedelta(days=1):
            q_o = False

    if q_o and q_y:  # есть актуальные записи по обоим источникам
        o = w_obj_openweather_last
        y = w_obj_yandex_last
        # берем среднее (остальное yandex)
        # определяем температуру
        temp_from_string, temp_to_string, wind_speed, pressure, humidity = temperature_average(y, o)
        # определим облачность
        cloud_type = set_weather_picture_y(y)
        # время дня
        d_type = set_weather_time_of_day(y)
        # направление ветра
        wind_dir_name = set_weather_wind_dir_y(y)
        weather_list = [y.date, d_type, y.cloud, temp_from_string, temp_to_string,
                                     wind_speed, wind_dir_name,
                                     pressure, humidity, cloud_type]


    if q_y and not q_o:  # ест актуальные записи только по yandex
        y = w_obj_yandex_last
        # температура
        temp_from_string, temp_to_string = temperature(y)
        # облачность(карт)
        cloud_type = set_weather_picture_y(y)
        # время дня
        d_type = set_weather_time_of_day(y)
        # направление ветра
        wind_dir_name = set_weather_wind_dir_y(y)
        weather_list = [y.date, d_type, y.cloud, temp_from_string, temp_to_string,
                         y.wind_speed, wind_dir_name,
                         int(y.pressure), int(y.humidity), cloud_type]

    if q_o and not q_y:
        o = w_obj_openweather_last
        # температура
        temp_from_string, temp_to_string = temperature(o)
        # определим класс для облочности(картинка)
        cloud_type = ''
        cloud_type_t = weather_pic_openweather[o.cloud]
        if (o.date_date_time == 4):
            cloud_type = cloud_type_t[4]
        else:
            cloud_type = cloud_type_t[1]
        if cloud_type == '':  # дополнить все варианты
            cloud_type = 'cloudy_clear'
        # определим время дня
        d_type = set_weather_time_of_day(o)
        # определим направление ветра
        wind_dir_name = weather_dir_openweather[o.wind_dir]
        # облачность
        cloud_name = weather_cloud_openweather[o.cloud]

        weather_list = [o.date, d_type, cloud_name, temp_from_string, temp_to_string,
                         int(o.wind_speed), wind_dir_name,
                         int(o.pressure), o.humidity, cloud_type]
    return weather_list

#=======================================================================================
# для html погода
@render_to("weather.html")
def weather (request):
    try:
        city_weather_id = int(request.POST['city_id'])
    except:
        city_weather_id = 35
    # находим город
    weathercountries_obj = WeatherCountries.objects.get(id=city_weather_id)
    # записываем погоду в базу (если по данному городу прошло больше n-го количества времени, иначе записей не делаем)
    take_weather(city_weather_id)
    context = {}
    context['placement'] = 14
    # ПЕРЕДАЕМ НА HTML ПОГОДУ ИЗ БАЗЫ
    weather_dict = get_weather_context(city_weather_id)
    if weather_dict == False:
        context['no_weather'] = True
    else:
        context['weather_dict'] = weather_dict
    context['weather_page'] = True
    context['current_city_obj'] = weathercountries_obj
    context['all_cities_obj'] = WeatherCountries.objects.all()
    context['weather'] = True
    context.update(hotspot_identity(request))
    return context

#=============================================================================================
# отображаем список регионов (ссылки на регионы)
@render_to("weather_change.html")
def weather_change(request):
    # Weather_Countries
    context = {}
    context['placement'] = 14
    weather_regions = ['Российская Федерация', 'США', 'Европа', 'Азия', 'Африка', 'Австралия&Океания', 'Америка']
    context['weather_regions'] = weather_regions
    context['weather_page'] = True
    context.update(hotspot_identity(request))
    return context
#=============================================================================================

# отображаем список городов (ссылки на погоду по городу)
@render_to("weather_cities.html")
def weather_region(request, region_id):
    context = {}
    context['placement'] = 14
    weather_countries_obj = WeatherCountries.objects.filter(region_id=int(region_id)).order_by('city_rus_name')
    context['weather_countries_obj'] = weather_countries_obj
    context['weather_page'] = True
    context.update(hotspot_identity(request))
    return context


#===========================================================================================================
# для организаций
@render_to("orgs.html")
def orgs(request, org):
    context = {}
    # if not request.GET.has_key('org_type'):
    #    raise Http404
    # вернем из выбранного пункта меню тип оранизации
    # org_type = request.GET['org_type']
    # context['org_type'] = int(org_type)
    org_type = {'banks':2, 'pharmacies':300, 'hospitals':301, 'antenatalclinics':302, 'clinics':303,
                'medicalceters':304, 'policlinic':305, 'maternities':306, 'ambulance':307, 'stomatology':308,
                'traumacenters':309, 'hairdressing': 400, 'beautysalons':401, 'tanning':402, 'spa-salons':403,
                'emergencyservices':500, 'tailoringclothes':501, 'utilityservice':502, 'pawnshops':503,
                'notaryservices':504, 'printingservices':505, 'laundry':506, 'taxi':507, 'photoservices':508,
                'dry-cleaning':509, 'lawyers':510, 'bathroomsandsauns':600, 'pools':601, 'sportscomplexes':602,
                'stadiums':603, 'clubs':604, 'hypermarkets':700, 'babyshops':701, 'bookstores':702, 'computerstores':703,
                'furniturestores':704, 'clothesandshoes':705, 'shopsproducts':706, 'shopstissue':707, 'householdgoodsstores':708,
                'electronicsstores':709, 'musicstores':710, 'perfumestores':711, 'huntingandfishing_stores':712, 'markets':713,
                'sportshops':714, 'supermarkets':715, 'shoppingmalls':716, 'jewelrystores':717, 'restaurantscafesbars':800,
                'movietheaters':801, 'pfs':900, 'employmentcenters':1000}
    try:
        context['org_type'] = org_type[org]
        context[org] = org
        if context['org_type'] == 2:
            context['placement'] = 2
        elif 300 <= context['org_type'] <= 309 :
            context['placement'] = 3
        elif 400 <= context['org_type'] <= 403 :
            context['placement'] = 4
        elif 500 <= context['org_type'] <= 510 :
            context['placement'] = 5
        elif 600 <= context['org_type'] <= 604 :
            context['placement'] = 6
        elif 700 <= context['org_type'] <= 717 :
            context['placement'] = 7
        elif 800 <= context['org_type'] <= 801 :
            context['placement'] = 8
        elif context['org_type'] == 900 :
            context['placement'] = 9
        elif context['org_type'] == 1000 :
            context['placement'] = 10
    except:
        raise  Http404
    context['org_page'] = True
    if request.COOKIES.has_key('organization'):
        try:
            installed_location = Mikrotik.objects.get(name_of_mikrotik=request.COOKIES['organization'])
            context['cur_microtik_coordinates'] = str(installed_location.get_address().x) + ':' + str(installed_location.get_address().y) + ':' + str(installed_location.get_address())
        except Mikrotik.DoesNotExist:
            pass
    context.update(hotspot_identity(request))
    return context
#======================================================================================================#
# функция формирования строки (списка организаций) для правого блока и карты на основании quareyset
def make_org_list(org_objs, org_type):

    j = 1  # для счетчика номера на карте

    str_ex = ''
    working_time = u'время работы: '
    tel = u'тел: '
    edit = u'редактировать'

    try:
        for org_obj in org_objs:
            if (org_obj.equal_coord_range == None) :
                # если совпадений нет
                # проверим наличие отсутствие url и working hours
                str_url = ' '
                str_hours = ' '
                str_name = '<a href = "#" onClick=OpenBalloon(' + str(j) + '); return false;><font class="org_name">' + org_obj.org_name + '</font></a>'
                if org_obj.url != 'nourl':
                    str_url = '<a href ="' + org_obj.url + '">' + org_obj.url + '</a>'
                if org_obj.hours != 'nohours':
                    str_hours = '<li>' + working_time + org_obj.hours + '</li>'

                str_info = '<div class = "last_params"><li>' + tel + org_obj.phone + ' ' + str_url + str_hours + '</li></div>'
                str_ex = str_ex + str(org_obj.x) + '|' + str(org_obj.y) + '|' + str_name \
                + '<li >' + org_obj.address + '</li>'\
                + str_info + '|' + '<div id = "but"><a href = "#edit_all" class = "edit_button" onClick=fun_edit_click(' + str(org_obj.id) + '); return false;>' + edit + '</a></div>' + '?'

            if (org_obj.equal_coord_range != None):
                org_coincidence_objs = MobiOrganizationsUnique.objects.filter(x=org_obj.x, y=org_obj.y, org_type=int(org_type))
                i = 1
                str_ex_temp = ''
                for org_coincidence_obj in org_coincidence_objs:
                    str_hours = ' '
                    str_url = ' '
                    str_name = '<a  href = "#" onClick=OpenBalloon(' + str(j) + '); return false;><font class = "org_name">' + org_coincidence_obj.org_name + '</font></a>'
                    if org_coincidence_obj.url != 'nourl':
                        str_url = '<a href ="' + org_coincidence_obj.url + '">' + org_coincidence_obj.url + '</a>'
                    if org_coincidence_obj.hours != 'nohours':
                        str_hours = '<li>' + working_time + org_coincidence_obj.hours + '</li>'

                    str_info = '<div class = "last_params"><li>' + tel + org_coincidence_obj.phone + ' '\
                    + str_url + str_hours + '</li></div>'

                    str_ex_temp = str_ex_temp + '<div class = "number_coincidence">' + str(i) + ')' + " " + str_name + '</div>' + '<div class ="coincidence_params"><li>'\
                    + org_coincidence_obj.address + '</li>' + str_info + '</div>'\
                    + '<div id = "but' + str(i) + '"><a href = "#edit_all" class = "edit_button" onclick = "fun_edit_click(' + str(org_coincidence_obj.id) + ',' + str(i) + ')">' + edit + '</a></div>'
                    i = i + 1
                str_ex = str_ex + str(org_coincidence_obj.x) + '|' + str(org_coincidence_obj.y) + '|' + str_ex_temp + '?'
                    # запомнить бы координатки.... (или distinct без сортировки...)
            j = j + 1  # нарасчиваем счетчик для номера на карте по ссылке
    except Exception, e:
        print e

    return str_ex
#======================================================================================================#
# 10 объектов обновляемые на сдвиг карты
@render_to('orgs.html')
def ajax_orgs_points(request):
    # границы
    if not request.GET.has_key('mapObjBounds'):
        raise Http404
    edge_points = request.GET.get('mapObjBounds')
    edge_points_array = edge_points.split(',')

    # вернем из выбранного пункта меню тип оранизации
    org_type = request.GET['org_type']

    org_objs = MobiOrganizationsUnique.objects.filter(org_type=int(org_type), x__lt=edge_points_array[3], x__gt=edge_points_array[1], \
                y__lt=edge_points_array[2], y__gt=edge_points_array[0], deleted=False).order_by('x', 'y').distinct('x', 'y')[0:10]
    str_ex = make_org_list(org_objs, org_type)



    return HttpResponse(str_ex)

#======================================================================================================#
# результаты поиска (по строке поиска)
@render_to('orgs.html')
def ajax_orgs_points_search(request):
    str_ex = ''
    if not request.GET.has_key('start'):
        raise Http404
    # получим первыую букву(буквы) названия организации
    start = request.GET.get('start')
    # получим текущее значение среза
    current = request.GET.get('current')
    # получим порядковый номер показанного списка
    turn = request.GET.get('turn')
    # вернем из выбранного пункта меню тип оранизации
    org_type = request.GET['org_type']


    # выполним запрос и посчитаем кол-во записей
    org_objs = MobiOrganizationsUnique.objects.filter(org_type=int(org_type), org_name__istartswith=start).distinct('org_name').order_by('org_name')
    count_org_objs = org_objs.count()


    # сформируем нужный срез  и вернем в javascript
    current_start, current_end = current.split(':')
    k = int(current_end) + 1  # нумерация пунктов (списка имен)
    no_next = False


    executing_start = int(current_end)
    executing_end = int(current_end) + 12
    if (executing_end >= count_org_objs):  # если выходим за пределы вправо -1 переход
        no_next = True

    if (turn == '1'):  # first time (ни разу не нажималась кнопка перемещения)
        executing_start = 0
        executing_end = 12
        k = 1
        if (count_org_objs < 13):
            no_next = True


    # нарасчиваем счетчик разов
    turn = int(turn) + 1
    org_objs_part_of = org_objs[executing_start:executing_end]
    for org_obj in org_objs_part_of:
        org_obj.org_name
        str_name = org_obj.org_name.replace(' ', '_')
        str_ex = str_ex + '<br><font id = "for_cicle">' + str(k) + '</font> <a  href = "#" onClick=view_by_name("' + str_name + '"); return false;><ul class = "org_param_right"> ' + org_obj.org_name + '</ul></a>'
        k = k + 1
    str_next = ''


    if (no_next == False):
        str_next = str_next + '<div  id="next_button" style =" margin-left:120px; position:absolute; margin-top: 10px; ">' \
        + '<a href = "#" onClick=nextfun("'\
        + str(executing_start) + ':' + str(executing_end) + '"); return false;>' + u'след. 12' + '</a></div>'

    str_ex = str_ex + '<div id="ins' + str(turn) + '"></div>' + '^' + str_next
    return HttpResponse(str_ex)


@render_to('article_mobi.html')
def article_mobi_slug(request, slug):
    context = {}
    context['article_mobi_slug_page'] = True
    obj = get_object_or_404(Article, slug=slug, is_published=True)
    context['obj'] = obj
    context.update(hotspot_identity(request))
    return context


#==========================================================================================================================
# вернем список по 1 организации
@render_to('orgs.html')
def ajax_orgs_points_search_by_name(request):
    working_time = u'время работы: '
    tel = u'тел: '
    edit = u'редактировать'
    if not request.GET.has_key('org_name'):
        raise Http404
    # получаем название организации
    org_name_underline = request.GET.get('org_name')
    org_name = org_name_underline.replace('_', ' ')
    # вернем из выбранного пункта меню тип оранизации
    org_type = request.GET['org_type']
    str_ex = ''

    # получим порядковый номер показанного списка
    turn = request.GET.get('turn_single_name')

    # получим текущее значение среза
    current = request.GET.get('current_single_name')

    # выполним запрос и посчитаем кол-во записей
    org_objs = MobiOrganizationsUnique.objects.filter(org_type=int(org_type), org_name__istartswith=org_name)
    count_org_objs = org_objs.count()


    # сформируем нужный срез  и вернем в javascript
    current_start, current_end = current.split(':')
    k = int(current_end) + 1  # нумерация пунктов (списка имен)
    no_next = False


    executing_start = int(current_end)
    executing_end = int(current_end) + 10
    if (executing_end > count_org_objs):  # если выходим за пределы вправо -1 переход
        no_next = True

    if (turn == '1'):  # first time (ни разу не нажималась кнопка перемещения)
        executing_start = 0
        executing_end = 10
        k = 1
        if (count_org_objs < 11):
            no_next = True

    turn = int(turn) + 1
    org_objs_part_of = org_objs[executing_start : executing_end]

    # проверка необходимости кнопок
    str_next = ''
    str_prev = ''
    if (no_next == False):
        str_next = str_next + '<div id = "next_button" style =" margin-left:120px; position:absolute; ">' \
        + '<a href = "#" onClick=nextfun_single_name("'\
        + str(executing_start) + ':' + str(executing_end) + '"); return false;>' + u'след. 10' + '</a></div>'
    # окончание проверки необходимости кнопок


    for org_obj in org_objs_part_of:
        str_url = ' '
        str_hours = ' '
        str_name = '<a id = "link" href = "#" onClick=OpenBalloon(' + str(k) + '); return false;><font class="org_name">' + org_obj.org_name + '</font></a>'
        if org_obj.url != 'nourl':
            str_url = '<a href ="' + org_obj.url + '">' + org_obj.url + '</a>'
        if org_obj.hours != 'nohours':
            str_hours = '<li>' + working_time + org_obj.hours + '</li>'
        str_info = '<li>' + tel + org_obj.phone + ' ' + str_url + str_hours + '</li>' + '</font>'
        str_ex = str_ex + str(org_obj.x) + '|' + str(org_obj.y) + '|'\
        + str_name \
        + '<div class = "last_params"><li>' + org_obj.address + '</li>' + str_info + '</div>|'\
        + '<div id = "but"><a href = "#edit_all" class = "edit_button" onclick = "fun_edit_click(' + str(org_obj.id) + ')">' + edit + '</a></div>' + '?'
        k = k + 1
    str_ex = str_ex + '^' + '<div id="ins' + str(turn) + '"></div>' + str_next + str_prev
    return HttpResponse(str_ex)
#====================================================================================================
# регестрация почтового ящика
@render_to('mail_reg.html')
def mail_reg(request):
    context = {}
    context['mail_page'] = True
    context.update(hotspot_identity(request))
    return context
#========================================================================================================
@render_to('mail.html')
def mail(request):
    context = {}
    login = ''
    pasword = ''
    login = request.POST.get('u_login')
    password = request.POST.get('u_password')
    if (login != '' and password != ''):
        context['log'] = login
        context['pas'] = password
        context['submit'] = True
    context['mail_page'] = True
    context.update(hotspot_identity(request))
    return context
#==============================================================================================================
@render_to('mail_reg.html')
def ajax_mail_reg(request):
    str_ex = ''
    str_ex_er = ''
    login = ''
    password = ''
    login = request.POST.get('login')
    password = request.POST.get('password')
    if login == None:
        login = ''
    if password == None:
        password = ''
    token = "ec0a770134ae7ea00b10cd43178c235171cfb39913833eb29abf9e42"
    ADRESS = 'https://pddimp.yandex.ru/reg_user_token.xml?token=' + token + '&u_login=' + login + '&u_password=' + password
    file = urllib2.urlopen(ADRESS)
    data = file.read()
    file.close()
    doc = parseString(data)
    root = doc.documentElement


    for q in root.childNodes:
        if q.nodeName == 'error':
            str_ex_er = q.getAttribute('reason')
        if q.nodeName == 'ok':
            str_ex_er = 'ok'
    er_dict = {'badlogin': u'Логин некорректен',
               'passwd-tooshort': u'Пароль короток',
               'passwd-toolong': u'Пароль слишком длинный',
               'occupied': u'Логин уже занят',
               'passwd-likelogin': u'Пароль и логин совпадают',
               'login-empty': u'Введите логин',
               'passwd-empty': u'Введите пароль',
               'ok': u'Регистрация завершена успешно'}
    str_ex = er_dict[str_ex_er]

    return HttpResponse(str_ex)
#===============================================================================================================
def ajax_mail_check_user(request):
    login = ''
    token = "ec0a770134ae7ea00b10cd43178c235171cfb39913833eb29abf9e42"
    str_ex = ''
    login = request.POST.get('login')
    if (login == '') or (login == None):
        str_ex = '<div style="color:red;">Логин не может быть пустым</div>'
        return HttpResponse(str_ex)
    ADRESS = 'https://pddimp.yandex.ru/check_user.xml?token=' + token + '&login=' + login
    file = urllib2.urlopen(ADRESS)
    data = file.read()
    file.close()
    doc = parseString(data)
    result = doc.getElementsByTagName('result')[0].childNodes[0]
    if result.nodeValue == 'exists':
        str_ex = '<div id = "lstatus" style="color:red;">Логин занят</div>'
    else:
        str_ex = '<div id = "lstatus" style="color:green;">Логин свободен</div>'
    return HttpResponse(str_ex)
#====================================================================================================
# регестрация почтового ящика
@render_to('mail_reg.html')
def mail_reg(request):
    context = {}
    context['placement'] = 12
    context['mail_page'] = True
    context.update(hotspot_identity(request))
    return context
#========================================================================================================
@render_to('mail.html')
def mail(request):
    context = {}
    context['placement'] = 12
    login = ''
    pasword = ''
    login = request.POST.get('u_login')
    password = request.POST.get('u_password')
    if (login != '' and password != ''):
        context['log'] = login
        context['pas'] = password
        context['submit'] = True
    context['mail_page'] = True
    context.update(hotspot_identity(request))
    return context
#==============================================================================================================
@render_to('mail_reg.html')
def ajax_mail_reg(request):
    str_ex = ''
    str_ex_er = ''
    login = ''
    password = ''
    login = request.POST.get('login')
    password = request.POST.get('password')
    if login == None:
        login = ''
    if password == None:
        password = ''
    token = "ec0a770134ae7ea00b10cd43178c235171cfb39913833eb29abf9e42"
    ADRESS = 'https://pddimp.yandex.ru/reg_user_token.xml?token=' + token + '&u_login=' + login + '&u_password=' + password
    file = urllib2.urlopen(ADRESS)
    data = file.read()
    file.close()
    doc = parseString(data)
    root = doc.documentElement


    for q in root.childNodes:
        if q.nodeName == 'error':
            str_ex_er = q.getAttribute('reason')
        if q.nodeName == 'ok':
            str_ex_er = 'ok'
    er_dict = {'badlogin': u'Логин некорректен',
               'passwd-tooshort': u'Пароль короток',
               'passwd-toolong': u'Пароль слишком длинный',
               'occupied': u'Логин уже занят',
               'passwd-likelogin': u'Пароль и логин совпадают',
               'login-empty': u'Введите логин',
               'passwd-empty': u'Введите пароль',
               'ok': u'Регистрация завершена успешно'}
    str_ex = er_dict[str_ex_er]

    return HttpResponse(str_ex)
#===============================================================================================================
def ajax_mail_check_user(request):
    login = ''
    token = "ec0a770134ae7ea00b10cd43178c235171cfb39913833eb29abf9e42"
    str_ex = ''
    login = request.POST.get('login')
    if (login == '') or (login == None):
        str_ex = '<div style="color:red;">Логин не может быть пустым</div>'
        return HttpResponse(str_ex)
    ADRESS = 'https://pddimp.yandex.ru/check_user.xml?token=' + token + '&login=' + login
    file = urllib2.urlopen(ADRESS)
    data = file.read()
    file.close()
    doc = parseString(data)
    result = doc.getElementsByTagName('result')[0].childNodes[0]
    if result.nodeValue == 'exists':
        str_ex = '<div id = "lstatus" style="color:red;">Логин занят</div>'
    else:
        str_ex = '<div id = "lstatus" style="color:green;">Логин свободен</div>'
    return HttpResponse(str_ex)


from findocs.models import FinDoc, FinDocTemplate
@render_to('findoc_mobi.html')
def findoc_mobi_slug(request, slug):
    context = {}
    context['article_mobi_slug_page'] = True
    obj = get_object_or_404(FinDoc, slug=slug)
    context['obj'] = obj
    context.update(hotspot_identity(request))
    return context


@render_to('content/article/object.html')
def findoc_globalhome_slug(request, slug):
    context = {}
    obj = get_object_or_404(FinDoc, slug=slug).template
    context['obj'] = obj
    return context



#===============================================================================================================
# вернем данные об организации
def ajax_get_org(request, org_id):
    org_obj = MobiOrganizationsUnique.objects.get(id=org_id)
    str = org_obj.org_name + '~' + org_obj.address + '~' + org_obj.phone + '~' + org_obj.url + '~' + org_obj.hours
    return HttpResponse(str)

#===============================================================================================================
# получаем данные с формы редактирования организации и записываем в модель MobiOrganizationsUserChanges
def ajax_user_chage_org_one(request):
    if not request.POST.has_key('org_id'):
        raise Http404

    org_id = request.POST.get('org_id')
    name = request.POST.get('u_name')
    email = request.POST.get('u_email')

    org_name = request.POST.get('org_name'),
    address = request.POST.get('address'),
    tel = request.POST.get('tel')
    site = request.POST.get('site')
    hours = request.POST.get('hours')
    to_del = request.POST.get('to_del')

    org_obj = MobiOrganizationsUnique.objects.get(id=int(org_id))
    if  to_del == 'false':
        org_user_change = MobiOrganizationsUserChanges(org_id=org_obj, user_name=name, user_email=email,
                                                       u_org_name='%s' % org_name, u_address='%s' % address, u_url=site,
                                                       u_phone=tel, u_hours=hours
                                                       )

        org_user_change.save()


    else:
        org_user_change = MobiOrganizationsUserChanges(org_id=org_obj, user_name=name, user_email=email,
                                                       u_org_name=u'Организации не существует',
                                                       u_address=u'Организации не существует', u_url=u'Организации не существует',
                                                       u_phone=u'Организации не существует', u_hours=u'Организации не существует',
                                                       )
        org_user_change.save()


    str = u'Ваша заявка принята к рассмотрению'
    return HttpResponse(str)


#=========================================================================================================
# проверяет есть ли различия между полями на форме и в базе
def ajax_user_chage_find_differnce(request):
    print 'ajax_user_change_find_differce'
    if not request.POST.has_key('org_id'):
        raise Http404
    org_id = request.POST.get('org_id')
    org_obj = MobiOrganizationsUnique.objects.get(id=org_id)
    str = ''
    if request.POST.get('org_name') != org_obj.org_name:
        str = str + 'org_name:name_org_all,'
    if request.POST.get('address') != org_obj.address:
        str = str + 'address:address_org_all,'
    if request.POST.get('tel') != org_obj.phone:
        print request.POST.get('tel')
        str = str + 'tel:tel_org_all,'
    if request.POST.get('site') != org_obj.url:
        str = str + 'site:site_org_all,'
    if request.POST.get('hours') != org_obj.hours:
        str = str + 'hours:hours_org_all'
    return HttpResponse(str)


#==========================================================================================================


def video_instruments(request, video_list, objs_count, select_list, year_objects, genre):
    context = {}
    section = request.GET.get('section')
    context['section'] = section
    context['video_page'] = True
    # year_objects = Video.objects.all() #.exclude( Q(year__contains = '2009') and Q(year__contains = '2014')).order_by('year')
    # select_list = Video.objects.all()
    context['chosen_value'] = "Введите название..."
    if video_list.filter(genres__translit_genre=genre):
        context['category'] = VideoGenre.objects.get(translit_genre=genre).genre

        video_list = video_list.filter(genres__translit_genre=genre)  # video_list.filter(genres__genre = category )
        select_list = video_list
        year_objects = video_list
        objs_count = video_list.count()
        objs_count = video_list.count()
    else:
        if genre != 'vse_ganri':
            try:
                context['category'] = VideoGenre.objects.get(translit_genre=genre).genre
                video_list = video_list.filter(genres__translit_genre=genre)
            except:
                raise Http404


    if request.GET.has_key('video_id'):
        video_list = Video.objects.all().filter(id=request.GET.get('video_id'))
        context['chosen_value'] = video_list[0]
        if request.GET.has_key('active_class'):
            context['category'] = request.GET.get('active_class')
            select_list = video_list
            year_objects = video_list
        objs_count = video_list.count()
        # context['active_all'] = False
    elif request.GET.has_key('year'):
        if request.GET.has_key('active_class_year'):  # Ищет по категории и по году одновременно
            context['category'] = request.GET.get('active_class_year')
            video_list = video_list.filter(Q(year__contains=str(request.GET.get('year'))), Q(genres__genre=request.GET.get('active_class_year')))
            select_list = video_list
            year_objects = video_list
        elif request.GET.has_key('section'):
            if request.GET.get('section') == 'films':
                video_list = Video.objects.filter(Q(year__contains=str(request.GET.get('year'))), Q (video_type=1))
            elif request.GET.get('section') == 'serials':
                video_list = Video.objects.filter(Q(year__contains=str(request.GET.get('year'))), Q (video_type=2))
        else:
            video_list = video_list.filter(year__contains=str(request.GET.get('year')))
            context['active_all'] = True
        if not video_list:
            context['message'] = u"К сожалению ничего не найдено"
        context['selected_year'] = request.GET.get('year')
        objs_count = video_list.count()

    video_genre = VideoGenre.objects.all()
    context['video_list'] = video_list.order_by('-date_aded')
    par = ['title', 'orig_title']
    context['select_list'] = [x  for x in select_list.order_by(*par)]
    context['year_objects'] = list(sorted(set([x.year for x in year_objects]), reverse=True))
    context['video_genre'] = video_genre
    context['objs_count'] = objs_count

    context.update(hotspot_identity(request))
    return context


@render_to('video.html')
def video_films(request, genre='vse_ganri'):
    context = {}
    context['placement'] = 17
    context['slug'] = 'films'

    video_list = Video.objects.all().filter(video_type=1)
    objs_count = video_list.count()
    select_list = video_list
    year_objects = video_list
    context['genre_one'] = Video.objects.all()[0].genres
    print context['genre_one']
    context['poisk_name'] = 'Поиск фильма по названию'
    context.update(video_instruments(request, video_list, objs_count, select_list, year_objects, genre))

    return context


@render_to('video.html')
def video_serials(request, genre='vse_ganri'):
    context = {}
    context['placement'] = 17
    context['slug'] = 'serials'

    video_list = Video.objects.all().filter(video_type=2)
    objs_count = video_list.count()
    select_list = video_list  # Содержание выбора селекта только по данной категории сериалы
    year_objects = video_list  # Селект годы содержит годы только сериалов
    context['poisk_name'] = 'Поиск сериала по названию'

    context.update(video_instruments(request, video_list, objs_count, select_list, year_objects, genre))

    return context


def change_url_gidonline(id_gid_film, video_object):
    print "=======change_url_gidonline=======change_url_gidonline======change_url_gidonline"
    str_vk = ''
    video_iframe = urllib.urlopen('http://gidonlinekino.com/1  trailer1.php', 'id_post=%s' % id_gid_film).read()
    try:
        soup = BeautifulSoup(video_iframe.decode('utf-8'))
    except TypeError:
        soup = BeautifulSoup(str(video_iframe))
    if not soup.find('iframe', {'id':'iframe_a'}).get('src').find('kinolove.tv') == -1:  #
        video_par = soup.find('iframe', {'id':'iframe_a'}).get('src').replace('http://kinolove.tv/?video=', '')
    else:
        print "Ne naydeno ssilki s parametrami vkontakte"
    url = 'http://kinolove.tv/'
    if video_par:
        video = {'video':video_par}
        headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip,deflate,sdch',
        'Accept-Language':'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Host':'kinolove.tv',
        'Referer':'http://gidonlinekino.com/2014/11/kolyuchka/',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'}
        r = requests.get(url, params=video, headers=headers)
        vk_params = re.findall(r'\w+\d+\w+[|]\d+[|]\d+', r.content)
        for vk_p in vk_params:
            vk_params = vk_p.split('|')
        for index, param in enumerate(vk_params):
            if index == 0:
                embed_hash = param
            elif index == 1:
                oid = -int(param)
            elif index == 2:
                video_id = param
        vk_request = requests.get('https://api.vk.com/method/video.getEmbed?oid=%s&video_id=%s&embed_hash=%s' % (oid, video_id, embed_hash))
        if not vk_request.content.find('"error_code":15') == -1:
            oid = -int(oid)
            vk_request = requests.get('https://api.vk.com/method/video.getEmbed?oid=%s&video_id=%s&embed_hash=%s' % (oid, video_id, embed_hash))
        print vk_request.url
        data = json.loads(vk_request.content)
        for k, response in data.items():
            if k == 'response':
                for k, v in response.items():
                    if k == 'url720':
                        str_vk = str_vk + (str(k) + ' ' + str(v)) + '|'
                        # print k, v
                    elif k == 'url240':
                        str_vk = str_vk + (str(k) + ' ' + str(v)) + '|'
                        # print k, v
                    elif k == 'url360':
                        str_vk = str_vk + (str(k) + ' ' + str(v)) + '|'
                        # print k, v
                    elif k == 'url480':
                        str_vk = str_vk + (str(k) + ' ' + str(v)) + '|'
                        # print k, v
            else:
                print "Json VK ne Vernul otvet"
    video_object.player_video_url = str_vk
    video_object.save()

@render_to('video_play.html')
def video_play(request, name):
    video = None
    context = {}
    context['placement'] = 17
    for obj in Video.objects.all():
            if obj.translit_video_name:
                if unicode(''.join(obj.translit_video_name.split())) == unicode(name):  # unicode(obj.translit_video_name)[:len(name)]
                    video = obj
    if video:
        id = video.player_video_url
        if video.video_type == 1:
            context['slug'] = 'films'
            context['ending_comment'] = 'фильму'
        elif video.video_type == 2:
            context['slug'] = 'serials'
            context['ending_comment'] = 'сериалу'
    else:
        raise Http404
    if not id.find('youtube') == -1:
        context['youtube'] = True

    context['id'] = id.split(',')[0]
    if not id.find('vk.me') == -1:  # Если ссылки с Гидонлай-на
        context['new_gidonline_player'] = True
        video_hd = []
        url_list = []
        for link in id.split('|'):
            try:
                if link.split(' ')[1] != '':
                    video_hd.append(link.split(' ')[1])
            except:
                pass
            try:
                if link.split(' ')[0] != '':
                    new_label = link.split(' ')[0].replace('url', 'hd ')
                    url_list.append(new_label)
            except:
                pass
        try:
            context['id'] = video_hd[0]
        except IndexError:
            context['id'] = video_hd[1]
        context['vk_new_video'] = zip(video_hd, url_list)
    try:
        if id.split(',')[1]:
           context['second_part'] = enumerate(id.split(','), start=1)
    except:
        pass
    video_object = Video.objects.get(player_video_url=str(id))
    if request.POST.has_key('change_url_gid'):
        print "change_url_gid =change_url_gid ========change_url_gid======change_url_gid"
        if video_object.id_gid_film:
            change_url_gidonline(video_object.id_gid_film, video_object)
    context['video_name'] = video_object
    context['meta_description'] = video_object.description[:200].replace('&nbsp;', '')
    if video_object.video_type == 2:
        context['serials'] = True
    context['zip'] = zip(video_object.label_text.split("| "), video_object.one_serial_links.split("| "))
    context['video_page'] = True

    # Получение комментариев от пользователя
    if request.POST.has_key('comment_content'):
        commentator_name = request.POST.get('commentator_name')
        comment_content = request.POST.get('comment_content')
        # print commentator_name
        # print comment_content
        comment = Comments_Of_Video()
        # comment.id = request.GET.get('id')
        comment.commentator_name = commentator_name
        comment.comment_content = comment_content
        comment.save()
        video.comments_m2m.add(comment)
        video.save()

    context.update(hotspot_identity(request))

    context['comments'] = video_object.comments_m2m.all().order_by('-id')

    return context

from hotspot.models import *  # HotSpot_Bad_Video_Link

def bad_link(request):
    obj = HotSpot_Bad_Video_Link.objects.all().order_by('id')
    hidden_id = int(obj.reverse()[0].id) + 1
    exist = request.POST.get('broken_video_id')
    if exist:
        broken_film = request.POST.get('broken_video_id')
        video = Video.objects.get(id=broken_film)
        # if request.POST.has_key('text'):
        sms = HotSpot_Bad_Video_Link()
        sms.contact_face = request.POST.get('contact_face')
        sms.mail = request.POST.get('mail')
        sms.text = request.POST.get('text')
        sms.broken_video_id = request.POST.get('broken_video_id') + " " + video.title + " " + video.orig_title
        sms.save()

        send_email(u'Сообщение о неработающем видео', "ID фильма  %s , ссылка: http://globalhome.su/admin/hotspot/hotspot_bad_video_link/%s/" % (str(broken_film), str(hidden_id)), settings.DEFAULT_FROM_EMAIL, ["Zz1n@globalhome.su", 'sales@globalhome.su', 'noc@globalhome.su'])
        return HttpResponse(u'Сообщение отправлено. Компнаия Globalhome благодарит вас за Ваше участие!!! ')
    else:
        return HttpResponse(u'Сообщение не отправлено. Не получено данных')


def save_ob2(object_id, obj):
    obj2 = Video.objects.get(id=object_id)
    obj2.site_rating = obj
    obj2.save()

def count_rate(request, object_id, score):
    try:
        obj = Video_Rate.objects.get(id=object_id)
        save_ob2(object_id, obj)
    except Video_Rate.DoesNotExist:
        obj = Video_Rate(rating_score=0, rating_votes=0)
        obj.id = object_id
    obj.rating_score = float(obj.rating_score) + float(score)
    obj.rating_votes = int(obj.rating_votes) + int(1)
    obj.save()
    save_ob2(object_id, obj)

    return HttpResponse('%s , %s' % (object_id, score))




