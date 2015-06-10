# coding: utf-8
"""
    Тут лежит базовый класс для всех функционалов услуг
"""
#from lib.utils import get_ready_context
#from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from services.consts import PACKET_CONNECTING

class BaseServiceFunctional(object):
    """
        Базовый класс для всех функционалов услуг
        
        все функции тут (кроме тех, которые view-функции) - как бы уведомительные. их вызывает сервер, когда что-то происходит. вроде подписания документы и тп
    """
    
    @classmethod
    def AdminConfigureFunctionalView(cls, functional, request, context):
        "Вызывается при редактировании через админку функционала в админке"
        return render_to_response("admin/services/base_functional_configure.html", context, context_instance = RequestContext(request))

    @classmethod
    def AdminSPApplicationEditView(cls, functional, packet, request, application, context):
        """
            Вызывается при редактировании через админку заявки на добавление/отключение пакета услуг.
            Функция должна вернуть название шаблона и дополнительный контекст
        """
        template_name = ""
        extra_context = {}
        return template_name, extra_context
    
    @classmethod
    def AdminSPAssignedEditView(cls, functional, packet, request, assigned_sp, context):
        """
            Вызывается при редактировании через админку назначенного пакета услуг.
            Функция должна вернуть название шаблона и дополнительный контекст
        """
        template_name = ""
        extra_context = {}
        return template_name, extra_context
    
    @classmethod
    def AdminSPAssignView(cls, functional, packet, request, context, to_user, assign = False):
        """
            View-функция, которая вызывается при назначении пользователю доступного пакета услуг
            Функция должна вернуть название шаблона, дополнительный контекст и HttpResponce или None
        """
        template_name = ""
        extra_context = {}
        responce = None
        return template_name, extra_context, responce
    
    
    
    
    
    
    @classmethod
    def AdminServicePacketApplicationExtraText(cls, functional, packet, sp_app):
        "Вызывается для показа в колонке Extra Text в админке у заявок на пакеты услуг"
        return ""
    
    @classmethod
    def AdminAssignedPacketExtraText(cls, functional, packet, assigned_packet):
        "Вызывается для показа в колонке Extra Text в админке у назначенных пакетов услуг"
        return ""
    
    
    
    
    
    
    
    @classmethod
    def AvailableServicePacketApplicationCreated(cls, functional, packet, application, no_documents, params, transaction = None):
        "Вызывается при создании заявки на подключение доступного пакета услуг"
        if application.application_type == PACKET_CONNECTING:
            # подключение пакета
            pass
        else:
            # отключение пакета
            pass

    @classmethod
    def ServicePacketApplicationCanceled(cls, functional, packet, sp_app, findoc_app, transaction = None):
        "Вызывается при отмене заявки на пакет услуг"
        if sp_app.application_type == PACKET_CONNECTING:
            # подключение пакета
            pass
        else:
            # отключение пакета
            pass
    
    @classmethod
    def ServicePacketApplicationAssigned(cls, functional, packet, sp_app, sp_assigned, transaction = None):
        "Вызывается, когда заявка на добавление пакета услуг была превращена в назначенную услугу"

    @classmethod
    def AssignedServicePacketDetached(cls, functional, packet, sp_app, assigned_packet):
        "Вызывается после отключения пакета услуг"
        






    @classmethod
    def AddTransactionCreated(cls, functional, packet, transaction, no_check_balance = False):
        "Вызывается при создании заявки на подключение доступный пакет услуг"

    @classmethod
    def AddTransactionCanceled(cls, functional, packet, findoc_app, transaction = None):
        "Выщывается, когда транзакция добавления пакетов была полностью отменена"

    @classmethod
    def AddTransactionCompleted(cls, functional, packet, transaction = None):
        "Вызывается, когда транзакция добавления услуги полностью завершилась"





    
    @classmethod
    def FindocApplicationCreated(cls, functional, packet, findoc_app, sp_app, transaction = None):
        "Вызывается при создании заявки на подписание документа"

    @classmethod
    def FindocApplicationSigned(cls, functional, packet, findoc_app, findoc_signed, sp_app, transaction = None):
        "Вызывается при подписании заявки на подписание документа"

    @classmethod
    def FindocApplicationCanceled(cls, functional, packet, findoc_app, sp_app, transaction = None):
        "Вызывается при отказе подписать заявку на подписание документа"








    @classmethod
    def CheckPacketAppBeforeAssign(cls, functional, packet, sp_app, transaction = None):
        "Вызывается при последней проверке перед назначением пакетов в транзакции. Если вернет False - транзакция будет отменена"
        return True
    
    
    
    
    @classmethod
    def NotEnoughBalanceWhenPacketAssign(cls, functional, packet, sp_app, transaction = None):
        "Вызывается, когда перед назначением услуги выяснилось, что не хватает баланса у пользователя"





#FUNCTIONAL_CLASS = LocalnumberServiceFunctinal


