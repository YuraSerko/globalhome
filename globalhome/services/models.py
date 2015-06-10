# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from content.models import BaseContent
from findocs.models import FinDoc
from prices.models import Price
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from lib.utils import get_now
from decimal import Decimal
from services.consts import PACKET_APPLICATION_CHOICES, PACKET_CONNECTING, PACKET_DISCONNECTING
import datetime
#from services.functional_registry import ServicesFunctionalRegistry
import log
from lib.models import ParamsModel
from django.conf import settings
from findocs.models import FinDocSignApplication,FinDoc
from django.core.mail import EmailMultiAlternatives
import datetime, calendar
from django.db import connections, transaction

class SPDescriptionTemplate(BaseContent):
    "Шаблон текста услуги"
    class Meta:
        db_table = "services_templates"
        verbose_name = _(u"Service template")
        verbose_name_plural = _(u"Services templates")

class ServiceFunctional(ParamsModel):
    "Функционал пакета услуг"
    name = models.CharField(max_length=255, verbose_name=_(u"Functional name"))
    slug = models.SlugField(blank=False, null=False, unique=True)
    module = models.CharField(max_length=255, verbose_name=_(u"Python module name"))

    def __unicode__(self):
        return self.name

    def get_functional(self):
        "Возвращает импортированный из модуля класс функционала этого функционала"
        if self.module:
            try:
                exec "from %s import FUNCTIONAL_CLASS" % self.module
            except Exception, e:
                log.add("ServiceFunctional(%s) get_functional import error: %s" % (self.slug, e))
                return None, e
            else:
                return FUNCTIONAL_CLASS, None #@UndefinedVariable
        else:
            return None, None

    class Meta:
        ordering = ("name",)
        db_table = "services_functionals"
        verbose_name = _(u"Service functional")
        verbose_name_plural = _(u"Services functionals")

class AvailableService(models.Model):
    "Доступная услуга"
    name = models.CharField(max_length=255, verbose_name=_(u"Available service name"))
    slug = models.SlugField(blank=False, verbose_name=_(u"Slug"))
    functional = models.ForeignKey(ServiceFunctional, verbose_name=_(u"Service functional"), related_name="+")

    connect_price = models.ForeignKey(Price, verbose_name=_(u"Connect price"), blank=True, null=True, related_name="+")
    abon_price = models.ForeignKey(Price, verbose_name=_(u"License fee"), blank=True, null=True, related_name="+")

    onetime_document = models.ForeignKey(FinDoc, verbose_name=_(u"One-time document"), blank=True, null=True, related_name="+",
        help_text=_(u"This document user will sign only one time"))
    reusable_document = models.ForeignKey(FinDoc, verbose_name=_(u"Reusable document"), blank=True, null=True, related_name="+",
        help_text=_(u"This document user will sign every time"))
    cancel_document = models.ForeignKey(FinDoc, verbose_name=_(u"Cancel document"), blank=True, null=True, related_name="+",
        help_text=_(u"This document user will sign when canceling service"))

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        db_table = "services_available"
        verbose_name = _(u"Available service")
        verbose_name_plural = _(u"Available services")

class BalanceException(Exception):
    pass

class AvailableServicePacket(ParamsModel):
    "Доступный пакет услуг"
    is_published = models.BooleanField(default=True, verbose_name=_(u"Is published"))
    name = models.CharField(max_length=255, verbose_name=_(u"Name"))
    display_name = models.CharField(max_length=255, verbose_name=_(u"Display name"), blank=True, null=True)
    slug = models.SlugField(blank=False, null=False, unique=True)
    services = models.ManyToManyField(AvailableService, verbose_name=_(u"Services in this packet"))
    template = models.ForeignKey(SPDescriptionTemplate, verbose_name=_(u"Text template"), related_name="+")
    short_template = models.ForeignKey(SPDescriptionTemplate, verbose_name=_(u"Short text template"), blank=True, null=True, related_name="+")

    def __unicode__(self):
        return self.name

    def functionals_call(self, func_name, *args, **kwargs):
        "Вызывает метод с переданным именем для функционала каждой услуги"
        result = []
        also_names = kwargs.pop("also_services", False)
        if also_names:
            services = []
        for service in self.services.all():
            functional = service.functional
            f_class, exc = functional.get_functional() #@UnusedVariable
            m = getattr(f_class, func_name)
            if also_names:
                services.append(service)
            result.append(m(functional, self, *args, **kwargs))
        if also_names:
            return result, services
        return result

    def get_connect_price(self):
        "Возвращает цену подключения этого пакета услуг"
        result = Decimal(0)
        for service in self.services.all():
            if service.connect_price:
                result += service.connect_price.value
            if service.abon_price:
                all_day = calendar.mdays[datetime.date.today().month]
                ost = all_day - datetime.datetime.now().day + 1
                result += service.abon_price.value * ost / all_day
        return result

    @staticmethod
    def connect(slug, user, by=None, no_documents=False, no_balance_check=False, params={}): #@deprecated: Это не использовать!!!
        "Пытается подключить пакет услуг с указанным слагом указанному пользователю"
        asp = AvailableServicePacket.objects.get(slug=slug)

        if not no_balance_check:
            # проверим на наличие средств у пользователя
            if user.get_profile().get_balance() + user.get_profile().get_credit() < asp.get_connect_price():
                raise AvailableServicePacket.BalanceException()

        app = ServicePacketApplication(
            packet=asp,
            application_type=PACKET_CONNECTING,
            assigned_to=user,
            assigned_by=by,
        )

        app.pickle_params(params)

        # уведомим функционалы о том, что заявка создана
        app.notify_created(no_documents)

        app.save()

        # создадим договоры, если нужно
        has_documents = False
        if not no_documents:
            # все же создаем договоры
            # сохраним в параметрах документа список с 1 элементом - id заявки
            # каждый созданный документ добавим в app.wait_documents и app.save()

            for service in asp.services.all():
                
                docapp = None
                if service.onetime_document:
                    # проверить, не подписан ли он уже
                    if not service.onetime_document.get_signed(user):
                        docapp = service.onetime_document.create_from_sp_app(user, app, by=by, params=params, user_can_cancel=True)
                        has_documents = True


                if service.reusable_document:
                    print '1-e doc'
                    print service.reusable_document.id
                    p2 = params.copy()
                    if service.reusable_document.id==3:
                        print 'sozdau'
                        print p2
                        t=FinDoc.objects.get(slug="act_for_numb")
                        t.new_doc(user,None,"",True,None)
                        t.save
                        print 'sozdal'
                        pass



                    if docapp:
                        p2["onetime_document_application_id"] = docapp.id
                    service.reusable_document.create_from_sp_app(user, app, by=by, params=p2, user_can_cancel=True)
                    has_documents = True


        # если не создали документы, то заявку можно прямо сейчас уже пытаться оформлять
        if not has_documents:
            app.go_next()

        else:
            app.update_ready()
        return app

    class Meta:
        ordering = ("name",)
        db_table = "services_available_packets"
        verbose_name = _(u"Available service packet")
        verbose_name_plural = _(u"Available services packets")

