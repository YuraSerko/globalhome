  # -*- coding=utf-8 -*-

from lib.decorators import render_to, login_required
from cards.forms import ContactForm
from django.utils.translation import ugettext_lazy as _, ugettext
import datetime
from django.db import connections, transaction
import settings
from django.shortcuts import render_to_response
from models import BillserviceCard
from account.views import login
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound


from lib.decorators import render_to
from account.forms import UserRegistrationForm
from account.forms import UserLoginForm2, PasswordResetRequestForm
from account.models import *
from billing.models import *
from externalnumbers.consts import *
from django.contrib.auth import authenticate, login as _login, logout as _logout
from lib.helpers import redirect, next
from django.utils.encoding import iri_to_uri, force_unicode
from content.models import Article
from django.utils.translation import ugettext_lazy as _, ugettext

# @login_required
@render_to("activationcards.html")
def activationcard(request):
    context = {}
    if request.method == 'POST':
        form = ContactForm(request.POST.copy())
        context['form'] = form
        if 'activ' in request.POST:
            form = ContactForm(request.POST.copy())
            if form.is_valid():
                context['form'] = form
                login = form.cleaned_data["login"]
                pin = form.cleaned_data["pin"]
                cur = connections[settings.BILLING_DB].cursor()
                cur2 = connections[settings.GLOBALHOME_DB2].cursor()


                status_ok = 1
                status_bad_userpassword = 2
                status_card_was_activated = 3
                now = datetime.datetime.now()
                transaction.commit_unless_managed(settings.BILLING_DB)
    #            transaction.commit_unless_managed(settings.GLOBALHOME_DB2)
                if login and pin:
                    try:
                        return_status = 0
                        cur.execute("SELECT * FROM billservice_card WHERE type=3 and login=%s and pin=%s and sold is not Null and disabled=False FOR UPDATE;", (login, pin,))
                        card = cur.fetchone()
                        transaction.commit_unless_managed(settings.BILLING_DB)
                        transaction.commit_unless_managed(settings.GLOBALHOME_DB2)


                        if not card:
                            return_status = status_bad_userpassword
                            context.update({'error_userpassword' : True})
                            return context
    #                        return HttpResponseRedirect("../login")
    #                    return render_to_response ('account/login?param1=value1)

                        if card[5] or card[7] > now or card[8] < now:
                            return_status = status_card_was_activated
                            context.update({'error_was_activated' : True})
                            return context

                        if not return_status:



                            cur.execute("""INSERT INTO billservice_account(username, "password",  ipn_status, status, created, ipn_added, allow_webcab, allow_expresscards, group_id)
                            VALUES(%s, %s, False, 1, now(), False, True, True, 4) RETURNING id;""", (login, pin,))



                            account_id = cur.fetchone()[0]



                            cur.execute("INSERT INTO billservice_prepaid_minutes(zone_id, minutes, account_id) SELECT telzone_id, %s, %s FROM billservice_tariff_tel_zone WHERE tariff_id=%s;", (card[4] // 10, account_id, card[13]))

                            cur.execute("""
                            INSERT INTO internal_numbers(
                                     account_id, username, "password", nas_id,
                                    allow_addonservice, type)
                            VALUES (%s, %s, %s, %s,
                                    True,1);
                            """, (account_id, login, pin, card[14]))

                            cur.execute("INSERT INTO billservice_accounttarif(account_id, tarif_id, datetime) VALUES(%s, %s, %s);", (account_id, card[13], now))

                            cur.execute(u"""
                            INSERT INTO billservice_transaction(bill, account_id, type_id, approved, tarif_id, summ, description, created, promise, end_promise)
                            VALUES('Активация карты доступа', %s, 'ACCESS_CARD', True, %s, %s,'', %s, False, Null);
                            """, (account_id, card[13], card[4], now))

                            cur.execute("UPDATE billservice_card SET activated = %s, activated_by_id = %s WHERE id = %s;", (now, account_id, card[0]))

                            is_activee = True
                            first_namee = ""
                            last_namee = ""
                            emaill = ""
                            isstave = False
                            is_superuser = False
                            is_jurudical = False
                            is_cardd = True



                            print "1212"
                            cur2.execute("INSERT INTO auth_user(username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (login, first_namee, last_namee, emaill, pin, isstave, is_activee, is_superuser, now, now))

                            cur2.execute("SELECT id FROM auth_user WHERE username=%s;", (login,))
                            id_acount_card = cur2.fetchone()


                            cur2.execute("INSERT INTO account_profile(user_id, billing_account_id, activated_at, modified_at, is_juridical, is_card) VALUES(%s, %s, %s, %s, %s, %s);", (id_acount_card, account_id, now, now, is_jurudical, is_cardd))



                            return_status = status_ok
                            transaction.commit_unless_managed(settings.BILLING_DB)
                            transaction.commit_unless_managed(settings.GLOBALHOME_DB2)

                            context.update({'status_ok' : True})



                        return context

                    except Exception, e:
                        print e
                        transaction.rollback_unless_managed(settings.BILLING_DB)
                        transaction.rollback_unless_managed(settings.GLOBALHOME_DB2)
                        return

            else:
                return context
    else:
        form = ContactForm()
        context['form'] = form
        return context

    return context

from django.contrib.admin.views.decorators import staff_member_required
def get_ready_context(request, title):
    context = {}
    context["request"] = request
    context["user"] = request.user
    context["title"] = title
    context["is_popup"] = True if (request.GET and request.GET.get("_popup")) else False
    context["csrf_token"] = request.COOKIES.get("csrftoken")
    context["app_label"] = "telnumbers"
    context["app_section"] = _(u"Local numbers")
    context["language"] = "ru"
    context["none_value"] = "---"
    return context

@staff_member_required
@render_to("generate_cards.html")
def generate_card(request):
    context = get_ready_context(request, _(u"Add local numbers"))
    card = BillserviceCard.generate_card(100, '1')
    context['card'] = card
    return context



