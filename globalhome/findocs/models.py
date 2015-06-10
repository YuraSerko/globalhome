# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from content.models import BaseContent
from consts import FIN_DOCS_TYPES_CHOICES
from django.utils.safestring import mark_safe
from ckeditor.fields import RichTextField as HTMLField
from lib.utils import get_now
from lib.models import ParamsModel
from services.consts import PACKET_DISCONNECTING
from data_centr.models import Service_type, Zakazy
import datetime
import calendar
from django.db.models import Min, Max
# from findocs.views import FINDOCS_NOT_TO_DELETE
# from findocs.functional_registry import FindocFunctionalRegistry
from south.modelsinspector import add_introspection_rules
from billing.models import BillserviceAccount
from dateutil.relativedelta import relativedelta
from account.models import Profile
from django.db.models import Q
import log
from django.conf import settings

rules = [
            (
                (HTMLField,), [],
                {
                    "verbose_name": ["verbose_name", {"default": None}],
                }
            ),
        ]

add_introspection_rules(rules, ["^ckeditor\.fields"])

class FinDocTemplate(BaseContent):

    class Meta:
        db_table = "fin_docs_templates"
        verbose_name = _(u"Financial document template")
        verbose_name_plural = _(u"Financial documents templates")

class FinDoc(models.Model):
    name = models.CharField(max_length=255, verbose_name=_(u"Document name"))
    type = models.IntegerField(choices=FIN_DOCS_TYPES_CHOICES, verbose_name=_(u"Document type"))
    display_name = models.CharField(max_length=255, verbose_name=_(u"Display name"), blank=True, null=True)
    description = models.TextField(verbose_name=_(u"Description"), blank=True, null=True)
    template = models.ForeignKey(FinDocTemplate, verbose_name=_(u"Template"))
    slug = models.SlugField(verbose_name=_(u"Slug"), unique=True)
    applied_to = models.ForeignKey('self', null=True, blank=True, verbose_name=_(u"Applied to"))

    # functional = models.CharField(max_length = 255, verbose_name = _(u"Document functional"), choices = FindocFunctionalRegistry.get_choices())

    def __unicode__(self):
        return self.display_name or self.name

    def get_signed(self, user):
        docs = FinDocSigned.objects.filter(findoc=self, signed_by=user)
        if docs.count() > 0:
            return docs[0]

    def create(self, user, by=None, save=True, params_data={}, user_can_cancel=True):
        return FinDocSignApplication.create(
            user, "", doc=self, by=by, save=save,
            params_data=params_data, user_can_cancel=user_can_cancel
        )

    def new_doc(self, user, by, service, user_can_cancel=True, transaction=None):
        app = FinDocSignApplication(
            service_for_billing=service,
            assigned_by=by,
            assigned_at=get_now(),
            findoc=self,
            assigned_to=user,
            user_can_cancel=user_can_cancel,
        )
        app.save()
        return app

    def new_doc_with_params(self, user, by, service, user_can_cancel=True, transaction=None, params_data={}):
        app = FinDocSignApplication(
            service_for_billing=service,
            assigned_by=by,
            assigned_at=get_now(),
            findoc=self,
            assigned_to=user,
            user_can_cancel=user_can_cancel,
        )
        app.pickle_params({"activation_zakaz": params_data})
        app.save()
        return app


    def create_from_sp_app(self, user, sp_app, by=None, params={}, user_can_cancel=True, transaction=None):
        app = FinDocSignApplication(
            assigned_by=by,
            assigned_at=get_now(),
            findoc=self,
            assigned_to=user,
            user_can_cancel=user_can_cancel,
        )
        app.pickle_params(params)
        app.save()
        if transaction:
            app.add_trans_wait.add(transaction)
        else:
            app.detach_packet_wait.add(sp_app)
        sp_app.packet.functionals_call("FindocApplicationCreated", app, sp_app, transaction=transaction)
        return app

    '''
    def get_functional(self):
        return FindocFunctionalRegistry.get_by_code(self.functional)
    '''

    class Meta:
        db_table = "fin_docs"
        verbose_name = _(u"Financial document")
        verbose_name_plural = _(u"Financial documents")

class FinDocSignApplication(ParamsModel):
    assigned_by = models.ForeignKey(User, editable=False, verbose_name=_(u"Assigned by"), related_name="+", blank=True, null=True)
    assigned_at = models.DateTimeField(editable=False, verbose_name=_(u"Assigned at"))
    findoc = models.ForeignKey(FinDoc, verbose_name=_(u"Financial document"))
    assigned_to = models.ForeignKey(User, verbose_name=_(u"Assigned to"))
    user_can_cancel = models.BooleanField(default=False, verbose_name=_(u"User can cancel this application"))
    service_for_billing = models.CharField(max_length=255)
    for_services = models.IntegerField(null=True)
    # from services.models import ServicePacketApplication
    # notify_sp_apps = ListModelsField(ServicePacketApplication)

    def __unicode__(self):
        return _(u"Sign application for the document %(document)s by user %(user)s") % {
            "document": self.findoc,
            "user": self.assigned_to,
        }

    def delete(self):
        print "FinDocSignApplication.delete() call..."
        return super(FinDocSignApplication, self).delete()

    def process_text(self, **kwargs):
        tt = self.findoc.template
        tt.processVars(["text"], **kwargs)
        return mark_safe(tt.text)


    def sign_with_params_data(self, user, text="", applied_to_id=""):
        sd = FinDocSigned(
            id=self.id,
            signed_by=user,
            signed_at=get_now(),
            findoc=self.findoc,
            signed_text=text,
            assigned_by=self.assigned_by,
            applied_to_id=applied_to_id,
        )
        sd.save()
        list_params = self.unpickle_params()
        list_params["findoc_id"] = sd.id
        self.delete()
        return list_params

    def sign(self, user, request=None, text="", signed_at=None, cancel_delete=False):
        "Подписывает эту заявку"

        if not signed_at:
            signed_at = get_now()
        sd = FinDocSigned(
            id=self.id,
            signed_by=user,
            signed_at=signed_at,
            findoc=self.findoc,
            signed_text=text,
            assigned_by=self.assigned_by,
        )
        sd.save()

        url = self.unpickle_params().get("redirect_after_sign")  #@attention: !!!!!!!!!!!!!!!!!!!!!!!!!
        if not url:
            if request:
                url = request.session.get("redirect_after_sign")

        if not cancel_delete:
            self.delete()

        transaction_id = self.unpickle_params().get("transaction_id")
        number_id = self.unpickle_params().get("number_from_detach")
        no_transaction = False
        if transaction_id:
            from services.models import AddSPTransaction
            try:
                transaction = AddSPTransaction.objects.get(id=transaction_id)
                transaction.findoc_app_signed(self, sd)
            except:
                no_transaction = True

        if not transaction_id or no_transaction:
            # работаем не с транзакцией, а просто с какой-то заявкой. - отключаем по заявке.
            sp_app_id = self.unpickle_params().get("sp_application_to_detach_id")
            if sp_app_id:
                from services.models import ServicePacketApplication
                sp_app = ServicePacketApplication.objects.get(id=sp_app_id)
                if sp_app.application_type == PACKET_DISCONNECTING:
                    sp_app.findoc_app_signed_detach(self, sd, number_id=number_id)
                else:
                    sp_app.findoc_app_signed(self, sd)
        return url

    def cancel(self, request=None, cancel_delete=False, no_notify=False):
        "Откланает эту заявку"
        if not self.user_can_cancel:
            raise Exception("Cannot cancel application '%s' because user_can_cancel is False!" % self)

        url = self.unpickle_params().get("redirect_after_cancel")  #@attention: переписывать!!!!!!!!!!!!!!!!!!!!!
        if not url:
            if request:
                url = request.session.get("redirect_after_cancel")

        if not cancel_delete:
            print "FinDocSignApplication.cancel(): self.delete()"
            self.delete()

        transaction_id = self.unpickle_params().get("transaction_id")
        no_transaction = False
        if transaction_id:
            from services.models import AddSPTransaction
            print "FinDocSignApplication: transaction canceling"
            try:
                transaction = AddSPTransaction.objects.get(id=transaction_id)
                transaction.findoc_app_canceled(self, no_notify=no_notify)
            except:
                no_transaction = True

        if not transaction_id or no_transaction:
            # отменяем не транзакцию а просто какую-то заявку
            print "FinDocSignApplication: cancel not transaction"
            sp_app_id = self.unpickle_params()["sp_application_to_detach_id"]
            if sp_app_id:
                from services.models import ServicePacketApplication
                sp_app = ServicePacketApplication.objects.get(id=sp_app_id)
                print "FinDocSignApplication: check application type and cancel it"
                if sp_app.application_type == PACKET_DISCONNECTING:
                    sp_app.findoc_app_canceled_detach(self)
                else:
                    sp_app.findoc_app_canceled(self)

        return url

    class Meta:
        db_table = "fin_docs_applications"
        verbose_name = _(u"Financial document sign application")
        verbose_name_plural = _(u"Financial documents sign applications")