class ServicePacketApplication(ParamsModel):
    "Заявка на добавление/удаление пакета"
    packet = models.ForeignKey(AvailableServicePacket, verbose_name=_(u"Available service packet"), related_name="+")
    application_type = models.IntegerField(choices=PACKET_APPLICATION_CHOICES, verbose_name=_(u"Application type"))
    assigned_to = models.ForeignKey(User, verbose_name=_(u"Assigned to"), related_name="+")
    assigned_at = models.DateTimeField(default=get_now, verbose_name=_(u"Assigned at"))
    assigned_by = models.ForeignKey(User, verbose_name=_(u"Assigned by"), related_name="+", blank=True, null=True)

    detach_packet = models.ForeignKey("AssignedServicePacket", editable=False, related_name="+", blank=True, null=True)

    from findocs.models import FinDocSignApplication
    wait_documents = models.ManyToManyField(FinDocSignApplication, related_name="detach_packet_wait", editable=False)

    def application_type_display(self):
        "Возвращает отображаемое значение типа заявки"
        for t in PACKET_APPLICATION_CHOICES:
            if t[0] == self.application_type:
                return t[1]

    def extra_text(self):
        try:
            return ", ".join(self.packet.functionals_call("AdminServicePacketApplicationExtraText", self))
        except Exception, e:
            return "Exception %s: %s" % (type(e), unicode(e))
    extra_text.short_description = _(u"Extra text")

    @staticmethod
    def filter_by_params(params, user=None, packet=None, packet_slug=""):
        "Фильтрует назначенные пакеты услуг по указанным параметрам, пользователю и пакету. Возвращает список из подошедших назначенных пакетов услуг"
        result = []
        all = ServicePacketApplication.objects.all()
        if user:
            all = all.filter(assigned_to=user)
        if packet:
            all = all.filter(packet=packet)
        else:
            if packet_slug:
                packet = AvailableServicePacket.objects.get(slug=packet_slug)
                all = all.filter(packet=packet)
        for app in all:
            app_params = app.unpickle_params()
            not_match = False
            for key in params:
                if app_params.has_key(key):
                    if app_params[key] != params[key]:
                        not_match = True
                        break
                else:
                    not_match = True
                    break
            if not not_match:
                result.append(app)
        return result

    @staticmethod
    def create_from_transaction(transaction, packet, user, by=None, params={}):
        spa = ServicePacketApplication(
            packet=packet,
            application_type=PACKET_CONNECTING,
            assigned_to=user,
            assigned_at=get_now(),
            assigned_by=by
        )
        spa.pickle_params(params)
        spa.save()
        spa.notify_created(transaction=transaction)
        transaction.packet_apps.add(spa)
        return spa

    @staticmethod
    def create_to_detach(assigned_packet, by=None, extra_params={}, number_id=""):
        "Создает заявку на отключение назначенного пакета услуг"
        app = ServicePacketApplication(
            packet=assigned_packet.packet,
            application_type=PACKET_DISCONNECTING,
            assigned_to=assigned_packet.assigned_to,
            assigned_at=get_now(),
            assigned_by=by,
            detach_packet=assigned_packet,
        )
        params = assigned_packet.unpickle_params()
        params.update(extra_params)
        app.pickle_params(params)
        app.save()
        #app.packet.functionals_call("AvailableServicePacketApplicationCreated", app, None, params)

        params["sp_application_to_detach_id"] = app.id
        params["number_from_detach"] = number_id
        cancel_doc_apps = []
        # создадим заявки на подписание документа отключения всех услуг этого пакета
        for service in app.packet.services.all():
            if service.cancel_document:
                doc_app = service.cancel_document.create_from_sp_app(
                    app.assigned_to,
                    app,
                    by=by,
                    params=params,
                    user_can_cancel=True,
                )
                cancel_doc_apps.append(doc_app)

        params = app.unpickle_params()
        params["cancel_findocuments_applications"] = cancel_doc_apps
        app.pickle_params(params)
        app.save()
        app.notify_created()
        return app

    def findoc_app_canceled_detach(self, findoc_app):
        "Вызывается заявкой на документ при отмене документа на отключение пакета услуг"
        self.packet.functionals_call("FindocApplicationCanceled", findoc_app, self)
        self.cancel(findoc_app, notify=True)

    def findoc_app_signed_detach(self, findoc_app, findoc_signed, number_id):
        "Вызывается заявкой на документ при при ее подписании. Отключение пакета услуг"
        self.packet.functionals_call("FindocApplicationSigned", findoc_app, findoc_signed, self)
        self.try_detach(number_id=number_id)

    def try_detach(self, number_id):
        "Пытается отсоединить отсоединяемый пакет услуг"
        findoc_app_count = len(self.wait_documents.all())
        if findoc_app_count == 0:
