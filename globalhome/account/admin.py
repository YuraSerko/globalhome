# -*- coding=utf-8 -*-
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from account.models import Profile, Address, fax_sending
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from billing.models import BillserviceAccount, BillservicePhoneTransaction
# from tariffs.models import TariffGroup
from django.http import HttpResponseRedirect
from prices.models import PricesGroup
from django.contrib.sites.models import Site
from lib.decorators import render_to
from django.contrib.admin.views.decorators import staff_member_required
from telnumbers.models import TelNumbersGroupNumbers, TelNumber, TelNumbersGroup
from externalnumbers.models import ExternalNumber
from lib.paginator import SimplePaginator
from forms import ProfileJuridicalDataForm, ProfilePhisicalDataForm, BalanceForm, UserForm, AddressBaseForm, BillingAccountFormIdle
from django.core.urlresolvers import reverse
from django.conf.urls import url
from lib.decorators import render_to
from account.managers import EmailManager
from lib.session_decode import session_delete
from forms import SendLetterToBlock
from adminmail.models import Letter
from managers import lockout_notification_email
from page.models import Send_mail
# from django.utils import timezone
import datetime


admin.site.unregister(User)


class UserProfileInlinePhysical(admin.StackedInline):
    model = Profile
    readonly_fields = ['addresses']
    exclude = ['company_name', 'sign_face', 'sign_cause', 'kpp']
    extra = 0
    max_num = 1

class UserProfileInline(admin.StackedInline):
    model = Profile
    readonly_fields = ['addresses']
    extra = 0
    max_num = 1

# class IsJuridicalFilterSpec(ChoicesFilterSpec):
#    def __init__(self, f, request, params, model, model_admin):
#        ChoicesFilterSpec.__init__(self, f, request, params, model, model_admin)
#        self.lookup_kwarg = 'profile__is_juridical'
#        self.lookup_val = request.GET.get(self.lookup_kwarg)
#
#        self.lookup_choices = ((1, _("Yes")), (0, _(u"No")))
#
#    def choices(self, cl):
#        yield { 'selected': self.lookup_val is None,
#                'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
#                'display': _('All') }
#        for val, verbose in self.lookup_choices:
#            yield {
#                'selected' : str(val) == self.lookup_val,
#                'query_string': cl.get_query_string({self.lookup_kwarg: val}),
#                'display': verbose }
#
#    def title(self):
#        # return the title displayed above your filter
#        return _(u"Legal person")
#
# class IsCardFilterSpec(ChoicesFilterSpec):
#    def __init__(self, f, request, params, model, model_admin):
#        ChoicesFilterSpec.__init__(self, f, request, params, model, model_admin)
#        self.lookup_kwarg = 'profile__is_card'
#        self.lookup_val = request.GET.get(self.lookup_kwarg)
#
#        self.lookup_choices = ((1, _("Yes")), (0, _(u"No")))
#
#    def choices(self, cl):
#        yield { 'selected': self.lookup_val is None,
#                'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
#                'display': _('All') }
#        for val, verbose in self.lookup_choices:
#            yield {
#                'selected' : str(val) == self.lookup_val,
#                'query_string': cl.get_query_string({self.lookup_kwarg: val}),
#                'display': verbose }
#
#    def title(self):
#        # return the title displayed above your filter
#        return _(u"Cards")
#
# FilterSpec.filter_specs.insert(0,
#    (lambda f: getattr(f, 'is_juridical_filter', False), \
#        IsJuridicalFilterSpec)
# )
# FilterSpec.filter_specs.insert(0,
#    (lambda f: getattr(f, 'is_card_filter', False), \
#        IsCardFilterSpec)
# )

User._meta.get_field('email').is_juridical_filter = True
User._meta.get_field('email').verbose_name = _("E-mail address")
User._meta.get_field('username').is_card_filter = True

