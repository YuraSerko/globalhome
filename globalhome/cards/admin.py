# coding: utf-8
from django.contrib import admin
from lib.decorators import render_to
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from models import BillserviceCard
from django.contrib import messages
from telnumbers.models import TelNumber
from billing.models import BillserviceAccount
from views import generate_card
# редактор текста тут -  from content import BaseContentAdmin

# @render_to("admin/tt2.html")
import datetime
from django.db import connections, transaction
import settings
import log

STATUSES_CREATE_MOBI_PROFILE = {1: u"Успешно создан",
                                2: u"Нет такой карты",
                                3: u"Карта уже активирована",
                                4: u"Получены неверные параметры",
                                - 1: u"Неизвестная ошибка",
                                0: u"Нулевой статус",
                                }

@transaction.commit_manually(using='billing')
@transaction.commit_manually
def create_mobi_sim_profile(login, pin):

    cur = connections[settings.BILLING_DB].cursor()
    cur2 = connections[settings.GLOBALHOME_DB2].cursor()

    status_ok = 1
    status_bad_userpassword = 2
    status_card_was_activated = 3
    now = datetime.datetime.now()
    # transaction.commit_unless_managed(settings.BILLING_DB)
    # transaction.commit_unless_managed(settings.GLOBALHOME_DB2)

    if not (login and pin):
        return_status = 4
    else:
        return_status = 0
        cur.execute("SELECT * FROM billservice_card WHERE type=3 and login=%s and pin=%s and sold is not Null and disabled=False FOR UPDATE;", (login, pin,))
        card = cur.fetchone()
        transaction.commit_unless_managed(settings.BILLING_DB)
        if not card:
            return status_bad_userpassword
        with transaction.commit_manually(using=settings.BILLING_DB):
            with transaction.commit_manually(using=settings.GLOBALHOME_DB2):
                transaction.commit(settings.BILLING_DB)
                transaction.commit(settings.GLOBALHOME_DB2)
                try:
                    
                    if card[5] or card[7] > now or card[8] < now:
                        return_status = status_card_was_activated


                    if not return_status:

                        cur.execute("""INSERT INTO billservice_account(username, "password",  ipn_status, status, created, ipn_added, allow_webcab, allow_expresscards, group_id)
                                        VALUES(%s, %s, False, 1, now(), False, True, True, 5) RETURNING id;""", (login, pin,))
                        account_id = cur.fetchone()[0]

                        cur.execute("""INSERT INTO internal_numbers(account_id, username, "password", nas_id,
                                                allow_addonservice, type)
                                        VALUES (%s, %s, %s, %s,
                                                True, 2);
                                        """, (account_id, login, pin, card[14]))

                        cur.execute("INSERT INTO billservice_accounttarif(account_id, tarif_id, datetime) VALUES(%s, %s, %s);", (account_id, card[13], now))

                        cur.execute(u"""INSERT INTO billservice_transaction(bill, account_id, type_id, approved, tarif_id, summ, description, created, promise, end_promise)
                                        VALUES('Активация профиля MobiSim', %s, 'ACCESS_CARD', True, %s, %s,'', %s, False, Null);
                                        """, (account_id, card[13], card[4], now))

                        cur.execute("UPDATE billservice_card SET activated = %s, activated_by_id = %s, account_id=%s WHERE id = %s;", (now, account_id, account_id, card[0]))

                        is_activee = True
                        first_namee = ""
                        last_namee = ""
                        emaill = ""
                        isstave = False
                        is_superuser = False
                        is_juridical = False
                        is_cardd = True

                        account = BillserviceAccount.objects.get(id=account_id,)
                        number = TelNumber.create(
                                account=account,
                                is_juridical=is_juridical,
                                # save=False,
                                is_mobi=True,
                            )

                        account.username = number.tel_number
                        account.save()

                        log.add("number=%s" % number.tel_number)

                        cur2.execute("INSERT INTO auth_user(username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (number.tel_number, first_namee, last_namee, emaill, pin, isstave, is_activee, is_superuser, now, now))

                        cur2.execute("SELECT id FROM auth_user WHERE username=%s;", (number.tel_number,))
                        id_acount_card = cur2.fetchone()

                        cur2.execute("INSERT INTO account_profile(user_id, billing_account_id, activated_at, modified_at, is_juridical, is_card) VALUES(%s, %s, %s, %s, %s, %s) RETURNING id;", (id_acount_card, account_id, now, now, is_juridical, is_cardd))
                        # a = cur2.fetchall()
                        # print a

                        return_status = status_ok

                except Exception, e:
                    # print "create mobi_sim_profile Except: %s" % e
                    log.add("create mobi_sim_profile Except: %s" % e)
                    transaction.rollback(settings.BILLING_DB)
                    transaction.rollback(settings.GLOBALHOME_DB2)
                    return_status = -1
                else:
                    transaction.commit(settings.BILLING_DB)
                    transaction.commit(settings.GLOBALHOME_DB2)

    return return_status

from django.conf.urls import patterns
class BillserviceCardAdmin(admin.ModelAdmin):

    list_display = ('login', 'pin', 'nominal', 'start_date', 'activated', 'tarif_id', 'type')  # отображаем калонками
    list_display_links = ('login',)  # какие поля доступны для изменения
    search_fields = ('login',)  # вверху  поиск
    list_filter = ('activated', 'tarif_id')  # справа  фильтр
    readonly_fields = ('series', 'pin', 'sold', 'nominal', 'activated', 'activated_by_id', 'start_date', 'end_date', 'disabled', 'created', 'template_id', 'account_id', 'tarif_id', 'nas_id', 'login', 'ip', 'ipinuse_id', 'type', 'ext_id', 'salecard_id')
#    date_hierarchy = 'time' # вверху  новая панель по выбору месяца
#    ordering = ('-time',) # сартировка по дате

    actions = ["create_mobi_sim_profile"]  # добавляет  поле в  всплывающий список  для  редактирование  выбранных  обьектов

#    # запретить добавление
#    def has_add_permission(self, request):
#        return False

    # запретить удаление
    def has_delete_permission(self, request, obj=None):
        return False
#    def has_change_permission(self, request, obj=None):
#        return False
    # Создание профиля MobiSim
    def create_mobi_sim_profile(self, request, queryset):
        for card in queryset:
            if card.tarif_id != 15:
                messages.error(request, u"Невозможно создать профиль MobiSim из %s, неверный тариф:%s" % (card.login, card.tarif_id))
                return
            result = create_mobi_sim_profile(card.login, card.pin)
            if result != 1:
                messages.error(request, u"Невозможно создать профиль MobiSim из %s, %s" % (card.login, STATUSES_CREATE_MOBI_PROFILE[result]))
                return
        messages.info(request, u"Succesfully created")

    def get_urls(self):
        urls = super(BillserviceCardAdmin, self).get_urls()
        my_urls = patterns('', ("^add/$", generate_card))
        return my_urls + urls



        # queryset.update(is_answered=True)
    create_mobi_sim_profile.short_description = u'Создать профиль MobiSim'

admin.site.register(BillserviceCard, BillserviceCardAdmin)

#    def change(self, request, queryset):
#        """
#            Админское действие - добавление поля
#        """
#        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
#        return HttpResponseRedirect("/change/?ids=%s" % ",".join(selected))
#    change.short_description = _(u"Dobawili pole")

#    add_form_template = "admin/tt2.html"
#    fields = ('name', 'text', 'time',) # в каком порядке отображать поля (почемуто неработает)
#    filter_horizontal = ('text',) # выбор несколких  через Ctrl (только с ManyToManyField)
#    raw_id_fields = ('name',) # добавляет иконку с увеличительным стеклом для поиска по выбранному id (только с ForeignKey)