###############################################################################################

            from django.db import connections, transaction
            import datetime
            import pickle
            query = pickle.loads(self.params_data.encode('utf-8'))
            try:
                numbers_id = query['transaction_create_list_params'][0]['localnumbers_add_num_id']
            except:
                numbers_id = query['localnumbers_add_num_id']
            no = datetime.datetime.now()
            now = datetime.datetime(no.year, no.month, no.day)
            cur = connections[settings.BILLING_DB].cursor()
            cur2 = connections[settings.GLOBALHOME_DB2].cursor()
            cur.execute("SELECT number FROM external_numbers WHERE id=%s;", (number_id,))
            numbers = cur.fetchone()[0]
            cur2.execute("SELECT billing_account_id FROM account_profile WHERE user_id=%s;", (self.assigned_to.id,))
            billing_account_id = cur2.fetchone()[0]
            transaction.commit_unless_managed(settings.BILLING_DB)
            transaction.commit_unless_managed(settings.GLOBALHOME_DB2)

            try:
                cur.execute("UPDATE billservice_accountaddonservice SET action_status=%s, deactivated=%s WHERE numbers=%s and service_id=%s and account_id=%s and action_status=%s;", (False, now, numbers, 3 , billing_account_id, True,))
                cur.execute("UPDATE billservice_accountaddonservice SET action_status=%s, deactivated=%s WHERE numbers=%s and service_id=%s and account_id=%s and action_status=%s RETURNING id;", (False, now, numbers, 4 , billing_account_id, True,))
                id_for_services = cur.fetchone()[0]
                cur.execute("DELETE FROM billservice_prepaid_minutes WHERE service_id = %s;", (id_for_services,))
                transaction.commit_unless_managed(settings.BILLING_DB)

            except:
                pass
###############################################################################################


            self.detach_packet.execute_detach(self)
            self.delete()

    def __unicode__(self):
        if self.application_type == PACKET_CONNECTING:
            return _(u'An application for service packet connection "%(packet)s" to the user "%(user)s"') % {
                "packet": unicode(self.packet),
                "user": self.assigned_to,
            }
        if self.application_type == PACKET_DISCONNECTING:
            return _(u'An application for service packet detaching "%(packet)s" from the user "%(user)s"') % {
                "packet": unicode(self.packet),
                "user": self.assigned_to,
            }

    def notify_created(self, no_documents=False, transaction=None):
        "Уведомляет функционалы пакета о том, что эта заявка создана"
        params = self.unpickle_params()
        self.packet.functionals_call("AvailableServicePacketApplicationCreated", self, no_documents, params, transaction=transaction)

    def cancel(self, findoc_app=None, transaction=None, notify=False, no_delete=False):
        self.packet.functionals_call("ServicePacketApplicationCanceled", self, findoc_app, transaction=transaction)

        wait_docs = list(self.wait_documents.all())
        for wd in wait_docs:
            self.wait_documents.remove(wd)

        if not no_delete:
            self.delete()
        if notify:
            settings.GLOBAL_OBJECTS["request"].notifications.add(_(u"Operation aborted by user"), "warning")

    def get_findocs_applications(self, request):
        "Возвращает список заявок на подписание документов, которые были добавлены при создании этой заявки"
        params = self.unpickle_params()
        result = []
        transaction_id = params.get("transaction_id")
        if transaction_id:
            # узнаем список документов у транзакции
            transaction = AddSPTransaction.objects.get(id=transaction_id)
            params = transaction.unpickle_params()
            otd_id = params.get("onetime_document_application_id")
            red_id = params.get("reusable_document_application_id")
            if otd_id:
                try:
                    result.append(FinDocSignApplication.objects.get(id=otd_id))
                except:
                    pass
            if red_id:
                try:
                    result.append(FinDocSignApplication.objects.get(id=red_id))
                except:
                    pass
        else:
            # узнаем список документов прямо у самой заявки, это должен быть список документов на отключение заявки
            apps_ids = params.get("cancel_findocuments_applications")
            if apps_ids:
                result.append(FinDocSignApplication.objects.filter(id__in=[int(id) for id in apps_ids]))
        return result

    def cancel_admin(self, request):
        "Вызывается из админки при отмене заявки админом"

        '''
            Надо найти заявку на подписание документа, которая соответствует этой заявке и отменить ее, а она уже отменит всё остальное.
        '''
        doc_apps = self.get_findocs_applications(request)
        if doc_apps:
            url = doc_apps[0].cancel(request=request, no_notify=True)#, cancel_delete = True)




    def findoc_app_canceled(self, findoc_app, transaction):
        self.packet.functionals_call("FindocApplicationCanceled", findoc_app, self, transaction=transaction)

    def findoc_app_signed(self, findoc_app, findoc_signed, transaction):
        self.packet.functionals_call("FindocApplicationSigned", findoc_app, findoc_signed, self, transaction=transaction)

    def assign(self, transaction=None):
        "Назначает этот пакет услуг"
        asp = AssignedServicePacket(
            packet=self.packet,
            assigned_to=self.assigned_to,
            assigned_by=self.assigned_by,
            assigned_at=get_now(),
            application_cteated_at=self.assigned_at,
        )
        asp.pickle_params(self.unpickle_params())
        asp.save()
        # снять финансы с пользователя за подключение
        self.assigned_to.get_profile().withdraw_funds(self.packet.get_connect_price(), cause=_(u"Assigning service packet '%s'") % self.packet)
        self.packet.functionals_call("ServicePacketApplicationAssigned", self, asp, transaction=transaction)
        self.delete()

    class Meta:
        ordering = ("-assigned_at",)
        db_table = "services_packets_applications"
        verbose_name = _(u"Service packet application")
        verbose_name_plural = _(u"Service packets applications")

