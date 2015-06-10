# -*- coding=utf-8 -*-
# $Id: models.py 239 2010-11-18 19:55:52Z dmitry $
import datetime
# from sorl.thumbnail.main import DjangoThumbnail
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
# from django.db.models import signals
from django.utils.safestring import mark_safe
from lib.db.models.fields import ImageField
from finoperations.models import BalanceOperation
from finoperations.consts import OP_TYPE_WITHDRAW
# from account.settings import PERSONAL_AREA_MENU, PERSONAL_AREA_MENU_CARD
from billing.models import create_billing_account
import log
from tariffs.models import TelZone  # TariffGroup,

# from django.http import Http404
# from settings_local import BILLING_DB
import string
from billing.models import BillservicePrepaidMinutes
from south.modelsinspector import add_introspection_rules
from django.db.models import Sum
rules = [
            (
                (ImageField,), [],
                {
                    "verbose_name": ["verbose_name", {"default": None}],
                }
            ),
        ]

add_introspection_rules(rules, ["^lib\.db\.models\.fields"])


site_reg = models.IntegerField(choices=settings.SITES, default=1)
site_reg.contribute_to_class(User, 'site_reg')
is_juridical = models.BooleanField(default=False)
is_juridical.contribute_to_class(User, 'is_juridical')


# patch User model
def set_password(self, raw_password):
    self.password = raw_password

def check_password(self, raw_password):
    return self.password == raw_password







User.add_to_class('set_password', set_password)
User.add_to_class('check_password', check_password)

#increase username max length
#User._meta.get_field("username").max_length = 75 # email in base  = 75
#User._meta.get_field('username').validators[0].limit_value = 75
#User._meta.ordering = ["username"]



def generate_username():
    return u"u_%s" % datetime.datetime.now().strftime('%y%m%d%H%M%S%f')

ADDRESS_TYPE_RESIDENTIAL = 1
ADDRESS_TYPE_LEGAL = 2
ADDRESS_TYPE_POSTAL = 3
ADDRESS_TYPE_PHYSICAL = 4
ADDRESS_TYPES = [
    (ADDRESS_TYPE_RESIDENTIAL, _(u"Residential")),
    (ADDRESS_TYPE_LEGAL, _(u"Legal")),
    (ADDRESS_TYPE_POSTAL, _(u"Postal")),
    (ADDRESS_TYPE_PHYSICAL, _(u"Physical")),
]

SEX_CHOICES = [(0, _(u"M")), (1, _(u"F"))]



class Address(models.Model):
    country = models.CharField(max_length=255, verbose_name=_(u"Country"))
    state = models.CharField(_('State'), max_length=100)  # , blank=True, null=True)
    zipcode = models.CharField(_('ZIP code'), max_length=10)  # , blank=True, null=True)
    city = models.CharField(_('City'), max_length=100)
    address_type = models.IntegerField(_(u"Address type"), default=ADDRESS_TYPE_RESIDENTIAL, \
                                       choices=ADDRESS_TYPES)
    address_line = models.TextField(_("Address line"))
    phones = models.TextField(_(u"Phones"), blank=True, null=True)

    def __unicode__(self):
        return ','.join([x for x in \
                   [self.country,
                    self.state or '',
                    self.zipcode or '',
                    self.city,
                    self.address_line or '',
                    self.phones or ''] \
                   if x != ''])

class ProfileManager(models.Manager):
    pass