class CustomerAccount(User):
    class Meta:
        proxy = True
        app_label = 'account'
        verbose_name = _('Customer account')
        verbose_name_plural = _('Customer accounts')


def compare(user_word, search_word):
    if not(user_word) or not(search_word):
        return False
    user_word = list(user_word)
    search_word = list(search_word)
    start_user_position = -1
    while (start_user_position < len(user_word)):
        start_user_position += 1
        i = start_user_position
        while (i < len(user_word)) and (i < len(search_word)) and (search_word[0] != user_word[i]):
            i += 1
        start_user_position = i
        j = 0
        while (i < len(user_word)) and (j < len(search_word)) and (user_word[i] == search_word[j]):
            i += 1
            j += 1
        if j == len(search_word):
            return True
        if i == len(user_word):
            return False

class Staff(User):
    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = _('staff account')
        verbose_name_plural = _('Staff management')

# Класс для введения глобальных переменных
# имеет 3 поля: sort_field - поле хранит сортируемый абзац для списка профилей
# is_juridical - для фильтрации объектов Profile по полю is_juridical
# objects - для хранения объектов Profile, чтобы не загружать их заново и фильтровать, если необходимо
class GlobalParam:
    sort_field = 0
    is_juridical = -1
    is_active = -1
    is_search = ''
    page = 1
    objects = None
    paginator = None


def from_qs_to_sort_objs(filter_field, columns, was_changed):
    qs, param, queryset = GlobalParam.objects, GlobalParam.sort_field, []
    if not(was_changed) and GlobalParam.paginator:
        paginator = SimplePaginator(GlobalParam.paginator, 50, filter_field)
        return paginator
    billAccounts = BillserviceAccount.objects.all()
    balances = {0: (0, 0)}
    for b in billAccounts:
        balances[b.id] = (b.ballance, b.credit)
    for pr in (qs):
        queryset.append({'user_id' : pr.user.id, 'username' : pr.user.username, 'user' : pr.get_company_name_or_family(), 'email': pr.user.email, 'balance':balances[pr.billing_account_id or 0][0], \
                         'credit': balances[pr.billing_account_id or 0][1], 'is_juridical' : pr.is_juridical, 'is_active': pr.user.is_active, })
    if param < 0:
        queryset = sorted(queryset, key=lambda d: d[columns[abs(param)].lower()], reverse=True)
    elif param > 0:
        queryset = sorted(queryset, key=lambda d: d[columns[abs(param)].lower()])
    GlobalParam.paginator = queryset
    paginator = SimplePaginator(queryset, 50, filter_field)
    return paginator