class AssignedServicePacket(ParamsModel):
    "Назначенный пакет услуг"
    enabled = models.BooleanField(default=True)
    packet = models.ForeignKey(AvailableServicePacket, verbose_name=_(u"Available service packet"), related_name="+")
    assigned_to = models.ForeignKey(User, verbose_name=_(u"Assigned to"), related_name="+")
    application_cteated_at = models.DateTimeField(default=get_now, verbose_name=_(u"Application created at"))
    assigned_at = models.DateTimeField(default=get_now, verbose_name=_(u"Assigned at"))
    assigned_by = models.ForeignKey(User, verbose_name=_(u"Assigned by"), related_name="+", blank=True, null=True)

    def __unicode__(self):
        return _(u'Assigned service packet "%(packet)s" to user "%(user)s"') % {
            "packet": unicode(self.packet),
            "user": self.assigned_to,
        }

    def extra_text(self):
        try:
            return ", ".join(self.packet.functionals_call("AdminAssignedPacketExtraText", self))
        except Exception, e:
            return "Exception %s: %s" % (type(e), unicode(e))
    extra_text.short_description = _(u"Extra text")

    @staticmethod
    def filter_by_params(params, user=None, packet=None, packet_slug=""):
        "Фильтрует назначенные пакеты услуг по указанным параметрам, пользователю и пакету. Возвращает список из подошедших назначенных пакетов услуг"
        result = []
        all = AssignedServicePacket.objects.all()
        if user:
            all = all.filter(assigned_to=user)
        if packet:
            all = all.filter(packet=packet)
        else:
            if packet_slug:
                packet = AvailableServicePacket.objects.get(slug=packet_slug)
                all = all.filter(packet=packet)
        for asp in all:
            asp_params = asp.unpickle_params()
            not_match = False
            for key in params:
                if asp_params.has_key(key):
                    if asp_params[key] != params[key]:
                        not_match = True
                        break
                else:
                    not_match = True
                    break
            if not not_match:
                result.append(asp)
        return result

    def detach(self, by=None, extra_params={}, number_id=""):
        "Отсоединяет этот назначенный пакет услуг"
        # создать заявку на отключение услуги
        app = ServicePacketApplication.create_to_detach(self, by=by, extra_params=extra_params, number_id=number_id)
        # попытаться ее выполнить
        return app.try_detach(number_id=number_id)

    def execute_detach(self, sp_app):
        self.packet.functionals_call("AssignedServicePacketDetached", sp_app, self)
        self.delete()
        settings.GLOBAL_OBJECTS["request"].notifications.add(_(u"Operation successfully completed"), "success")

    class Meta:
        ordering = ("-assigned_at",)
        db_table = "services_packets_assigned"
        verbose_name = _(u"Assigned service packet")
        verbose_name_plural = _(u"Assigned services packets")

class AddSPTransaction(ParamsModel):
    "Транзакция добавления нескольких экземпляров одного пакета услуг"
    packet = models.ForeignKey(AvailableServicePacket, verbose_name=_(u"Available service packet"), related_name="+")
    assigned_to = models.ForeignKey(User, verbose_name=_(u"Assigned to"), related_name="+")
    assigned_at = models.DateTimeField(default=get_now, verbose_name=_(u"Assigned at"))
    assigned_by = models.ForeignKey(User, verbose_name=_(u"Assigned by"), related_name="+", blank=True, null=True)
    packet_apps = models.ManyToManyField(ServicePacketApplication, related_name="add_transactions", editable=False)

    from findocs.models import FinDocSignApplication
    wait_documents = models.ManyToManyField(FinDocSignApplication, related_name="add_trans_wait", editable=False)

    def check_price(self, user=None):
        "Проверяет на наличие средств у указанного пользователя на выполнение этой транзакции"
        if not user:
            user = self.assigned_to
        price1 = self.packet.get_connect_price()
        list_params = self.unpickle_params()["transaction_create_list_params"]
        sum_price = price1 * len(list_params)
        if user.get_profile().get_balance() + user.get_profile().get_credit() < sum_price:
            return False
        return True

    def delete(self):
        return super(AddSPTransaction, self).delete()

    @staticmethod
    def connect_many(slug, user, by=None, list_params=[], no_check_balance=True):
        "Создает транзакцию добавления пакетов услуг и пытается их добавить"
        packet = AvailableServicePacket.objects.get(slug=slug)

        asptrans = AddSPTransaction(
            packet=packet,
            assigned_to=user,
            assigned_at=get_now(),
            assigned_by=by,
        )
        asptrans.pickle_params({ "transaction_create_list_params": list_params, "no_check_balance": no_check_balance })
        asptrans.save()

        asptrans.packet.functionals_call("AddTransactionCreated", asptrans, no_check_balance=no_check_balance)