class FinDocSigned(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    signed_by = models.ForeignKey(User, verbose_name=_(u"Signed by"), related_name="+")
    signed_at = models.DateTimeField(verbose_name=_(u"Signed at"))
    findoc = models.ForeignKey(FinDoc, verbose_name=_(u"Financial document"))
    assigned_by = models.ForeignKey(User, editable=False, verbose_name=_(u"Assigned by"), related_name="+", blank=True, null=True)
    signed_text = HTMLField(verbose_name=_(u"Text when signing"))
    applied_to_id = models.IntegerField(verbose_name=_(u"Applied to"), null=True, blank=True)
    cancellation_date = models.DateTimeField(null=True, blank=True)
    def __unicode__(self):
        return unicode(self.findoc) + " " + unicode(_("signed by")) + " " + unicode(self.signed_by)

    class Meta:
        db_table = "fin_docs_signeds"
        verbose_name = _(u"Signed financial document")
        verbose_name_plural = _(u"Signed financial documents")

class FinDocSignedZakazy(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    fin_doc = models.ForeignKey(FinDocSigned)
    zakaz_id = models.IntegerField()
    def __unicode__(self):
        return self.fin_doc

    class Meta:
        db_table = "fin_docs_signeds_m2m_data_centr_zakazy"


PACKAGE_STATUS_CHOICES = (
        (u'', u''),
        (u'Заявка в рассмотрении', u'Заявка в рассмотрении'),
        (u'Оборудование подготовлено', u'Оборудование подготовлено'),
    )

class Package_on_connection_of_service(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    user = models.ForeignKey(User)
    url_after_sign = models.CharField(max_length=255)
    url_after_cancel = models.CharField(max_length=255)
    slugs_document = models.TextField(null=True, blank=True)
    findoc_sign = models.ManyToManyField(FinDocSigned, null=True, blank=True)
    data = models.TextField(null=True, blank=True)
    activate = models.BooleanField(default=False)
    deactivate = models.BooleanField(default=False)
    # поле для договоров админа
    slugs_document_admin = models.TextField(null=True, blank=True)
    activate_admin = models.BooleanField(default=False)
    date_create = models.DateTimeField(null=True, blank=True)
    package_status = models.CharField(max_length=100, choices=PACKAGE_STATUS_CHOICES, default=u'', blank=True, null=True, verbose_name=u'Статус пакета')
    deliver_takeaway_date = models.DateTimeField(null=True, blank=True)


    def __unicode__(self):
        return str(self.id)

    class Meta:
        db_table = "package_on_connection_of_service"


ZAKAZ = 1
USLUGA = 2
TYPE_RULES = [
    (ZAKAZ, u'Заказ'),
    (USLUGA, u'Услуга'),
]

POSTPAID = 1
PREPAID = 2
TYPE_PAID = [
    (PREPAID, u'Предоплата'),
    (POSTPAID, u'Постоплата'),
]

from django.db import transaction
SERVICE_TYPE = [(f.id, f.service) for f in Service_type.objects.all()]
transaction.commit_unless_managed(using=settings.BILLING_DB)


class Rules_of_drawing_up_documents(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    type = models.IntegerField(choices=TYPE_RULES)
#    service_type = models.ManyToManyField(Service_type, blank=True, null = True, verbose_name=_(u"Service type"))
    service_type = models.IntegerField(choices=SERVICE_TYPE, blank=True, null=True)
    method_bill_acc = models.CharField(max_length=100, blank=True, null=True)
    findoc_juridical = models.ForeignKey(FinDoc, default=1, related_name='findoc_juridical')
    findoc_physical = models.ForeignKey(FinDoc, default=1, related_name='findoc_physical')
    name_service = models.CharField(max_length=255, blank=True, null=True)
    type_check = models.IntegerField(choices=TYPE_PAID)
    type_act = models.IntegerField(choices=TYPE_PAID)
    type_invoice = models.IntegerField(choices=TYPE_PAID)
    switch_on_off = models.BooleanField(default=True)
    def __unicode__(self):
        return str(self.id)

    class Meta:
        db_table = 'rules_of_drawing_up_documents'


class Document(models.Model):
    created_by = models.ForeignKey(User, editable=True, verbose_name=u'Пользователь')  # , default = 1
    year = models.IntegerField(default=datetime.datetime.now().year, verbose_name=u'Год')
    month = models.IntegerField(default=datetime.datetime.now().month, verbose_name=u'Месяц')
    every_month = models.BooleanField(default=False, verbose_name=u'Каждый месяц')  # default=False
    created_at = models.DateTimeField(default=datetime.datetime.now().date(), editable=True, verbose_name=u'Дата создания')
    text = HTMLField(null=True, blank=True, verbose_name=_('Text'))
    sent = models.BooleanField(default=False, null=False, verbose_name=u'Отправлено на почту')
    number = models.IntegerField(verbose_name=u'Номер счета')  # null=True,
    findoc = models.ForeignKey(FinDoc, default=1, verbose_name=u'Договор')
    type_paid = models.IntegerField(choices=TYPE_PAID, verbose_name=u'Тип оплаты')

    @staticmethod
    def get_next_number(class_model, year):
        min_number = class_model.objects.filter(year=year).aggregate(Min('number'))['number__min']
        max_number = class_model.objects.filter(year=year).aggregate(Max('number'))['number__max']
        count = class_model.objects.filter(year=year).count()
        if min_number and max_number:
            if count != max_number:
                for i in range(min_number, max_number + 1):
                    document = class_model.objects.filter(number=i)
                    if not document:
                        number = i
                        break
            else:
                number = max_number + 1
            try:
                number
            except:
                number = max_number + 1
        else:
            number = 1
        return number

    @staticmethod
    def create_record(class_model, user_obj, year, month, every_month, number_document, findoc_obj, type_paid, text_document):
        class_model_obj = class_model(
                          created_by=user_obj,
                          year=year,
                          month=month,
                          every_month=every_month,
                          created_at=datetime.datetime.now(),
                          sent=False,
                          number=number_document,
                          findoc=findoc_obj,
                          type_paid=type_paid,
                          text=text_document,
                          )
        class_model_obj.save()
        return class_model_obj

    @staticmethod
    def group_rules(profile_obj, spis_rules, type_rule, zakaz_id=0):
        group_rules_for_user = {}
        for rule_id in spis_rules:
            rule_obj = Rules_of_drawing_up_documents.objects.get(id=rule_id)
            if eval('rule_obj.%s' % type_rule) == 1:
                date_check_temp = datetime.datetime.now() - relativedelta(months=1)
            elif eval('rule_obj.%s' % type_rule) == 2:
                date_check_temp = datetime.datetime.now()
            if profile_obj.is_juridical:
                shablon_findoc_obj = rule_obj.findoc_juridical
            else:
                shablon_findoc_obj = rule_obj.findoc_physical
            if zakaz_id:
                try:
                    findoc_sign_zakaz = FinDocSignedZakazy.objects.get(zakaz_id=zakaz_id, fin_doc__findoc=shablon_findoc_obj)
                    findoc_signeds = [findoc_sign_zakaz.fin_doc]
                except FinDocSignedZakazy.DoesNotExist:
                    print 'FinDocSignedZakazy does not exist, zakaz_id = %s, user_id = %s' % (zakaz_id, profile_obj.user.id)
            else:
                findoc_signeds = FinDocSigned.objects.filter(Q(signed_by=profile_obj.user) & Q(findoc=shablon_findoc_obj) & (Q(cancellation_date=None) | Q(cancellation_date__gte=date_check_temp))).order_by('cancellation_date')
                if not findoc_signeds:
                    print 'Findoc id = %s does not exist, user_id = %s' % (shablon_findoc_obj, profile_obj.user.id)
            print 'findoc_signeds = %s' % findoc_signeds
            for findoc_signed in findoc_signeds:
                list_rule = [findoc_signed.id, eval('rule_obj.%s' % type_rule)]
                # проверяем есть ли уже такая комбинация (договор - тип оплаты)
                if group_rules_for_user.has_key(str(list_rule)):
                    spis_rule_id = group_rules_for_user[str(list_rule)]
                    spis_rule_id.append(rule_id)
                    group_rules_for_user.update({str(list_rule):spis_rule_id})
                else:
                    # если нету, тогда добавляем
                    group_rules_for_user.update({str(list_rule):[rule_id]})
        return group_rules_for_user

    @staticmethod
    def add_value_in_dict_service(dict_service, temp_key_word, cost):
        temp_key = temp_key_word
        if dict_service.has_key(temp_key):
            dict_service[temp_key] += [cost]
        else:
            dict_service[temp_key] = [cost]
        return dict_service

    class Meta:
        abstract = True


class Check(Document):
    valid = models.BooleanField(default=True, verbose_name=u"Фиктивный счет")
    class Meta:
        db_table = "document_check"

    @staticmethod
    def create_check(user_obj, group_rules_for_user, every_month, not_every_month_id_zakaz=[], advance_sum=0):
        try:
            print 'poshli na cheeck'
            now = datetime.datetime.now()
            profile_obj = Profile.objects.get(user=user_obj.id)
            if not profile_obj.create_invoice:
                return None
            bill_account = BillserviceAccount.objects.get(id=profile_obj.billing_account_id)
            now_start_month = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
            ready_documents = []
            print 'pered for'
            print group_rules_for_user
            for rule, spis_rule_id in sorted(group_rules_for_user.items()):
                print 'poshli na rules'
                print rule
                sum_all_service = 0
                dict_service = {}
                add_service_in_check = ''
                try:
                    rule = eval(rule)
                    findoc_signed = FinDocSigned.objects.get(id=rule[0])
                except Exception, e:
                    print 'error in create check = %s ' % e
                    print user_obj.id
                    continue
                for rule_id in spis_rule_id:
                    rule_obj = Rules_of_drawing_up_documents.objects.get(id=rule_id)
                    if rule_obj.type == 1:
                        if every_month:
                            zakazy_queryset_temp = Zakazy.objects.filter(Q(bill_account=bill_account) & Q(status_zakaza__id__in=[2, 4]) & \
                                                                    Q(service_type__id=rule_obj.service_type) & \
                                                                    (Q(date_deactivation=None) | Q(date_deactivation__gt=now_start_month)) & \
                                                                    Q(date_activation__lt=now_start_month) & (Q(date_end_test_period__lte=now) | Q(date_end_test_period=None)))
                        else:
                            zakazy_queryset_temp = Zakazy.objects.filter(id__in=not_every_month_id_zakaz, service_type=rule_obj.service_type)
                        zakazy_queryset = []
                        for zakaz_obj in zakazy_queryset_temp:
                            print 'findoc_signed =  %s' % findoc_signed.id
                            print 'test findoc, zakaz_id = %s' % zakaz_obj.id
                            findoc_sign_zakaz = FinDocSignedZakazy.objects.filter(fin_doc=findoc_signed, zakaz_id=zakaz_obj.id)
                            if findoc_sign_zakaz:
                                print 'est findoc'
                                zakazy_queryset.append(zakaz_obj)
                        for zakaz_obj in zakazy_queryset:
                            if zakaz_obj.connection_cost.cost > 0:
                                date_over_check_temp = zakaz_obj.date_activation + relativedelta(months=1)
                                date_over_check = datetime.datetime(date_over_check_temp.year, date_over_check_temp.month, 1, 0, 0, 0)
                                if now < date_over_check:
                                    sum_all_service += zakaz_obj.connection_cost.cost
                                    dict_service = Check.add_value_in_dict_service(dict_service, 'Подключение местного телефонного номера', zakaz_obj.connection_cost.cost)
                            if zakaz_obj.delivery:
                                date_over_check_temp = zakaz_obj.date_activation + relativedelta(months=1)
                                date_over_check = datetime.datetime(date_over_check_temp.year, date_over_check_temp.month, 1, 0, 0, 0)
                                if now < date_over_check:
                                    sum_all_service += (zakaz_obj.delivery.price_id.cost)
                                    dict_service = Check.add_value_in_dict_service(dict_service, 'Доставка оборудования', zakaz_obj.delivery.price_id.cost)
                            if not every_month:
                                # подсчитываем стоимость исходя из оставшегося количества дней до конца месяца
                                mday = float(calendar.mdays[datetime.date.today().month])
                                day = float(calendar.mdays[datetime.date.today().month] - datetime.datetime.now().day + 1)
                                cost_temp = float(zakaz_obj.cost) / float(mday) * float(day)
                                print zakaz_obj.cost, mday, day
                                print "cost_temp = %s" % cost_temp
                            else:
                                cost_temp = zakaz_obj.cost
                            # записываем стоимость заказа
                            cost = float('%.2f' % float(cost_temp))
                            # добавляем к общей стоимости счета
                            sum_all_service += cost
                            if rule_obj.name_service:
                                service_type = rule_obj.name_service.encode("utf-8")
                            else:
                                service_type = str(zakaz_obj.service_type)
                            # получаем дату начала и конца пользования услугой для оплаты
                            last_day = int(calendar.mdays[datetime.date.today().month])
                            date_end = datetime.datetime(now.year, now.month, last_day).date()
                            date_end = datetime.datetime.strftime(date_end, "%d.%m.%Y")
                            if not every_month:
                                date_start = datetime.datetime.strftime(now, "%d.%m.%Y")
                            else:
                                date_start = datetime.datetime(now.year, now.month, 1).date()
                                date_start = datetime.datetime.strftime(date_start, "%d.%m.%Y")
                            dict_service = Check.add_value_in_dict_service(dict_service, service_type + ' за период с ' + date_start + ' по ' + date_end, cost)
                    elif rule_obj.type == 2:
                        if advance_sum == 0:
                            if rule_obj.type_check == 1:
                                str_start_service = datetime.datetime.strftime(now_start_month - relativedelta(months=1), "%d.%m.%Y")
                                str_end_service = datetime.datetime.strftime(now_start_month - relativedelta(days=1), "%d.%m.%Y")
                            elif rule_obj.type_check == 2:
                                str_start_service = datetime.datetime.strftime(now_start_month, "%d.%m.%Y")
                                str_end_service = datetime.datetime.strftime(now_start_month + relativedelta(months=1) - relativedelta(days=1), "%d.%m.%Y")
                            sum_service = eval('bill_account.%s(bill_account.id)' % rule_obj.method_bill_acc)
                            sum_all_service += sum_service

                            dict_service = Check.add_value_in_dict_service(dict_service, rule_obj.name_service.encode('utf-8') + ' с ' + str_start_service + ' по ' + str_end_service, sum_service)
                        else:
                            sum_all_service += advance_sum
                            service_type = rule_obj.name_service
                            dict_service = Check.add_value_in_dict_service(dict_service, service_type.encode("utf-8"), advance_sum)

                if not dict_service:
                    continue
                print 'dict_service = %s' % dict_service
                for key in dict_service:
                    spis_cost = dict_service[key]
                    temp_spis_cost = list(set(spis_cost))
                    temp_spis_cost.sort()
                    spis_cost.sort()
                    for cost in temp_spis_cost:
                        count_service = spis_cost.count(cost)
                        add_service_in_check += """
                        <tr>
                        <th align="left">%(service_type)s</th>
                        <th>%(unit_of_measure)s</th>
                        <th>%(count_service)s</th>
                        <th>%(cost_for_one_service)s</th>
                        <th>%(summ_cost_service)s</th>
                        </tr>
                        """ % {
                                "service_type": key.decode('UTF-8'),
                                "unit_of_measure": u'шт',
                                "count_service": count_service,
                                "cost_for_one_service": cost,
                                "summ_cost_service": cost * count_service,
                                }

                findoc_template_obj = FinDocTemplate.objects.get(name='check')

                sum_all_service = '%.2f' % sum_all_service
                nds_temp = round(float(sum_all_service) / 1.18 * 0.18, 2)
                nds = '%.2f' % nds_temp
                from content.views import perewod
                sum_k_oplate = perewod(sum_all_service)

                if rule[1] == 1:
                    number_check = Check.get_next_number(Check, (now - relativedelta(months=1)).year)
                elif rule[1] == 2:
                    number_check = Check.get_next_number(Check, datetime.datetime.now().year)

                if every_month:
                    if rule_obj.type_check == 1:
                        date_check = datetime.datetime.strftime(now_start_month - relativedelta(days=1), "%d.%m.%Y")
                    elif rule_obj.type_check == 2:
                        date_check = datetime.datetime.strftime(now_start_month, "%d.%m.%Y")
                else:
                    date_check = datetime.datetime.strftime(now, "%d.%m.%Y")
                our_requisites = Profile.objects.get(id=15)
                text_document = findoc_template_obj.text % {
                                "profile.company_name" : profile_obj.get_company_name_or_family(),
                                "legal_adrress": profile_obj.get_legal_adrress(),
                                "inn_kpp": profile_obj.get_inn_kpp(),
                                "date_now": date_check,
                                "NDS_all": nds,
                                "summ_for_service_all": sum_all_service,
                                "id_from_check": "%s" % number_check,
                                "id_findoc": findoc_signed.id,
                                "sum_k_oplate": sum_k_oplate.decode('UTF-8'),
                                "count_service": count_service,
                                "add_service_in_check": add_service_in_check,

                                "our_requisites.inn": our_requisites.bank_address,
                                "our_requisites.kpp": our_requisites.kpp,
                                "our_requisites.rs": our_requisites.settlement_account,
                                "our_requisites.bank_name": our_requisites.bank_name,
                                "our_requisites.bik": our_requisites.bik,
                                "our_requisites.ks": our_requisites.correspondent_account,
                                "our_requisites.legal_form": our_requisites.legal_form,
                                "our_requisites.company_name": our_requisites.company_name,
                                "our_requisites.legal_adrress": our_requisites.get_legal_adrress(),
                              }
                if rule[1] == 1:
                    year, month = (now - relativedelta(months=1)).year, (now - relativedelta(months=1)).month
                elif rule[1] == 2:
                    year, month = now.year, now.month
                check_obj = Check.create_record(Check, user_obj, year, month, every_month, number_check, findoc_signed.findoc, rule[1], text_document)
                ready_documents.append(check_obj.id)
        except Exception, e:
            import os, sys
            log.add("Exception in create_check: '%s'" % e)
            exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.add("Exception in create_check: file:%s line:%s" % (fname, exc_tb.tb_lineno))
        return ready_documents


class Act(Document):
    class Meta:
        db_table = "document_act"

    @staticmethod
    def create_act(user_obj, group_rules_for_user):

        from data_centr.views import cost_dc
        from data_centr.models import Data_centr_payment

        now = datetime.datetime.now()
        profile_obj = Profile.objects.get(user=user_obj.id)
        bill_account = BillserviceAccount.objects.get(id=profile_obj.billing_account_id)
        now_start_month = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
        last_start_month = now_start_month - relativedelta(months=1)
        ready_documents = []
        for rule, spis_rule_id in group_rules_for_user.items():
            dict_service = {}
            sum_all_service = 0
            add_service_in_act = ''
            try:
                rule = eval(rule)
                findoc_signed = FinDocSigned.objects.get(id=rule[0])
            except Exception, e:
                print 'error in create act = %s ' % e
                print user_obj.id
                continue
            for rule_id in spis_rule_id:
                rule_obj = Rules_of_drawing_up_documents.objects.get(id=rule_id)
                if rule_obj.type == 1:
                    print 'rule 1'
                    zakazy_queryset_temp = Zakazy.objects.filter(Q(bill_account=bill_account) & Q(status_zakaza__in=[2, 3, 4, 5]) & \
                                                            Q(service_type=rule_obj.service_type) & \
                                                            ((Q(date_activation__lt=now_start_month) & Q(date_deactivation=None) & (Q(date_end_test_period__lt=now_start_month) | Q(date_end_test_period=None))) | \
                                                            (Q(date_activation__lt=last_start_month) & Q(date_deactivation__gte=now_start_month) & (Q(date_end_test_period__lt=last_start_month) | Q(date_end_test_period=None)))))
                    zakazy_queryset = []
                    date_start_last_month_temp = now - relativedelta(months=1)
                    date_start_last_month = datetime.datetime(date_start_last_month_temp.year, date_start_last_month_temp.month, 1, 0, 0, 0)
                    for zakaz_obj in zakazy_queryset_temp:
                        print 'findoc_signed =  %s' % findoc_signed.id
                        print 'test findoc, zakaz_id = %s' % zakaz_obj.id
                        if zakaz_obj.cost > 0:
                            findoc_sign_zakaz = FinDocSignedZakazy.objects.filter(fin_doc=findoc_signed, zakaz_id=zakaz_obj.id)
                            if findoc_sign_zakaz:
                                print '***da***'
                                zakazy_queryset.append(zakaz_obj)
                    date_start_now_month = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
                    date_end_act_temp = date_start_now_month - relativedelta(days=1)
                    date_end_act_temp = datetime.datetime(date_end_act_temp.year, date_end_act_temp.month, date_end_act_temp.day, 23, 59, 59)
                    date_end_act = datetime.datetime.strftime(date_end_act_temp, "%d.%m.%Y")
                    for zakaz_obj in zakazy_queryset:
                        print 'zakaz_obj = %s' % zakaz_obj.id
                        start_activation = zakaz_obj.date_end_test_period if zakaz_obj.date_end_test_period else zakaz_obj.date_activation
                        if start_activation < date_start_now_month:
                            if zakaz_obj.connection_cost.cost > 0:
                                date_over_act_temp = start_activation + relativedelta(months=2)
                                date_over_act = datetime.datetime(date_over_act_temp.year, date_over_act_temp.month, 1, 0, 0, 0)
                                if now < date_over_act:
                                    sum_all_service += zakaz_obj.connection_cost.cost
                                    dict_service = Act.add_value_in_dict_service(dict_service, 'Подключение местного телефонного номера', zakaz_obj.connection_cost.cost)
                        if start_activation < date_start_now_month:
                            if zakaz_obj.delivery:
                                date_over_act_temp = start_activation + relativedelta(months=2)
                                date_over_act = datetime.datetime(date_over_act_temp.year, date_over_act_temp.month, 1, 0, 0, 0)
                                if now < date_over_act:
                                    sum_all_service += zakaz_obj.delivery.price_id.cost
                                    dict_service = Act.add_value_in_dict_service(dict_service, 'Доставка оборудования', zakaz_obj.delivery.price_id.cost)
                        cost_temp = float(zakaz_obj.cost)
                        # если заказ был активирован в предыдущем месяце
                        if start_activation > date_start_last_month:
                            # принимаем за дату начала списания дату заказа
                            # дата начала = дата заказа
                            date_start_act_temp = start_activation
                            date_start_act = datetime.datetime.strftime(date_start_act_temp, "%d.%m.%Y")
                            # узнаем сколько в месяце дней
                            mday_act_temp = date_start_now_month - relativedelta(days=1) - date_start_last_month
                            mday_act = mday_act_temp.days + 1
                            # получаем количество дней, за которое пользователь оплатил
                            if zakaz_obj.date_deactivation:
                                day_act_temp = zakaz_obj.date_deactivation - date_start_act_temp
                            else:
                                day_act_temp = date_end_act_temp - date_start_act_temp
                            day_act = day_act_temp.days + 1
                            # высчитываем стоимость заказа за предыдущий месяц
                            cost_temp = float(cost_temp) / float(mday_act) * float(day_act)
                        else:
                            if zakaz_obj.date_deactivation:
                                if zakaz_obj.date_deactivation < date_end_act_temp:
                                    # узнаем сколько в месяце дней
                                    mday_act_temp = date_start_now_month - relativedelta(days=1) - date_start_last_month
                                    mday_act = mday_act_temp.days + 1
                                    day_act_temp = start_activation - date_start_last_month
                                    day_act = day_act_temp.days + 1
                                    # высчитываем стоимость заказа за предыдущий месяц
                                    cost_temp = float(cost_temp) / float(mday_act) * float(day_act)

                            # если заказ давно активирован, то берем первое число предыдущего месяца
                            date_start_act = datetime.datetime.strftime(date_start_last_month, "%d.%m.%Y")
                        sum_all_service += cost_temp
                        cost = '%.2f' % cost_temp
                        service_type = str(zakaz_obj.service_type)
                        if zakaz_obj.date_deactivation:
                            print 'tut 100 pro'
                            if zakaz_obj.date_deactivation <= date_start_now_month:
                                if zakaz_obj.date_deactivation == date_start_now_month:
                                    date_deactivation_for_act_temp = date_end_act_temp
                                else:
                                    date_deactivation_for_act_temp = zakaz_obj.date_deactivation
                                date_deactivation_for_act = datetime.datetime.strftime(date_deactivation_for_act_temp, "%d.%m.%Y")
                                dict_service = Act.add_value_in_dict_service(dict_service, service_type + ' за период с ' + date_start_act + ' по ' + date_deactivation_for_act, float(cost))
                            else:
                                dict_service = Act.add_value_in_dict_service(dict_service, service_type + ' за период с ' + date_start_act + ' по ' + date_end_act, float(cost))
                        else:
                            dict_service = Act.add_value_in_dict_service(dict_service, service_type + ' за период с ' + date_start_act + ' по ' + date_end_act, float(cost))
                elif rule_obj.type == 2:
                    print 'rule 2'
                    if rule_obj.type_act == 1:
                        str_start_service = datetime.datetime.strftime(now_start_month - relativedelta(months=1), "%d.%m.%Y")
                        str_end_service = datetime.datetime.strftime(now_start_month - relativedelta(days=1), "%d.%m.%Y")
                    elif rule_obj.type_act == 2:
                        str_start_service = datetime.datetime.strftime(now_start_month, "%d.%m.%Y")
                        str_end_service = datetime.datetime.strftime(now_start_month + relativedelta(months=1) - relativedelta(days=1), "%d.%m.%Y")
                    sum_service = eval('bill_account.%s(bill_account.id)' % rule_obj.method_bill_acc)
                    sum_all_service += sum_service

                    dict_service = Act.add_value_in_dict_service(dict_service, rule_obj.name_service.encode('utf-8') + ' с ' + str_start_service + ' по ' + str_end_service, sum_service)
            print 'dict_service = %s' % dict_service
            if not dict_service:
                continue
            for key in dict_service:
                spis_cost = dict_service[key]
                temp_spis_cost = list(set(spis_cost))
                temp_spis_cost.sort()
                spis_cost.sort()
                for cost in temp_spis_cost:
                    count_service = spis_cost.count(cost)
                    add_service_in_act += """
                    <tr>
                    <th align="left">%(service_type)s</th>
                    <th>%(count_service)s</th>
                    <th>%(unit_of_measure)s</th>
                    <th>%(cost_for_one_service)s</th>
                    <th>%(summ_cost_service)s</th>
                    </tr>
                    """ % {
                            "service_type": key.decode('utf-8'),
                            "count_service": count_service,
                            "unit_of_measure": u'шт',
                            "cost_for_one_service": '%.2f' % (cost / 1.18),
                            "summ_cost_service": '%.2f' % ((cost / 1.18) * count_service),
                          }
            findoc_template_obj = FinDocTemplate.objects.get(name='act')
            sum_all_service = '%.2f' % sum_all_service
            nds_temp = round(float(sum_all_service) / 1.18 * 0.18, 2)
            nds = '%.2f' % nds_temp
            summ_for_service_minus_NDS_temp = float(sum_all_service) / 1.18
            summ_for_service_minus_NDS = '%.2f' % summ_for_service_minus_NDS_temp

            from content.views import perewod
            sum_k_oplate = perewod(sum_all_service)
            number_act = Act.get_next_number(Act, (now - relativedelta(months=1)).year)

            if rule_obj.type_act == 1:
                date_act_temp = now_start_month - relativedelta(days=1)
                date_act = datetime.datetime.strftime(now_start_month - relativedelta(days=1), "%d.%m.%Y")
            elif rule_obj.type_act == 2:
                date_act_temp = now_start_month
                date_act = datetime.datetime.strftime(now_start_month, "%d.%m.%Y")

            our_requisites = Profile.objects.get(id=15)
            text_profile = u'%s, %s' % (profile_obj.get_company_name_or_family(), profile_obj.main_billing_account_id()) if not profile_obj.is_juridical else u'%s' % profile_obj.get_company_name_or_family()
            text_document = findoc_template_obj.text % {
                                    "profile.company_name" : text_profile,
                                    "date_now": date_act,
                                    "NDS_all": nds,
                                    "summ_for_service_minus_NDS": summ_for_service_minus_NDS,
                                    "summ_for_service_all": sum_all_service,
                                    "id_from_check": "%s" % number_act,
                                    "id_findoc": findoc_signed.id,
                                    "sum_k_oplate": str(sum_k_oplate).decode('utf-8'),
                                    "add_service_in_act": add_service_in_act,

                                    "our_requisites.legal_form": our_requisites.legal_form,
                                    "our_requisites.company_name": our_requisites.company_name,
                                    "our_requisites.legal_adrress": our_requisites.get_legal_adrress(),
                                  }
            year, month = (now - relativedelta(months=1)).year, (now - relativedelta(months=1)).month
            act_obj = Act.create_record(Act, user_obj, year, month, True, number_act, findoc_signed.findoc, rule[1], text_document)
            ready_documents.append(act_obj.id)
        return ready_documents

    @staticmethod
    def create_act_hotspot(user_obj):
        from content.views import perewod
        now = datetime.datetime.now()
        findoc_obj = FinDoc.objects.get(id=37)
        number_act = Act.get_next_number(Act, (now - relativedelta(months=1)).year)
        findoc_template_obj = FinDocTemplate.objects.get(name='act_hotspot')
        profile_obj = Profile.objects.get(user=user_obj.id)
        bill_account = BillserviceAccount.objects.get(id=profile_obj.billing_account_id)
        text_profile = u'%s' % (profile_obj.main_billing_account_id())
        now_start_month = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
        date_act = datetime.datetime.strftime(now_start_month - relativedelta(days=1), "%d.%m.%Y")
        our_requisites = Profile.objects.get(id=15)
        str_start_service = datetime.datetime.strftime(now_start_month - relativedelta(months=1), "%d.%m.%Y")
        str_end_service = datetime.datetime.strftime(now_start_month - relativedelta(days=1), "%d.%m.%Y")
        cost_temp = bill_account.get_sum_hotspot(all_summ=True)
        cost_for_word = '%.2f' % cost_temp
        cost = float(cost_for_word)
        nds_temp = round(float(cost) / 1.18 * 0.18, 2)
        nds = '%.2f' % nds_temp
        cost_without_nds_temp = float(cost) / 1.18
        cost_without_nds = '%.2f' % cost_without_nds_temp
        sum_k_oplate = perewod(cost_for_word)
        add_service_in_act = """
        <tr>
        <th align="left">%(service_type)s</th>
        <th>%(count_service)s</th>
        <th>%(unit_of_measure)s</th>
        <th>%(cost_for_one_service)s</th>
        <th>%(summ_cost_service)s</th>
        </tr>
        """ % {
                "service_type": u'Доступ в интернет за период с %s по %s' % (str_start_service, str_end_service),
                "count_service": 1,
                "unit_of_measure": u'шт',
                "cost_for_one_service": '%.2f' % (cost / 1.18),
                "summ_cost_service": '%.2f' % (cost / 1.18),
              }
        text_document = findoc_template_obj.text % {
                        "profile.company_name" : text_profile,
                        "date_now": date_act,
                        "NDS_all": nds,
                        "summ_for_service_minus_NDS": cost_without_nds,
                        "summ_for_service_all": cost,
                        "id_from_check": "%s" % number_act,
                        "sum_k_oplate": str(sum_k_oplate).decode('utf-8'),
                        "add_service_in_act": add_service_in_act,
                        "our_requisites.legal_form": our_requisites.legal_form,
                        "our_requisites.company_name": our_requisites.company_name,
                        "our_requisites.legal_adrress": our_requisites.get_legal_adrress(),
                      }
        year, month = (now - relativedelta(months=1)).year, (now - relativedelta(months=1)).month
        act_obj = Act.create_record(Act, user_obj, year, month, True, number_act, findoc_obj, 1, text_document)
        return act_obj


class Invoice(Document):
    class Meta:
        db_table = "document_invoice"

    @staticmethod
    def create_invoice(user_obj, group_rules_for_user):
        from data_centr.views import cost_dc
        from data_centr.models import Data_centr_payment

        now = datetime.datetime.now()
        profile_obj = Profile.objects.get(user=user_obj.id)
        bill_account = BillserviceAccount.objects.get(id=profile_obj.billing_account_id)
        now_start_month = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
        last_start_month = now_start_month - relativedelta(months=1)
        ready_documents = []
        for rule, spis_rule_id in group_rules_for_user.items():
            try:
                rule = eval(rule)
                findoc_signed = FinDocSigned.objects.get(id=rule[0])
            except Exception, e:
                print 'error in create check = %s ' % e
                print user_obj.id
                continue
            dict_service = {}
            sum_all_service = 0
            add_service_in_invoice = ''

            date_start_last_month_temp = now - relativedelta(months=1)
            date_start_last_month = datetime.datetime(date_start_last_month_temp.year, date_start_last_month_temp.month, 1, 0, 0, 0)
            date_start_month_now = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
            date_end_invoice_temp = date_start_month_now - relativedelta(days=1)
            date_end_invoice_temp = datetime.datetime(date_end_invoice_temp.year, date_end_invoice_temp.month, date_end_invoice_temp.day, 23, 59, 59)
            numb_month = date_end_invoice_temp.month
            dict_month = {1:u'января', 2:u'февраля', 3:u'марта', 4:u'апреля', 5:u'мая', 6:u'июня', \
                          7:u'июля', 8:u'августа', 9:u'сентября', 10:u'октября', 11:u'ноября', 12:u'декабря'}
            month = dict_month[numb_month]
            date_end_invoice = datetime.datetime.strftime(date_end_invoice_temp, "%d " + month.encode("utf-8") + " %Y")

            for rule_id in spis_rule_id:
                rule_obj = Rules_of_drawing_up_documents.objects.get(id=rule_id)
                if rule_obj.type == 1:
                    zakazy_queryset_temp = Zakazy.objects.filter(Q(bill_account=bill_account) & Q(status_zakaza__in=[2, 3, 4, 5]) & \
                                                            Q(service_type=rule_obj.service_type) & \
                                                            ((Q(date_activation__lt=now_start_month) & Q(date_deactivation=None) & (Q(date_end_test_period__lt=now_start_month) | Q(date_end_test_period=None))) | \
                                                            (Q(date_activation__lt=last_start_month) & Q(date_deactivation__gte=now_start_month) & (Q(date_end_test_period__lt=last_start_month) | Q(date_end_test_period=None)))))
                    zakazy_queryset = []
                    for zakaz_obj in zakazy_queryset_temp:
                        print 'findoc_signed =  %s' % findoc_signed.id
                        print 'test findoc, zakaz_id = %s' % zakaz_obj.id
                        if zakaz_obj.cost > 0:
                            findoc_sign_zakaz = FinDocSignedZakazy.objects.filter(fin_doc=findoc_signed, zakaz_id=zakaz_obj.id)
                            if findoc_sign_zakaz:
                                zakazy_queryset.append(zakaz_obj)
                    for zakaz_obj in zakazy_queryset:
                        start_activation = zakaz_obj.date_end_test_period if zakaz_obj.date_end_test_period else zakaz_obj.date_activation
                        if start_activation < date_start_month_now:
                            if zakaz_obj.connection_cost.cost > 0:
                                date_over_invoice_temp = start_activation + relativedelta(months=2)
                                date_over_invoice = datetime.datetime(date_over_invoice_temp.year, date_over_invoice_temp.month, 1, 0, 0, 0)
                                if now < date_over_invoice:
                                    sum_all_service += zakaz_obj.connection_cost.cost
                                    dict_service = Invoice.add_value_in_dict_service(dict_service, 'Подключение местного телефонного номера', zakaz_obj.connection_cost.cost)
                        if start_activation < date_start_month_now:
                            if zakaz_obj.delivery:
                                date_over_invoice_temp = start_activation + relativedelta(months=2)
                                date_over_invoice = datetime.datetime(date_over_invoice_temp.year, date_over_invoice_temp.month, 1, 0, 0, 0)
                                if now < date_over_invoice:
                                    sum_all_service += zakaz_obj.delivery.price_id.cost
                                    dict_service = Invoice.add_value_in_dict_service(dict_service, 'Доставка оборудования', zakaz_obj.delivery.price_id.cost)


                        cost_temp = float(zakaz_obj.cost)
                        if start_activation > date_start_last_month:
                            date_start_invoice_temp = start_activation
                            date_start_invoice = datetime.datetime.strftime(date_start_invoice_temp, "%d.%m.%Y")

                            mday_invoice_temp = date_start_month_now - relativedelta(days=1) - date_start_last_month
                            mday_invoice = mday_invoice_temp.days + 1

                            # получаем количество дней, за которое пользователь оплатил
                            if zakaz_obj.date_deactivation:
                                day_invoice_temp = zakaz_obj.date_deactivation - date_start_invoice_temp
                            else:
                                day_invoice_temp = date_end_invoice_temp - date_start_invoice_temp
                            day_invoice = day_invoice_temp.days + 1
                            # высчитываем стоимость заказа за предыдущий месяц
                            cost_temp = float(cost_temp) / float(mday_invoice) * float(day_invoice)
                        else:
                            if zakaz_obj.date_deactivation:
                                if zakaz_obj.date_deactivation < date_end_invoice_temp:
                                    # узнаем сколько в месяце дней
                                    mday_act_temp = date_start_month_now - relativedelta(days=1) - date_start_last_month
                                    mday_act = mday_act_temp.days + 1
                                    day_act_temp = zakaz_obj.date_deactivation - date_start_last_month
                                    day_act = day_act_temp.days + 1
                                    # высчитываем стоимость заказа за предыдущий месяц
                                    cost_temp = float(cost_temp) / float(mday_act) * float(day_act)
                            date_start_invoice = datetime.datetime.strftime(date_start_last_month, "%d.%m.%Y")
                        sum_all_service += cost_temp
                        cost = '%.2f' % cost_temp
                        service_type = str(zakaz_obj.service_type)
                        if zakaz_obj.date_deactivation:
                            if zakaz_obj.date_deactivation <= date_start_month_now:
                                if zakaz_obj.date_deactivation == date_start_month_now:
                                    date_deactivation_for_invoice_temp = date_end_invoice_temp
                                else:
                                    date_deactivation_for_invoice_temp = zakaz_obj.date_deactivation
                                date_deactivation_for_invoice = datetime.datetime.strftime(date_deactivation_for_invoice_temp, "%d.%m.%Y")
                                dict_service = Invoice.add_value_in_dict_service(dict_service, service_type + ' за период с ' + date_start_invoice + ' по ' + date_deactivation_for_invoice, float(cost))
                            else:
                                dict_service = Invoice.add_value_in_dict_service(dict_service, service_type + ' за период с ' + date_start_invoice + ' по ' + date_end_invoice, float(cost))
                        else:
                            dict_service = Invoice.add_value_in_dict_service(dict_service, service_type + ' за период с ' + date_start_invoice + ' по ' + date_end_invoice, float(cost))
                elif rule_obj.type == 2:
                    if rule_obj.type_invoice == 1:
                        str_start_service = datetime.datetime.strftime(now_start_month - relativedelta(months=1), "%d.%m.%Y")
                        str_end_service = datetime.datetime.strftime(now_start_month - relativedelta(days=1), "%d.%m.%Y")
                    elif rule_obj.type_invoice == 2:
                        str_start_service = datetime.datetime.strftime(now_start_month, "%d.%m.%Y")
                        str_end_service = datetime.datetime.strftime(now_start_month + relativedelta(months=1) - relativedelta(days=1), "%d.%m.%Y")
                    sum_service = eval('bill_account.%s(bill_account.id)' % rule_obj.method_bill_acc)
                    sum_all_service += sum_service

                    dict_service = Invoice.add_value_in_dict_service(dict_service, rule_obj.name_service.encode('utf-8') + ' с ' + str_start_service + ' по ' + str_end_service, sum_service)

            if not dict_service:
                continue
            for key in dict_service:
                spis_cost = dict_service[key]
                temp_spis_cost = list(set(spis_cost))
                temp_spis_cost.sort()
                spis_cost.sort()
                for cost in temp_spis_cost:
                    count_service = spis_cost.count(cost)
                    cost = float(cost) * count_service
                    add_service_in_invoice += """
                    <tr>
                        <td style="text-align: left; vertical-align: middle; ">
                            <font size="1">%(service_type)s</font></td>
                        <td style="text-align: center; vertical-align: middle; ">
                            <font size="1">---</font></td>
                        <td style="text-align: center; vertical-align: middle; ">
                            <font size="1">---</font></td>
                        <td style="text-align: right; vertical-align: middle; ">
                            <font size="1">---</font></td>
                        <td style="text-align: right; vertical-align: middle; ">
                            <font size="1">---</font></td>
                        <td style="text-align: right; vertical-align: middle; ">
                            <font size="1">%(cost_of_the_goods_without_nds)s</font></td>
                        <td style="text-align: center; vertical-align: middle; ">
                            <font size="1">%(without_an_excise)s</font></td>
                        <td style="text-align: center; vertical-align: middle; ">
                            <font size="1">18%%</font></td>
                        <td style="text-align: right; vertical-align: middle; ">
                            <font size="1">%(nds)s</font></td>
                        <td style="text-align: right; vertical-align: middle; ">
                            <font size="1">%(cost_of_the_goods_with_nds)s</font></td>
                        <td style="text-align: center; vertical-align: middle; ">
                            <font size="1">---</font></td>
                        <td style="text-align: center; vertical-align: middle; ">
                            <font size="1">---</font></td>
                        <td style="text-align: center; vertical-align: middle; ">
                            <font size="1">---</font></td>
                    </tr>
                    """ % {
                        "service_type": str(key).decode('utf-8'),
                        "cost_of_the_goods_without_nds": '%.2f' % (cost / 1.18),
                        "without_an_excise": u'без акциза',
                        "nds": '%.2f' % (cost / 1.18 * 0.18),
                        "cost_of_the_goods_with_nds": cost,
                        }

            findoc_template_obj = FinDocTemplate.objects.get(name='invoice')
            nds_temp = sum_all_service / 1.18 * 0.18
            nds_all = '%.2f' % nds_temp
            summ_for_service_all = '%.2f' % sum_all_service
            summ_cost_of_the_goods_without_nds = '%.2f' % (sum_all_service / 1.18)

            number_invoice = Invoice.get_next_number(Invoice, (now - relativedelta(months=1)).year)

            our_requisites = Profile.objects.get(id=15)
            text_profile = u'%s, %s' % (profile_obj.get_company_name_or_family(), profile_obj.main_billing_account_id()) if not profile_obj.is_juridical else u'%s' % profile_obj.get_company_name_or_family()
            text_document = findoc_template_obj.text % {
                                           "add_service_in_invoice": add_service_in_invoice,
                                           "number_invoice": '%s' % number_invoice,
                                           "date_invoice": date_end_invoice.decode("utf-8"),
                                           "profile.company_name": text_profile,
                                           "address": profile_obj.get_legal_adrress(),
                                           "inn_kpp": profile_obj.get_inn_kpp(),
                                           "summ_cost_of_the_goods_without_nds": summ_cost_of_the_goods_without_nds,
                                           "nds_all": nds_all,
                                           "summ_for_service_all": summ_for_service_all,

                                           "our_requisites.legal_form": our_requisites.legal_form,
                                           "our_requisites.company_name": our_requisites.company_name,
                                           "our_requisites.legal_adrress": our_requisites.get_legal_adrress(),
                                           "our_requisites.inn": our_requisites.bank_address,
                                           "our_requisites.kpp": our_requisites.kpp,
                                           }
            year, month = (now - relativedelta(months=1)).year, (now - relativedelta(months=1)).month
            invoice_obj = Invoice.create_record(Invoice, user_obj, year, month, True, number_invoice, findoc_signed.findoc, rule[1], text_document)
            ready_documents.append(invoice_obj.id)
        return ready_documents

    @staticmethod
    def create_invoice_hotspot(user_obj):
        now = datetime.datetime.now()
        findoc_obj = FinDoc.objects.get(id=37)
        number_invoice = Invoice.get_next_number(Invoice, (now - relativedelta(months=1)).year)
        findoc_template_obj = FinDocTemplate.objects.get(name='invoice')
        profile_obj = Profile.objects.get(user=user_obj.id)
        bill_account = BillserviceAccount.objects.get(id=profile_obj.billing_account_id)
        our_requisites = Profile.objects.get(id=15)
        text_profile = u'%s' % (profile_obj.main_billing_account_id())
        now_start_month = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
        str_start_service = datetime.datetime.strftime(now_start_month - relativedelta(months=1), "%d.%m.%Y")
        str_end_service = datetime.datetime.strftime(now_start_month - relativedelta(days=1), "%d.%m.%Y")
        cost_temp = bill_account.get_sum_hotspot(all_summ=True)
        cost_for_word = '%.2f' % cost_temp
        cost = float(cost_for_word)
        nds_temp = round(float(cost) / 1.18 * 0.18, 2)
        nds = '%.2f' % nds_temp
        cost_without_nds_temp = float(cost) / 1.18
        cost_without_nds = '%.2f' % cost_without_nds_temp
        date_end_invoice = datetime.datetime.strftime(now_start_month - relativedelta(days=1), "%d.%m.%Y")
        add_service_in_invoice = """
                    <tr>
                        <td style="text-align: left; vertical-align: middle; ">
                            <font size="1">%(service_type)s</font></td>
                        <td style="text-align: center; vertical-align: middle; ">
                            <font size="1">---</font></td>
                        <td style="text-align: center; vertical-align: middle; ">
                            <font size="1">---</font></td>
                        <td style="text-align: right; vertical-align: middle; ">
                            <font size="1">---</font></td>
                        <td style="text-align: right; vertical-align: middle; ">
                            <font size="1">---</font></td>
                        <td style="text-align: right; vertical-align: middle; ">
                            <font size="1">%(cost_of_the_goods_without_nds)s</font></td>
                        <td style="text-align: center; vertical-align: middle; ">
                            <font size="1">%(without_an_excise)s</font></td>
                        <td style="text-align: center; vertical-align: middle; ">
                            <font size="1">18%%</font></td>
                        <td style="text-align: right; vertical-align: middle; ">
                            <font size="1">%(nds)s</font></td>
                        <td style="text-align: right; vertical-align: middle; ">
                            <font size="1">%(cost_of_the_goods_with_nds)s</font></td>
                        <td style="text-align: center; vertical-align: middle; ">
                            <font size="1">---</font></td>
                        <td style="text-align: center; vertical-align: middle; ">
                            <font size="1">---</font></td>
                        <td style="text-align: center; vertical-align: middle; ">
                            <font size="1">---</font></td>
                    </tr>
                    """ % {
                        "service_type": u'Доступ в интернет за период с %s по %s' % (str_start_service, str_end_service),
                        "cost_of_the_goods_without_nds": '%.2f' % (cost / 1.18),
                        "without_an_excise": u'без акциза',
                        "nds": '%.2f' % (cost / 1.18 * 0.18),
                        "cost_of_the_goods_with_nds": cost,
                        }
        text_document = findoc_template_obj.text % {
                               "add_service_in_invoice": add_service_in_invoice,
                               "number_invoice": '%s' % number_invoice,
                               "date_invoice": date_end_invoice.decode("utf-8"),
                               "profile.company_name": text_profile,
                               "address": profile_obj.get_legal_adrress(),
                               "inn_kpp": profile_obj.get_inn_kpp(),
                               "summ_cost_of_the_goods_without_nds": cost_without_nds,
                               "nds_all": nds,
                               "summ_for_service_all": cost,
                               "our_requisites.legal_form": our_requisites.legal_form,
                               "our_requisites.company_name": our_requisites.company_name,
                               "our_requisites.legal_adrress": our_requisites.get_legal_adrress(),
                               "our_requisites.inn": our_requisites.bank_address,
                               "our_requisites.kpp": our_requisites.kpp,
                               }

        year, month = (now - relativedelta(months=1)).year, (now - relativedelta(months=1)).month
        invoice_obj = Invoice.create_record(Invoice, user_obj, year, month, True, number_invoice, findoc_obj, 1, text_document)
        return invoice_obj


class Download_documents(models.Model):
    class Meta:
        verbose_name_plural = u"Скачать акты и сф одним архивом"
        managed = False


class Download_checks(models.Model):
    class Meta:
        verbose_name_plural = u"Скачать счета одним архивом"
        managed = False

class Print_act(models.Model):
    class Meta:
        verbose_name_plural = u"Просмотр акта приемки/передачи"
        managed = False