@staff_member_required
@render_to("account/send_email_to_block.html")
def to_block_profile(request, user_id):
    user = User.objects.get(id=user_id)
    text = ''.decode('utf-8')
    if request.GET.has_key('send_email'):
        try:
            current_domain = Site.objects.get_current().domain
            mail_context = {'username': 'User login name', 'domain': 'Current domain', }
            letter = Letter.objects.get(code="NOTIFICATION_OF_LOCKOUT", language_code="ru")
            letter_obj = SendLetterToBlock(instance=letter)
            if not(request.POST):
                context = {"letter": letter_obj, 'mail_context': mail_context }
                return context
            else:
                letter_obj = SendLetterToBlock(request.POST.copy(), instance=letter)
                if letter_obj.is_valid():
                    letter.subject = letter_obj.cleaned_data['subject']
                    letter.texttemplate = letter_obj.cleaned_data['texttemplate']
                lockout_notification_email(user, letter, mail_context)
        except Letter.DoesNotExist:
            print "Can't send letter to user. Because required letter with code NOTIFICATION_OF_LOCKOUT.\
                    Create this letter in adminmail"
    user.is_active = False
    user.save()
    try:
        billservice_account = BillserviceAccount.objects.get(id=Profile.objects.get(user=user).billing_account_id)
        telNumbers = TelNumber.objects.filter(account_id=billservice_account.id)
        print billservice_account.id, len(telNumbers)
        for telNumber in telNumbers:
            telNumber.account_id = None
            try:
                telNumber.save()
            except Exception, e:
                info = '\nНе удалось пересохранить объект модели TelNumber, где id=%s по причине: %s' % (telNumber.id, e)
                text += info.decode('utf-8')
        billservice_account.status = 4
        try:
            billservice_account.save()
        except Exception, e:
            info = '\nНе удалось пересохранить объект модели BillserviceAccount, где id=%d по причине: %s' % (billservice_account.id, e)
            text += info.decode('utf-8')
    except Profile.DoesNotExist:
        pass
    session_delete(user_id)
    juridical_field = '?is_jur=%s' % (GlobalParam.is_juridical)
    if GlobalParam.is_juridical == -1 or GlobalParam.is_juridical == None:
        juridical_field = '?'
    active_field = '&is_act=%s' % GlobalParam.is_active
    if GlobalParam.is_active == -1 or GlobalParam.is_active == None:
        active_field, GlobalParam.is_active = '', -1
    else:
        GlobalParam.is_active = None
    filter_field = juridical_field + active_field
    if GlobalParam.is_search:
        filter_field += '&q=%s' % GlobalParam.is_search
    if GlobalParam.sort_field:
        filter_field += '&o=%s' % GlobalParam.sort_field
    text += u'User %s was locked' % (user.username)
    request.notifications.add(text)
    return HttpResponseRedirect(request.path.replace(user_id + "/delete/", filter_field))