#        if not no_check_balance:
#            if not asptrans.check_price(user):
#                asptrans.cancel(no_notify=True)
#                raise BalanceException()

        doc_params = {
            "transaction_create_list_params": list_params,
            "transaction_id": asptrans.id,
        }

        # создаем заявки на подключение пакетов услуг
        for params in list_params:
            doc_params.update(params)
            ServicePacketApplication.create_from_transaction(asptrans, packet, user, by=by, params=doc_params)

        # создадим заявки на подписание документов
        print doc_params
        asptrans.create_documents(doc_params)

        # попробуем подключить все эти пакеты услуг
        asptrans.go_next()

        return asptrans



    def create_documents(self, params):
        "Создает все необходимые заявки на подписание документов"
        for service in self.packet.services.all():
            if service.onetime_document:
                # проверить, не подписан ли он уже
                if not service.onetime_document.get_signed(self.assigned_to):
                    docapp = service.onetime_document.create_from_sp_app(
                        self.assigned_to,
                        self,
                        by=self.assigned_by,
                        params=params,
                        user_can_cancel=True,
                        transaction=self,
                    )
                    t_params = self.unpickle_params()
                    t_params["onetime_document_application_id"] = docapp.id
                    self.pickle_params(t_params)
                    self.save()
            if service.reusable_document:

                p2 = params.copy()
                try:
                    if service.reusable_document.id==3:
                        print 'sozdau'
                        print p2
                        t=FinDoc.objects.get(slug="act_for_numb")
                        t.new_doc(self.assigned_to,None,"",True,None)
                        t.save
                        print 'sozdal'
                        pass
                except Exception,e:
                    print e

                docapp = service.reusable_document.create_from_sp_app(
                    self.assigned_to,
                    self,
                    by=self.assigned_by,
                    params=p2,
                    user_can_cancel=True,
                    transaction=self,
                )
                t_params = self.unpickle_params()
                t_params["reusable_document_application_id"] = docapp.id
                self.pickle_params(t_params)
                self.save()

    def findoc_app_canceled(self, findoc_app, no_notify=False):
        "Вызывается заявкой на подписание документа при ее отмене"
        # уведомить все заявки на пакеты о том, что документ отменен
        for spa in self.packet_apps.all():
            # просто уведомим все заявки на пакеты в этой транзакции о том, что было отменено подписание заявки на документ
            spa.findoc_app_canceled(findoc_app, self)

        self.cancel(findoc_app, no_notify=no_notify)

    def findoc_app_signed(self, findoc_app, findoc_signed):
        "Вызывается заявкой на подписание документа при ее подписании"
        # уведомить все заявки на пакеты о том, что документ подписан
        for spa in self.packet_apps.all():
            spa.findoc_app_signed(findoc_app, findoc_signed, self)

        self.go_next()

    def go_next(self):
        # вот тут нужно проверить, готовы ли все заявки на пакеты и если готовы - тогда подключить все заявки этой транзакции
        findoc_app_count = len(self.wait_documents.all())
        if findoc_app_count == 0:
            self.try_assign()

    def try_assign(self):
        "Пытается назначить все пакеты в этой транзакции"
        # опросим все заявки на пакеты на тот факт, можно ли подключать эту услугу
        cancel = False
        for spapp in self.packet_apps.all():
            res = spapp.packet.functionals_call("CheckPacketAppBeforeAssign", spapp, transaction=self)
            for r in res:
                if not r:
                    cancel = True
        # если какой-то функционал не разрешил назначение пакета - то отменяем всю транзакцию
        if cancel:
            self.cancel()
        else:
            if not self.unpickle_params()["no_check_balance"]:
                if not self.check_price():
                    # не хватает денег у пользователя
                    for spapp in self.packet_apps.all():
                        spapp.packet.functionals_call("NotEnoughBalanceWhenPacketAssign", spapp, transaction=self)
                    self.cancel()
                    cancel = True
            if not cancel:
                # назначаем пакеты
                nnuu = 0
                x = 0
                for spapp in self.packet_apps.all():

##########добавляем  запись в accountaddonservice запись!!#############################################################



                    print "test"

                    import datetime
                    import pickle
                    import calendar
                    try:
                        query = pickle.loads(self.params_data.encode('utf-8'))
                        numbers_id = query['transaction_create_list_params'][nnuu]['localnumbers_add_num_id']
                        nnuu = nnuu + 1
                        now = datetime.datetime.now()
                        now1 = datetime.datetime(now.year, now.month, 1)
                        cur = connections[settings.BILLING_DB].cursor()
                        cur2 = connections[settings.GLOBALHOME_DB2].cursor()
                        cur.execute("SELECT number, region,tarif_group FROM external_numbers WHERE id=%s;", (numbers_id,))
                        external_numbers = cur.fetchone()

                        cur.execute("SELECT id,price_add,price_abon FROM external_numbers_tarif WHERE id=%s;", (external_numbers[2],))
                        price_for_numb = cur.fetchone()
                        ####################################

                        print price_for_numb
                        cur.execute("SELECT cost FROM billservice_addonservice WHERE id=%s ;", (price_for_numb[1],))
                        summ_in_service_3 = cur.fetchone()[0]
                        cur.execute("SELECT cost FROM billservice_addonservice WHERE id=%s ;", (price_for_numb[2],))
                        summ = cur.fetchone()
                        print '-----------'
                        print 'bred'
                        print price_for_numb[1]
                        print price_for_numb[2]
                        print '-----------'

                        cur2.execute("SELECT billing_account_id, is_juridical FROM account_profile WHERE user_id=%s;", (self.assigned_to.id,))
                        resultat = cur2.fetchall()[0]
                        billing_account_id = resultat[0]
                        is_juridical = resultat[1]
                        cur.execute("INSERT INTO billservice_accountaddonservice(service_id, account_id, activated, action_status, numbers) VALUES(%s, %s, %s, %s, %s) RETURNING id;", (price_for_numb[1], billing_account_id, now1, True, external_numbers[0],))
                        id_for_services1 = cur.fetchone()
                        cur.execute("INSERT INTO billservice_accountaddonservice(service_id, account_id, activated, action_status, numbers) VALUES(%s, %s, %s, %s, %s) RETURNING id;", (price_for_numb[2], billing_account_id, now1, True, external_numbers[0],))
                        id_for_services = cur.fetchone()
                        cur.execute("SELECT id FROM billservice_accounttarif WHERE account_id=%s ;", (billing_account_id,))
                        accounttarif_id = cur.fetchone()

                        #получаем цены для данного номера


                    except Exception, e:
                        print e

                    all_day = calendar.monthrange(now.year, now.month)
                    active_day = int(all_day[1]) - now.day
                    summ_end = float(summ[0]) / int(all_day[1]) * (active_day + 1)
                    cur.execute("INSERT INTO billservice_addonservicetransaction(service_id, service_type, account_id, accountaddonservice_id, accounttarif_id, summ, created, type_id, check_sent) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;", (price_for_numb[1], "onetime", billing_account_id, id_for_services1, accounttarif_id, round(summ_in_service_3, 2), now1, "ADDONSERVICE_ONETIME", True,))
                    id_for_transaktion_onetime = cur.fetchone()
                    cur.execute("INSERT INTO billservice_addonservicetransaction(service_id, service_type, account_id, accountaddonservice_id, accounttarif_id, summ, created, type_id, check_sent) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;", (price_for_numb[1], "periodical", billing_account_id, id_for_services, accounttarif_id, round(summ_end, 2), now1, "ADDONSERVICE_PERIODICAL_AT_START", True,))
                    id_for_transaktion = cur.fetchone()
                    cur.execute("UPDATE billservice_accountaddonservice SET deactivated = %s, last_checkout = %s WHERE id = %s;", (now1, now1, id_for_services1,))
                    cur.execute("SELECT billservice_addonservice.prepaid_minutes FROM billservice_accountaddonservice JOIN billservice_addonservice on(billservice_accountaddonservice.service_id = billservice_addonservice.id) WHERE billservice_accountaddonservice.id=%s ;", (id_for_services,))
                    minutes = cur.fetchone()[0]
                    if external_numbers[1] == 1:
                        zone_id = '404'
                    elif external_numbers[1] == 2:
                        zone_id = '408'
                    else:
                        zone_id = '0'
                    cur.execute("INSERT INTO billservice_prepaid_minutes(zone_id, minutes, account_id, service_id, date_of_accrual) VALUES(%s, %s, %s, %s, %s);", (zone_id, minutes, billing_account_id, id_for_services, now))

                    transaction.commit_unless_managed(settings.BILLING_DB)
                    x = x + 1