class Profile(models.Model):
    """
    Profile - intermediate model between django auth and utm database
    """
    user = models.ForeignKey(User, unique=True)
    billing_account_id = models.IntegerField(null=True, blank=True, editable=False)  # Id in billing accounts table
    activated_at = models.DateTimeField(blank=True, null=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    # data
    is_juridical = models.BooleanField(default=False, editable=False)
    # billing_group_id = models.IntegerField(verbose_name = _(u"Tariff group"), default = 1)
    # billing_group = models.ForeignKey(TariffGroup, verbose_name = _(u"Tariff group"))
    first_name = models.CharField(verbose_name=_(u"First name"), max_length=255, null=True)
    second_name = models.CharField(verbose_name=_(u"Second name"), max_length=255, null=True)
    last_name = models.CharField(verbose_name=_(u"Last name"), max_length=255, null=True)
    birthday = models.DateField(verbose_name=_(u"Birsday"), null=True)
    pasport_serial = models.CharField(verbose_name=_(u"Passport series"), max_length=20)  # , null=True, blank=True)
    when_given_out = models.DateField(verbose_name=_(u"When it is given out"), null=True)
    by_whom_given_out = models.CharField(verbose_name=_(u"By whom it is given out"), null=True, max_length=120)
    sex = models.IntegerField(verbose_name=_(u"Sex"), choices=SEX_CHOICES, null=True)
#    avatar = ImageField(verbose_name=_(u"Avatar"), upload_to='uploads/avatar', null=True, blank=True)
    addresses = models.ManyToManyField(Address, null=True, blank=True)
    phones = models.TextField(verbose_name=_(u"Contact phones / fax"), null=True)
    company_name = models.CharField(verbose_name=_(u"Company name"), max_length=255, help_text=mark_safe(u"""\
                                                                        - в названии компании не должны быть употреблены кавычки<br>\
                                                                        - если перед названием компании должны присутствовать иные слова, то они должны быть указаны в поле правовая форма<br>\
                                                                        Пример: Общество с ограниченной ответственностью Консалтинговое Агентство «Радуга»<br>\
                                                                        поле "Название компании": Радуга<br>\
                                                                        поле "Правовая форма": Общество с ограниченной ответственностью Консалтинговое Агентство
                                                                        """))
    legal_form = models.CharField(verbose_name=_("legal_form"), max_length=255, null=True, blank=True, help_text=mark_safe(u"\
                                                                        - правовая форма должна быть написана в развернутом виде<br>\
                                                                        - правовая форма должна начинаться с заглавной буквы<br>\
                                                                        Пример: Общество с ограниченной ответственностью"))
    general_director = models.CharField(verbose_name=_(u"Director"), max_length=255, null=True, blank=True, help_text=_(u"Job title, Name"))
    sign_face = models.CharField(max_length=255, verbose_name=_(u"Person signing the contracts"), help_text=mark_safe(u"""\
                                                                        - должность, ФИО - в <red style="color:red">именительном падеже</red><br>\
                                                                        - должность должна начинаться с заглавной буквы<br>\
                                                                        Пример: Генеральный директор, Локтишов Илья Михайлович"""))
    # лицо подписывающее договоры в родительном падеже
    sign_face_in_a_genitive_case = models.CharField(max_length=255, null=True, blank=True, verbose_name=_(u"Person signing the contracts"), help_text=mark_safe(u"""\
                                                                        - должность, ФИО - в <red style="color:red">родительном падеже</red><br>\
                                                                        - должность должна начинаться с заглавной буквы<br>\
                                                                        Пример: Генерального директора, Локтишова Ильи Михайловича"""))
    sign_cause = models.CharField(max_length=255, verbose_name=_(u"On the basis of which signed contracts"))
    bank_name = models.CharField(verbose_name=_(u"Bank name"), max_length=255, null=True, blank=True)
    bank_address = models.CharField(verbose_name=_(u"INN"), max_length=255, null=True, blank=True)
    settlement_account = models.CharField(verbose_name=_(u"Settlement account"), max_length=255, null=True, blank=True)
    correspondent_account = models.CharField(verbose_name=_(u"Correspondent account"), max_length=255, null=True, blank=True)
    bik = models.CharField(verbose_name=_(u"BIK"), max_length=255, null=True, blank=True)
    okpo = models.CharField(verbose_name=_(u"OKPO"), max_length=255, null=True, blank=True)
    kpp = models.CharField(verbose_name=_(u"KPP"), max_length=20)  # , null=True, blank=True)
    is_card = models.BooleanField(default=False, editable=False)
    is_hostel = models.BooleanField(verbose_name=_(u"Hostel"), default=False)
    create_invoice = models.BooleanField(verbose_name=_(u"Debit account"), default=True)
    mail_for_document = models.EmailField(null=True, blank=True)
    access_to_personal_information = models.BooleanField(default=False)


    def get_display_name(self):
        if self.company_name:
            return self.user.username + " (%s)" % self.company_name
        else:
            return self.user.username


    def is_physical(self, obj):
        return self.is_juridical
    is_physical.boolean = True

    @property
    def billing_account(self):
        return create_billing_account(self.user)

    def main_billing_account_id(self):
        bac_temp = create_billing_account(self.user)
        bac = string.zfill(bac_temp.id, 10)
        return bac

    def has_inactive_phones(self):
        return False  # self.billing_account.phones.filter(activated = False).count != 0

    def has_external_numbers(self):
        return self.billing_account.has_external_numbers

    def how_to_activate_message(self):
        if self.is_juridical:
            msg = _(u'In order to activate inactive phone number, call from it to #activate#')
        else:
            msg = _(u'In order to activate inactive phone number, call from it to #activate# or refill balance')
        return mark_safe(u"%s. %s." % \
        (msg, _(u'See <a href="%(alink)s">"How to activate"</a> page for details') \
        % {'alink': reverse('article_by_slug', args=['how-to-activate'])}))

    def address(self, address_type):
        try:
            return self.addresses.filter(address_type=address_type)[0]
        except IndexError:
            return None

    def get_sex_display(self):
        if self.sex is None:
            return None
        try:
            return [i[1] for i in SEX_CHOICES if i[0] == self.sex][0]
        except IndexError:
            return None

    def get_birthday_display(self):
        if self.birthday:
            return self.birthday.strftime('%d.%m.%Y')
        return ''

    def has_billing_account(self):
        return None != self.billing_account_id

    def get_balance(self):
        return self.billing_account.ballance

    def get_credit(self):
        return self.billing_account.credit

    def withdraw_funds(self, value, cause=u""):
        "Снимает средства с баланса пользователя и создает запись в журнале операций по балансу"
        if hasattr(settings, "WITHDRAW_FUNDS"):
            if not settings.WITHDRAW_FUNDS:
                log.add("withdraw_funds. user='%s' value='%s' cause='%s'" % (self.user, value, cause))
                return
        BalanceOperation(
            operation_type=OP_TYPE_WITHDRAW,
            user=self.user,
            value=value,
            cause=cause
        ).save()
        bac = self.billing_account
        bac.ballance -= value
        bac.save()

    def get_inn_kpp(self):
        inn_kpp = ''
        if self.is_juridical:
            inn_kpp = u'ИНН/КПП покупателя: ' + self.bank_address + '/' + self.kpp
        return inn_kpp

    def get_company_name_or_family(self):
        if self.is_juridical:
            company_name_or_family = u'%s "%s"' % (self.legal_form if self.legal_form else '', self.company_name if self.company_name else '')
        elif not self.is_juridical:
            company_name_or_family = u'%s %s %s' % (self.last_name if self.last_name else '', self.first_name if self.first_name else '', self.second_name if self.second_name else '',)
        return company_name_or_family

    def get_legal_adrress(self):
        legal_adrress = ''
        for adrress in self.addresses.all():
            if adrress.address_type in (2, 4):
                legal_adrress = adrress.country + ', ' + adrress.state + ', ' + adrress.city + ', ' + adrress.address_line
        return legal_adrress

    def get_postal_adrress(self):
        postal_adrress = ''
        for adrress in self.addresses.all():
            if adrress.address_type in (3,):
                postal_adrress = adrress.country + ', ' + adrress.state + ', ' + adrress.city + ', ' + adrress.address_line
        return postal_adrress

    def get_free_minutes(self):
        zone_ids = BillservicePrepaidMinutes.objects.order_by('zone_id').filter(account_id=self.billing_account_id).distinct('zone_id')
        all_sums = {}
        for id_zone in zone_ids:
            zone_name = TelZone.objects.get(id=id_zone.zone_id).ru_RU
            min_summ = BillservicePrepaidMinutes.objects.filter(account_id=self.billing_account_id, zone_id=id_zone.zone_id).aggregate(Sum('minutes'))
            all_sums[zone_name] = min_summ['minutes__sum']
        return all_sums




# ActionRecord
from account.managers import RegistrationManager, ResetManager, EmailManager

ACTION_RECORD_TYPES = (
    ('A', _(u'Activation')),
    ('R', _(u'Password change/restore')),
    ('E', _(u'E-mail change')),
)

def filter_for_admin():
#    users = User.objects.all().order_by("username")
    result = []
    profiles = Profile.objects.select_related('user__username').all()
    for profile in profiles:
        name = '%s (%s)' % (profile.user.username, profile.company_name) if profile.company_name else profile.user.username
        result.append((profile.billing_account_id, name,))
    result = sorted(result, key=lambda tup: tup[1])
    result_first = [(0, '---')]
    result = result_first + result
    return result

# return user.id, name
def get_all_user_choices(no_staff=False, only_juridical=False, first_null=False):
    if no_staff:
        users = User.objects.filter(is_staff=False)
    else:
        users = User.objects.all()
    result = []
    if first_null:
        result.append((0, "---", "---"))
    for user in users:
        try:
            profile = user.get_profile()
            if only_juridical:
                if not profile.is_juridical:
                    continue
            name = profile.get_display_name()
        except:
            name = user.username
        result.append((user.id, name))
    return result

class ActionRecord(models.Model):
    """Record that holds activation_key generated upon user registration"""
    user = models.ForeignKey(User)
    action_key = models.CharField(max_length=40)
    date = models.DateTimeField(auto_now_add=True)
    action_type = models.CharField(max_length=1, choices=ACTION_RECORD_TYPES)

    objects = models.Manager()
    registrations = RegistrationManager()
    resets = ResetManager()
    mail_for_documents = EmailManager()

    def get_mail(self):
        return self.mail_for_documents


    def __unicode__(self):
        return u"%s record for %s" % (self.get_action_type_display(), self.user.username)

    @property
    def expired(self):
        """
        Determines whether this Profile's activation key has expired,
        based on the value of the setting ``ACTION_RECORD_DAYS``.

        Set ``ACTION_RECORD_DAYS`` in 0 to disable expiring
        """
        if settings.ACTION_RECORD_DAYS:
            expiration_date = datetime.timedelta(days=settings.ACTION_RECORD_DAYS)
            return self.date + expiration_date <= datetime.datetime.now()
        else:
            return False
    class Meta:
        db_table = 'actionrecord'

def update_profile_on_activation(sender, **kwargs):
    pass

def get_base_url(user):
    """
    Returns base URL for user private area.
    This is usefull i.e. in login redirect etc.
    """
    if not user.get_profile().is_card:
        if settings.CURRENT_SITE in (1,):
            return reverse('service_choice')
        else:
            return reverse('account_profile')
    else:
        return reverse('account_profile')

class number_tarif(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    about = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        assigned_at = kwargs.pop("assigned_at", None)
        if not kwargs.pop("no_assigned_at_save", False):
            if assigned_at:
                self.assigned_at = assigned_at
            else:
                self.assigned_at = get_now()
        self.update_free_reserved(save=False)
        return super(ExternalNumber, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name
    class Meta:
        db_table = 'external_numbers_tarif'
        managed = True
        ordering = ("name",)
        verbose_name = _(u"Local number")
        verbose_name_plural = _(u"Local numbers")
        app_label = "telnumbers"

class fax_sending_temp(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    filename = models.ImageField(upload_to='fax/upl_fax', blank=True)
    enabled_size = models.BooleanField(default=False)
    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "fax_send_temp"

    def save(self, using=settings.BILLING_DB):
        super(fax_sending_temp, self).save(using=using)

class fax_sending(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    number = models.CharField(max_length=255, default='')  # с какого номера будет отправлен факс
    to_numb = models.CharField(max_length=255, default='')  # на этот номер будет отправлен факс
    add_number = models.CharField(max_length=255, default='')  # добавочный номер
    date_send = models.DateTimeField(null=True)  # время отправки факса
    # filename = models.CharField(max_length = 255, default = '') # путь к файлу
    status = models.CharField(max_length=255, default='')
    id_send = models.ForeignKey(fax_sending_temp)  # номер отправки факса, т.е. у каждой отправки будет свой номер
    def __unicode__(self):
        return self.id_send_id

    class Meta:
        app_label = 'fsmanage'
        db_table = "fax_send"
        ordering = ['number', 'to_numb']
        verbose_name = _(u"Отправленные факсы")
        verbose_name_plural = _(u"Отправленные факсы")

    def save(self, using=settings.BILLING_DB):
#        if using:
#            super(Rule, self).save(using = using)
#        else:
        super(fax_sending, self).save(using=using)
        # и записать еще в tel_numbers что есть переадресация
        # num = TelNumber.objects.using(using).get(tel_number = self.from_number)
        # num.has_forwarding = True
#        if using:
#            num.save(using = using)
#        else:
#            num.save()
class AllScheme(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    info = models.CharField(max_length=255, default='')  # с какого номера будет отправлен факс

    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "all_scheme_designer"

    def save(self, using=settings.BILLING_DB):
        super(AllScheme, self).save(using=using)

class OrderScheme(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    number_in_order = models.IntegerField()
    type = models.CharField(max_length=255, default='')
    id_next_scheme = models.ForeignKey(AllScheme, related_name="next_scheme")
    id_scheme = models.ForeignKey(AllScheme, related_name="scheme")
    id_element = models.IntegerField()
    number_in_arterial = models.IntegerField()
    level_width = models.IntegerField(default=1)
    nabor_for_ivr = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.id_scheme_id

    class Meta:
        db_table = "all_order_scheme"

    def save(self, using=settings.BILLING_DB):
        super(OrderScheme, self).save(using=using)


class AllSchemeDraft(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    info = models.CharField(max_length=255, default='')  # с какого номера будет отправлен факс
    id_scheme = models.ForeignKey(AllScheme)
    id_external_number = models.IntegerField()

    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "all_scheme_draft"

    def save(self, using=settings.BILLING_DB):
        super(AllSchemeDraft, self).save(using=using)



class CallTimeRange(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    billing_account_id = models.IntegerField()
    date_time_begin = models.TimeField(null=True)  # Начальное время интервала времени дня
    date_time_end = models.TimeField(null=True)  # Конечное время интервала времени дня

    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "call_time_range"

    def save(self, using=settings.BILLING_DB):
        super(CallTimeRange, self).save(using=using)

class CallNumber(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    billing_account_id = models.IntegerField()
    number = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "call_number"

    def save(self, using=settings.BILLING_DB):
        super(CallNumber, self).save(using=using)


#mine
from django.contrib.auth.models import AbstractUser
User._meta.get_field('username').max_length=50


class MyUser(AbstractUser):
    some_field = models.CharField(max_length=20)
    
    
USERNAME_LENGTH = 50
MyUser._meta.get_field('username').max_length = USERNAME_LENGTH
#end_mine