# Для отображения объектов Profile
@staff_member_required
@render_to("account/change_list.html")
def customer_admin(request):
    context = {}

    context['notifications'] = request.notifications
    data_profile = list()
    filter = [{'selected':False, 'url':'?', 'display':'All'},
              {'selected':False, 'url':'?is_jur=1', 'display':'Yes'},
              {'selected':False, 'url':'?is_jur=0', 'display':'No'}]
    active_filter = [{'selected':False, 'url':'?', 'display':'All'},
              {'selected':False, 'url':'?is_act=1', 'display':'Yes'},
              {'selected':False, 'url':'?is_act=0', 'display':'No'}]
    columns = {1:'User_id', 2:'Username', 3:'User', 4:'Email', 5: 'Balance', 6:'Credit', 7:'Is_juridical', 8:'Is_active'}
    active_field, search_field, juridical_field, sort_field, GlobalParam.page = '', '', '', '', 1
    was_changed = False
    if request.GET.has_key('page'):
        GlobalParam.page = request.GET['page']
    if request.GET.has_key('o'):
        if (GlobalParam.sort_field != int(request.GET['o'])):
            GlobalParam.sort_field, was_changed = int(request.GET['o']), True
        if int(request.GET['o']) != 0:
            sort_field = '&o=' + request.GET['o']
    else:
        GlobalParam.sort_field = 1

    if (GlobalParam.is_juridical == -1 or GlobalParam.is_active == -1) or request.GET.has_key('q') and (len(request.GET['q']) == 0 or request.GET['q'] != GlobalParam.is_search) or (request.GET == {}):
        GlobalParam.is_juridical, GlobalParam.is_active, GlobalParam.paginator = None, None, None
        GlobalParam.objects = Profile.objects.select_related()

    if request.GET.has_key('is_jur'):
        if GlobalParam.is_juridical != int(request.GET['is_jur']) or (request.GET.has_key('is_act') and GlobalParam.is_active != int(request.GET['is_act'])) or\
         (not(request.GET.has_key('is_act')) and GlobalParam.is_active != None):
            if not(request.GET.has_key('is_act')):
                GlobalParam.is_active = None
            GlobalParam.objects, was_changed = Profile.objects.select_related(), True
            GlobalParam.is_juridical = int(request.GET['is_jur'])
            GlobalParam.objects = GlobalParam.objects.filter(is_juridical=(GlobalParam.is_juridical == 1))
        juridical_field = '&is_jur=' + str(GlobalParam.is_juridical)
    elif(GlobalParam.is_juridical != None) or (request.GET.has_key('is_act')) and (GlobalParam.is_active != int(request.GET['is_act'])):
        GlobalParam.objects = Profile.objects.select_related()
        GlobalParam.is_juridical = None
        was_changed = True

    if request.GET.has_key('is_act'):
        if GlobalParam.is_active != int(request.GET['is_act']) or was_changed or (not(request.GET.has_key('is_jur')) and GlobalParam.is_juridical != None):
            GlobalParam.is_active, was_changed = int(request.GET['is_act']), True
            GlobalParam.objects = GlobalParam.objects.filter(user__is_active=(GlobalParam.is_active == 1))
        active_field = '&is_act=' + str(GlobalParam.is_active)
    else:
        GlobalParam.is_active = None

    if request.POST.has_key('select_across'):
        id_profile_delete = request.POST['select_across'].split(",")[1:]
        print id_profile_delete

    if request.GET.has_key('q') and len(request.GET['q']):
        GlobalParam.is_search = (request.GET['q']).strip()
        profile_objs, qs, was_changed = GlobalParam.objects, [], True
        for profile in profile_objs:
            if compare(profile.user.username.lower(), GlobalParam.is_search.lower()) or  compare(profile.get_company_name_or_family().lower(), GlobalParam.is_search.lower())\
            or compare(str(profile.billing_account_id), GlobalParam.is_search) or compare(str(profile.user.id), GlobalParam.is_search) or compare(str(profile.user.email), GlobalParam.is_search):
                qs.append(profile)
        GlobalParam.objects = qs
        search_field = '&q=' + GlobalParam.is_search
    else:
        GlobalParam.is_search = ''
    context['count'] = len(GlobalParam.objects)
    filter_field = juridical_field + active_field + search_field + sort_field
    paginator = from_qs_to_sort_objs("?page=%s" + filter_field, columns, was_changed)
    paginator.set_page(request.GET.get('page', 1))
    objs = paginator.get_page()
    for i, pr in enumerate(objs):
        row = "row2"
        if i % 2 == 0:
            row = "row1"
        pr["row"] = row
        data_profile.append(pr)
    for i, value in enumerate([None, 1, 0]):
        if GlobalParam.is_active == value:
            active_filter[i]['selected'] = True
        if GlobalParam.is_juridical == value :
            filter[i]['selected'] = True
        active_filter[i]['url'] = active_filter[i]['url'] + juridical_field + search_field + sort_field
        filter[i]['url'] = filter[i]['url'] + active_field + search_field + sort_field
    context['paginator'] = paginator
    if GlobalParam.is_active != None:
        context['is_act'] = str(GlobalParam.is_active)
    if GlobalParam.is_juridical != None:
        context['is_jur'] = str(GlobalParam.is_juridical)
    context['cl'], context['o'], context['abs_o'] = data_profile, GlobalParam.sort_field, abs(GlobalParam.sort_field)
    context['columns'], context['filter'], context['active_filter'], context['q'] = columns, filter, active_filter, GlobalParam.is_search
    return context


from django import forms
class ProfileCreateInvoiceForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['create_invoice']
    def __init__(self, *args, **kwargs):
        super(ProfileCreateInvoiceForm, self).__init__(*args, **kwargs)
        self.fields['create_invoice'].label = u'Выставлять счета'

from account.forms import Zakazy_Custom_Form
from django.http import Http404
from data_centr.models import Zakazy