#                    except:
#                        pass

#################################################################################################
                    spapp.assign(self)
                from account.models import Profile
                profile = Profile.objects.get(user=self.assigned_to.id)
                if profile.company_name:
                    c_name = profile.company_name
                else:
                    c_name = ""
                if profile.last_name:
                    last_name = profile.last_name
                else:
                    last_name = ""
                if profile.first_name:
                    first_name = profile.first_name
                else:
                    first_name = ""
                if profile.second_name:
                    second_name = profile.second_name
                else:
                    second_name = ""
                cur.execute("SELECT name, cost FROM billservice_addonservice WHERE id = %s;", (3,))
                service_name1 = cur.fetchall()[0]
                cur.execute("SELECT name FROM billservice_addonservice WHERE id = %s;", (4,))
                service_name2 = cur.fetchone()[0]
                add_service_1_in_check1 = ""
                start = datetime.datetime(now.year, now.month - 1, 1).date()
                filename = "check_for_" "%s" % self.assigned_to.username + "_at_" + "%s" % start
                filename1 = "check_invoice_for_" "%s" % self.assigned_to.username + "_at_" + "%s" % start
                filename2 = "akt_for_" "%s" % self.assigned_to.username + "_at_" + "%s" % start
                cur2.execute("SELECT max(number) FROM content_check;")
                max_number = cur2.fetchone()
                cur2.execute("INSERT INTO content_check(created_by_id, created_at, modified_at, name, type, number) VALUES(%s, %s, %s, %s, %s, %s) RETURNING id;", (self.assigned_to.id, now, now, filename, 'check', (max_number[0] + 1)))
                id_from_check = cur2.fetchone()
                number_check = max_number[0] + 1
                cur2.execute("INSERT INTO content_check(created_by_id, created_at, modified_at, name, type, number) VALUES(%s, %s, %s, %s, %s, %s) RETURNING id;", (self.assigned_to.id, now, now, filename1, 'invoice', (max_number[0] + 1)))
                id_from_check_invoice = cur2.fetchone()
                number_check_invoice = max_number[0] + 1
                cur2.execute("INSERT INTO content_check(created_by_id, created_at, modified_at, name, type, number) VALUES(%s, %s, %s, %s, %s, %s) RETURNING id;", (self.assigned_to.id, now, now, filename2, 'act', (max_number[0] + 1)))
                id_from_akt = cur2.fetchone()
                number_akt = max_number[0] + 1
                cur2.execute("SELECT id FROM fin_docs_signeds WHERE signed_by_id = %s and findoc_id = %s;", (self.assigned_to.id, 1,))
                id_findoc = cur2.fetchone()[0]

                #transaction.commit_unless_managed(settings.BILLING_DB)
                #transaction.commit_unless_managed()
                NDS_all = 0
                NDS_all = ((float(service_name1[1]) - float(service_name1[1]) / 1.18) + (float(summ_end) - float(summ_end) / 1.18)) * x
                summ_for_service_all = 0
                summ_for_service_all = (float(service_name1[1]) + float(summ_end)) * x
                add_service_1_in_check1 = """
                                <tr>
                                    <th align="left">%(service_name)s</th>
                                    <th>шт</th>
                                    <th>%(service_1)s</th>
                                    <th>%(service_for_account)s</th>
                                    <th>%(summ_for_service_1)s</th>
                                </tr>
                                    """ % {
                                            "service_name": service_name1[0].encode('utf-8'),
                                            "service_1": x,
                                            "service_for_account": round(float(service_name1[1]) / 1.18, 2),
                                            "summ_for_service_1": round((float(service_name1[1]) / 1.18) * x, 2),
                                         }
                add_service_1_in_check2 = """
                                <tr>
                                    <th align="left">%(service_name)s</th>
                                    <th>шт</th>
                                    <th>%(service_1)s</th>
                                    <th>%(service_for_account)s</th>
                                    <th>%(summ_for_service_1)s</th>
                                </tr>
                                    """ % {
                                            "service_name": service_name2.encode('utf-8'),
                                            "service_1": x,
                                            "service_for_account": round(float(summ_end) / 1.18, 2),
                                            "summ_for_service_1": round((float(summ_end) / 1.18) * x, 2),
                                         }
                add_service_1_in_ak1 = """
                                        <tr>
                                            <th align="left">%(service_name)s</th>
                                            <th>%(service_1)s</th>
                                            <th>шт</th>
                                            <th>%(service_for_account)s</th>
                                            <th>%(summ_for_service_1)s</th>
                                        </tr>
                """ % {
                        "service_1": x,
                        "service_for_account": round(float(service_name1[1]) / 1.18, 2),
                        "service_name": service_name1[0].encode('utf-8'),
                        "summ_for_service_1": round((float(service_name1[1]) / 1.18) * x, 2),
                    }
                add_service_1_in_ak2 = """
                                        <tr>
                                            <th align="left">%(service_name)s</th>
                                            <th>%(service_1)s</th>
                                            <th>шт</th>
                                            <th>%(service_for_account)s</th>
                                            <th>%(summ_for_service_1)s</th>
                                        </tr>
                """ % {
                        "service_1": x,
                        "service_for_account": round(float(summ_end) / 1.18, 2),
                        "service_name": service_name2.encode('utf-8'),
                        "summ_for_service_1": round((float(summ_end) / 1.18) * x, 2),
                    }
                add_service_1_invoic1 = """

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
                                            "service_1": x,
                                            "service_for_account": round(float(service_name1[1]) / 1.18, 2),
                                            "summ_for_service_1": round((float(service_name1[1]) / 1.18) * x, 2),
                                            "NDS_1": round((float(service_name1[1]) - float(service_name1[1]) / 1.18) * x, 2),
                                            "service_name": service_name1[0].encode('utf-8'),
                                            "summa_s_nds_1": round((float(service_name1[1])) * x, 2),

                                        }
                add_service_1_invoic2 = """

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
                                            "service_1": x,
                                            "service_for_account": round(float(summ_end) / 1.18, 2),
                                            "summ_for_service_1": round((float(summ_end) / 1.18) * x, 2),
                                            "NDS_1": round((float(summ_end) - float(summ_end) / 1.18) * x, 2),
                                            "service_name": service_name2.encode('utf-8'),
                                            "summa_s_nds_1": round((float(summ_end)) * x, 2),

                                        }
                if is_juridical == True:
                    company_name_or_family = c_name.encode('utf-8')
                else:
                    company_name_or_family = (last_name.encode('utf-8') + " " + first_name.encode('utf-8') + " " + second_name.encode('utf-8'))
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
                               <th> <h5>КПП</h5></th>
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
           <h3 align="left"><strong>СЧЕТ №  %(id_from_check)s на основании договора № %(id_findoc)s</strong></h3>

              <div align="left">Заказчик: %(profile.company_name)s</div>
              <hr />
             <div align="left"> Плательщик: %(profile.company_name)s</div>
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

                                    %(add_service_1_in_check)s
                                    %(add_service_1_in_check2)s
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
                     <h4 align="left"><address> К оплате:</address><hr/><h4>
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
                    "profile.company_name": company_name_or_family,