@staff_member_required
@render_to("account/customer_account_id.html")
def customeraccountid(request, user_id):

    forms = {}
    context = {}
    identification_numbers = {'User id':user_id}
    user_obj = User.objects.get(id=user_id)
    context["username"] = user_obj.username
    profile_obj = Profile.objects.get(user_id=user_id)
    user_obj.date_joined = (user_obj.date_joined.strftime("%Y-%m-%d %H:%M:%S"))
    user_form = UserForm(instance=user_obj)
    z_form = ('Номер заказа', 'Тип услуги', 'Дата создания', 'Дата активации', 'Дата деактивации', 'Статус заказа')
    context['z_form'] = z_form
    zakaz_multiple = Zakazy.objects.filter(Q(bill_account__id=profile_obj.billing_account_id), Q(date_deactivation__gte=datetime.date.today()) | Q(date_deactivation=None)).order_by('id')
    context['zakaz_mul'] = zakaz_multiple

    zakaz_objs = []
    for i, obj in enumerate(zakaz_multiple):  # tel_obj
        row = "row1"
        if i % 2 == 0:
            row = "row2"
        zakaz_objs.append({"row": row, "id":obj.id, "service_type":obj.service_type, "date_create":obj.date_create, "date_activation":obj.date_activation, "date_deactivation":obj.date_deactivation, "status_zakaza":obj.status_zakaza })
    context['zakaz_objs'] = zakaz_objs


    addr_form = None
    addr_form2 = None
    addresses = profile_obj.addresses.all()
    if profile_obj.is_juridical:
        addr_form = None if len(addresses) < 1 else AddressBaseForm(instance=addresses[0])
        addr_form2 = None if len(addresses) < 2 else(AddressBaseForm(instance=addresses[1], prefix='corporate'))
        form = ProfileJuridicalDataForm(instance=profile_obj)
    if profile_obj.is_juridical == False:
        addr_form = None if len(addresses) < 1 else AddressBaseForm(instance=addresses[0])
        form = ProfilePhisicalDataForm(instance=profile_obj)
    if not profile_obj.is_card:
        context['form'] = form
        context['aform'] = addr_form
        context['aform2'] = addr_form2
    identification_numbers['Profile id'] = profile_obj.id;

    if profile_obj.has_billing_account() == True:
        billaccount = BillserviceAccount.objects.get(id=profile_obj.billing_account_id)
        billaccount.credit = round(billaccount.credit, 2)
        billIdleForm = BillingAccountFormIdle(instance=billaccount)
        balance_form = BalanceForm(instance=billaccount)

        user = User.objects.get(username=billaccount)
        tel_form, telgrs_form = ('Телефонный номер', 'Имя владельца', 'Короткий номер', 'Пароль', 'Внешние номера'), ('Городской номер', 'Имя группы', 'Внутренние номера')

        tel_obj = TelNumber.objects.filter(account__id=billaccount.id)
        telgrs_obj = TelNumbersGroup.objects.filter(account__id=billaccount.id)
        tel_objs, telgr_objs = [], []
        for i, obj in enumerate(tel_obj):
            row, telnumbergroups = "row1", []
            if i % 2 == 0:
                row = "row2"
            for telnumbergroup in (TelNumbersGroup.objects.filter(numbers=obj)):
                telnumbergroups.append(ExternalNumber.objects.filter(phone_numbers_group=telnumbergroup))
            tel_objs.append({"row": row, "tel_number":obj.tel_number, "password":obj.password, "internal_phone":obj.internal_phone, "person_name":obj.person_name, "numbers":telnumbergroups})
        for i, obj in enumerate(telgrs_obj):
            row = "row1"
            if i % 2 == 0:
                row = "row2"
            telgr_objs.append({"row": row, "numbers":ExternalNumber.objects.filter(phone_numbers_group=obj),
                               "name":obj.name, "internal_numbers": TelNumbersGroupNumbers.objects.filter(telnumbersgroup=obj)})
        context['billIdleForm'] = billIdleForm
        context['billing_account_id'] = billaccount.id
        context['balance_form'] = balance_form
        context['tel_objs'] = tel_objs
        context['tel_form'] = tel_form
        context['telgrs_form'] = telgrs_form
        context['telgrs_objs'] = telgr_objs
        context['profile_create_invoice_form'] = ProfileCreateInvoiceForm(instance=profile_obj)
        identification_numbers['BillingAccount id'] = billaccount.id;
        identification_numbers[u'Личный счёт'] = ''.join(str(e) for e in [0 for x in range(10 - len(str(billaccount.id))) ]) + str(billaccount.id)
    context['identification_numbers'] = identification_numbers

    context['uform'] = user_form
    context['user_id'] = user_id

    if request.POST:
        if request.POST.has_key('delete'):
            if request.POST.has_key('send_email'):
                return HttpResponseRedirect(request.path + 'delete/?send_email=1')
            return HttpResponseRedirect(request.path + 'delete/')
        error_message, valid = [], True

        if context.has_key('balance_form'):
            billaccount.credit = request.POST['credit']
            billaccount.save()
            billIdleForm = BillingAccountFormIdle(request.POST.copy(), instance=billaccount)
            billIdleForm.save()
        if context.has_key('uform'):
            user_form = UserForm(request.POST.copy(), instance=user_obj)
            if user_form.is_valid():
                user_obj.save()
            else:
                valid = False
                error_message.append("Неверно заполнена форма с данными о User")
        if context.has_key('aform') and addr_form != None:
            addr_form = AddressBaseForm(request.POST.copy(), instance=addresses[0])
            if addr_form.is_valid():
                addr_form.save()
            else:
                valid = False
                error_message.append("Неверно заполнен адрес пользователя\n")
        if context.has_key('aform2') and context['aform2']:
            addr_form = AddressBaseForm(request.POST.copy(), instance=addresses[1], prefix='corporate')
            if addr_form.is_valid():
                addr_form.save()
            else:
                valid = False
                error_message.append("Неверно заполнен второй адрес пользователя\n")
        if context.has_key('profile_create_invoice_form'):
            form = ProfileCreateInvoiceForm(request.POST.copy(), instance=profile_obj)
            if form.is_valid():
                profile_obj.save()
        if context.has_key('form') and not(profile_obj.is_juridical):
            form = ProfilePhisicalDataForm(request.POST.copy(), instance=profile_obj)
            if form.is_valid():
                profile_obj.save()
            else:
                valid = False
                error_message.append("Неверно заполнена форма с данными о пользователе\n")
        if context.has_key('form') and (profile_obj.is_juridical):
            form = ProfileJuridicalDataForm(request.POST.copy(), instance=profile_obj)
            if form.is_valid():
                profile_obj.save()
            else:
                valid = False
                error_message.append("Неверно заполнена форма с данными о пользователе\n")
        if not(valid):
            print error_message
            context['form_is_not_valid'] = error_message
            return context
        # print request

        juridical_field = '?is_jur=%s' % (GlobalParam.is_juridical)
        if GlobalParam.is_juridical == -1 or GlobalParam.is_juridical == None:
            juridical_field, GlobalParam.is_juridical = '?', -1
        active_field = '&is_act=%s' % GlobalParam.is_active
        if GlobalParam.is_active == -1 or GlobalParam.is_active == None:
            active_field = ''
        filter_field = '' + juridical_field + active_field
        if GlobalParam.is_search != '':
            filter_field += '&q=%s' % GlobalParam.is_search
        if GlobalParam.sort_field != 0:
            filter_field += '&o=%s' % GlobalParam.sort_field
        return HttpResponseRedirect(request.path.replace(user_id + '/', ''))
    return context

class CustomerAdmin(UserAdmin):

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super(CustomerAdmin, self).get_urls()
        for i, u in enumerate(urls[1:]):
            if "_changelist" in u.name:
                urls[i] = url("^$", customer_admin)
            if "_delete" in str(u.name) and "_change" not in str(u.name) and "_changelist" not in str(u.name):
                context = to_block_profile
                urls[i] = url("^(.+)/delete/$", context)
            if "_change" in str(u.name) and "_delete" not in str(u.name) and "_changelist" not in str(u.name):
                context = customeraccountid
                urls[i] = url("^(.+)/$", context)
        return urls



class StaffAdmin(UserAdmin):

    def response_add(self, request, obj, post_url_continue=None):
        obj.is_staff = True
        obj.save()
        return super(UserAdmin, self).response_add(request, obj, post_url_continue)


    def queryset(self, request):
        qs = super(UserAdmin, self).queryset(request)
        qs = qs.filter(Q(is_staff=True) | Q(is_superuser=True))
        print qs
        return qs

class FaxSendingAdmin(admin.ModelAdmin):
    list_display = ('number', 'to_numb', 'status', 'date_send')
    list_filter = ('status',)
    search_fields = ('number',)



class Account(User):
    def adv_company_name(self):
        profile = self.get_profile()
        try:
            if profile.is_juridical:
                try:
                    return profile.company_name
                except:
                    return ""
            else:
                try:
                    return profile.last_name + " " + profile.first_name + " " + profile.second_name
                except:
                    return ""
        except:
            return ""
    adv_company_name.short_description = _("Company name")
    class Meta:
        proxy = True
        app_label = 'account'
        verbose_name = _(u'Поиск пользователя')
        verbose_name_plural = _(u'Поиск пользователя')




class AccountAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    list_display = ['id', 'username', 'adv_company_name', 'email', 'is_juridical', 'is_active', 'reg', 'last', "balance", "credit"]
    search_fields = ['username', 'email']
    actions = None
    spoecialSearchField = ['adv_company_name']
    specialFields = [ "adv_company_name", 'reg', 'last', "balance", "credit"]

    def is_juridical(self, obj):
        try:
            return obj.get_profile().is_juridical
        except:
            return False
    is_juridical.short_description = _(u"Legal person")
    is_juridical.boolean = True

    def reg(self, obj):
        return obj.date_joined.strftime("%Y-%m-%d %H:%M:%S")
    reg.short_description = User._meta.get_field_by_name('date_joined')[0].verbose_name
    reg.admin_order_field = 'date_joined'


    def last(self, obj):
        return obj.last_login.strftime("%Y-%m-%d %H:%M:%S")
    last.short_description = User._meta.get_field_by_name('last_login')[0].verbose_name
    last.admin_order_field = 'last_login'


    def balance(self, obj):
        try:
            profile = obj.get_profile()
            bill_object = BillserviceAccount.objects.get(id=profile.billing_account_id)
            return bill_object.ballance
        except:
            return 0
    balance.allow_tags = True
    balance.short_description = _(u"Ballance")

    def credit(self, obj):
        try:
            profile = obj.get_profile()
            bill_object = BillserviceAccount.objects.get(id=profile.billing_account_id)
            return bill_object.credit
        except:
            return 0
    credit.allow_tags = True
    credit.short_description = _(u"Credit")


    def get_changelist(self, request, **kwargs):
        from changelist import SpecialChangeList
        return SpecialChangeList


    def get_urls(self):
        urls = super(AccountAdmin, self).get_urls()
        for i, u in enumerate(urls[1:]):
            if "_delete" in str(u.name) and "_change" not in str(u.name) and "_changelist" not in str(u.name):
                context = to_block_profile
                urls[i] = url("^(.+)/delete/$", context)
            if "_change" in str(u.name) and "_delete" not in str(u.name) and "_changelist" not in str(u.name):
                context = customeraccountid
                urls[i] = url("^(.+)/$", context)
        return urls
        # form.base_fields["service_type"] = zakaz_form

admin.site.register(Account, AccountAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(CustomerAccount, CustomerAdmin)
admin.site.register(fax_sending, FaxSendingAdmin)