#                        "add_summ_in_check": add_telemate_in_check,
                    "add_service_1_in_check": add_service_1_in_check1,
#                            "add_service_2_in_check": add_service_2_in_check,
                    "add_service_1_in_check2": add_service_1_in_check2,
                    "NDS_all": round(NDS_all, 2),
                    "summ_for_service_all": round(summ_for_service_all, 2),
                    "id_from_check": "%s/1" % number_check,
                    "id_findoc": id_findoc,
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
                           <h6> <div>Приложение N1</div>
                            <div>к Правилам ведения журналов учета полученных и выставленных счетов-фактур, </div>
                            <div> книг покупок и книг продаж при расчетах по налогу на добавленную стоимость, </div>
                            <div>утвержденным постановлением Правительства Российской Федерации от 2 декабря 2000 г. N 914</div>
                            <div>(в редакции пос    тановлений Правительства Российской Федерации от 15 марта 2001 г. N 189, </div>
                            <div> от 27 июля 2002 г. N 575, от 16 февраля 2004 г. N 84, от 11 мая 2006 г. N 283, от 26 мая 2009 г. N 451)</div></h6>
                        </th>
                        </tr>
                        <tr>
                        <th align="left">
                                            СЧЕТ-ФАКТУРА № %(id_from_check)s на основании договора № %(id_findoc)s
                            <h6> <div>Продавец: Общество с ограниченной ответственностью "Телеком-ВИСТ" (ООО "Телеком-ВИСТ")</div>
                            <div>Адрес: 125367, Москва г, Врачебный проезд, д. 10, кв. 1</div>
                            <div>ИНН/КПП продавца: 7733720884/773301001</div>
                            <div>Грузоотправитель и его адрес: ----</div>
                            <div>Грузополучатель и его адрес:----</div>
                            <div>К платежно-расчетному документу______________от____________</div>
                            <div>Покупатель: %(profile.company_name)s</div>
                            <div align="right">Валюта: руб.</div>
                        <table style="color:#black" border="1" cellpadding="4" cellspacing="0">
                        <thead>
                                            <tr bgcolor="#FBF0DB">
                                                <th><h5>Наименование товара (описание выполненных работ, оказанных услуг), имущественного права</h5></th>
                                                <th><h5>Единица измерения</h5></th>
                                                <th><h5>Количество</h5></th>
                                                <th><h5>Цена (тариф) за единицу измерения</h5></th>
                                                <th><h5>Стоимость товаров (работ, услуг), имущественных прав, всего без налога</h5></th>
                                                <th><h5>В том числе акциз</h5></th>
                                                <th><h5>Страна происхождения</h5></th>
                                                <th><h5>Номер таможенной декларации</h5></th>
                                                <th><h5>Налоговая ставка</h5></th>
                                                <th><h5>Сумма налога</h5></th>
                                                <th><h5>Стоимость товаров (работ, услуг), имущественных прав, всего с учетом налога</h5></th>

                                            </tr>
                        </thead>
                        <tbody>
                                            %(add_service_1_invoice)s
                                            %(add_service_2_invoice)s
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
                                                <td colspan="9"><strong>Всего к оплате</strong></td>
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
                """ % {
                    "profile.company_name": company_name_or_family,
                    "add_service_1_invoice": add_service_1_invoic1,
                    "add_service_2_invoice": add_service_1_invoic2,
                    "NDS_all": round(NDS_all, 2),
                    "summ_for_service_all": round(summ_for_service_all, 2),
                    "id_from_check": "%s/2" % number_check,
                    "id_from_check_invoice": number_check_invoice,
                    "id_findoc": id_findoc,
                    }
                from content.views import perewod
                qqqq = str(round(summ_for_service_all, 2))
                slowa_dlj_itogo = perewod(qqqq)
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
                        <th align="left"><h3>Акт № %(id_from_check)s на основании договора № %(id_findoc)s<h3><hr/></th>
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
                            <td align="left"><h4>%(profile.company_name)s</h4></td>
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

                                                                            %(add_service_1_in_akt)s
                                                                            %(add_service_2_in_akt)s
                                                                            <tr>
                                                                                <td>&nbsp;</td>
                                                                                <td>&nbsp;</td>
                                                                                <td>&nbsp;</td>
                                                                                <td>&nbsp;</td>
                                                                                <td>&nbsp;</td>
                                                                            </tr>
                                                                            <tr>
                                                                                <th colspan="4" align="right"><strong>Итого:</strong></th>
                                                                                <th>%(summ_for_service_minus_NDS)s</th>
                                                                            </tr>
                                                                            <tr>
                                                                                <th colspan="4" align="right"><strong>В том числе НДС:</strong></th>
                                                                                <th>%(NDS_all)s</th>
                                                                            </tr>
                                                                            <tr>
                                                                                <th colspan="4" align="right"><strong>Итого с НДС:</strong></th>
                                                                                <th>%(summ_for_service_all)s</th>
                                                                            </tr>
                                                        </tbody>
                                   </table>
                       </tr>
                       </th>
                       <tr><th>&nbsp;</th></tr>
                       <tr><th>&nbsp;</th></tr>
                       <tr align="left"><th>Всего оказано услуг на сумму: %(slowa_dlj_itogo)s</th></tr>
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
                    "profile.company_name": company_name_or_family,
                    "add_service_1_in_akt": add_service_1_in_ak1,
                    "add_service_2_in_akt": add_service_1_in_ak2,
                    "summ_for_service_minus_NDS": round(summ_for_service_all / 1.18, 2),
                    "NDS_all": round(NDS_all, 2),
                    "slowa_dlj_itogo": slowa_dlj_itogo,
                    "summ_for_service_all": round(summ_for_service_all, 2),
                    "id_from_akt": number_akt,
                    "id_findoc": id_findoc,
                    "id_from_check": "%s/3" % number_check,
                    }
                cur2.execute("UPDATE content_check SET text = %s, sent = %s WHERE id = %s;", (text, True, id_from_check))
                cur2.execute("UPDATE content_check SET text = %s, sent = %s WHERE id = %s;", (text2, True, id_from_check_invoice))
                cur2.execute("UPDATE content_check SET text = %s, sent = %s WHERE id = %s;", (text3, True, id_from_akt))

                filename1 = 'check'
                filename2 = 'invoice'
                filename3 = 'akt'
                out_f = open('%s.htm' % filename1, 'w')
                out_f.write(text)
                out_f.close()
                out_f1 = open('%s.htm' % filename2, 'w')
                out_f1.write(text2)
                out_f1.close()
                out_f2 = open('%s.htm' % filename3, 'w')
                out_f2.write(text3)
                out_f2.close()
                cur2.execute("SELECT email FROM auth_user WHERE id=%s;", (self.assigned_to.id,))
                email = cur2.fetchone()[0]
                msg = EmailMultiAlternatives("email subject", "check", settings.DEFAULT_FROM_EMAIL, [email])
                msg.attach_alternative(text, "text/html")
                msg.attach_file('%s.htm' % filename1)
                msg.attach_file('%s.htm' % filename2)
                msg.attach_file('%s.htm' % filename3)
                msg.send()
                transaction.commit_unless_managed(settings.BILLING_DB)
                transaction.commit_unless_managed(settings.GLOBALHOME_DB2)
                self.packet.functionals_call("AddTransactionCompleted", self)

                self.delete()

                try:
                    settings.GLOBAL_OBJECTS["request"].notifications.add(_(u"The transaction was successfully off and the invoice was sent to your e-mail."), "success")
                except:
                    print "exception..."

    def cancel(self, findoc_app=None, no_notify=False):
        "Отменяет эту транзакцию"
        # отменяем каждую заявку на пакет

        all_spapps = list(self.packet_apps.all())

        for spapp in all_spapps:
            # отменяем каждую заявку
            spapp.cancel(findoc_app, self)
            self.packet_apps.remove(spapp)



        self.packet.functionals_call("AddTransactionCanceled", findoc_app, self)
        '''
        for da in findoc_apps:
            print "deleting findoc app, id:", da.id
            da.delete()
        '''
        '''
        # вот этот кусок что-то дурно пахнет
        params = self.unpickle_params()
        print
        print "transaction params:", params
        print
        otd_app_id = params.get("onetime_document_application_id")
        if otd_app_id:
            try:
                print "deleting otd"
                otd_app = FinDocSignApplication.objects.get(id = otd_app_id)
                otd_app.delete()
                print "otd deleted"
            except:
                pass

        red_app_id = params.get("reusable_document_application_id")
        if red_app_id:
            try:
                red_app_id = int(red_app_id)
                print "deleting red, id =", red_app_id
                red_app = FinDocSignApplication.objects.get(id = red_app_id)
                print "founded red:", red_app
                red_app.delete()
                print "red deleted"
            except Exception, e:
                print type(e), e
        # а вот после этого уже нормально. пахнет.
        '''

        self.delete()

        if not no_notify:
            try:
                settings.GLOBAL_OBJECTS["request"].notifications.add(_(u"Operation aborted by user"), "warning")
            except:
                print "exception..."

    class Meta:
        ordering = ("-assigned_at",)
        db_table = "services_packets_add_transactions"

class AssignServicePacket(models.Model):

    class Meta:
        verbose_name_plural = _(u"Assign service packet")
        managed = False




