# coding: utf-8
from services.functional import BaseServiceFunctional
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from services.consts import PACKET_CONNECTING
from django.core.urlresolvers import reverse

class LocalnumberServiceFunctinal(BaseServiceFunctional):

    @classmethod
    def AdminConfigureFunctionalView(cls, functional, request, context):
        "Вызывается при редактировании функционала в админке"
        params = functional.unpickle_params()
        dm = params.get("detach_mode")
        if not dm:
            params["detach_mode"] = 2
            dm = "reserved"
            functional.pickle_params(params)
            functional.save()

        if request.POST:
            try:
                dm = int(request.POST.get("detach_mode"))
            except:
                dm = 2
            params["detach_mode"] = dm
            functional.pickle_params(params)
            functional.save()

        context["detach_mode"] = dm

        return render_to_response("admin/localphones/functional_configure.html", context, context_instance = RequestContext(request))

    @classmethod
    def AdminSPApplicationEditView(cls, functional, packet, request, application, context):
        """
            Вызывается при редактировании через админку заявки на добавление/отключение пакета услуг.
            Функция должна вернуть название шаблона и дополнительный контекст
        """
        template_name = "admin/localphone_service/sp_application_edit.html"
        extra_context = {}

        params = application.unpickle_params()
        num_id = params["localnumbers_add_num_id"]
        grp_id = params.get("localnumbers_add_group_id")
        from telnumbers.models import TelNumbersGroup
        from externalnumbers.models import ExternalNumber

        number = ExternalNumber.objects.get(id = int(num_id))
        if grp_id:
            group = TelNumbersGroup.objects.get(id = int(grp_id))
        else:
            group = None

        extra_context["application_number"] = number
        extra_context["application_group"] = group

        return template_name, extra_context

    @classmethod
    def AdminSPAssignedEditView(cls, functional, packet, request, assigned_sp, context):
        """
            Вызывается при редактировании через админку назначенного пакета услуг.
            Функция должна вернуть название шаблона и дополнительный контекст
        """
        template_name = "admin/localphone_service/sp_assigned_edit.html"
        extra_context = {}

        params = assigned_sp.unpickle_params()
        num_id = params["localnumbers_add_num_id"]
        from externalnumbers.models import ExternalNumber
        number = ExternalNumber.objects.get(id = int(num_id))
        extra_context["assigned_number"] = number
        return template_name, extra_context

    @classmethod
    def AdminSPAssignView(cls, functional, packet, request, context, to_user, assign = False):
        """
            View-функция, которая вызывается при назначении пользователю доступного пакета услуг
            Функция должна вернуть название шаблона, дополнительный контекст и HttpResponce или None
        """
        template_name = "admin/localphone_service/assign_service_packet.html"
        extra_context = {}
        responce = None

        from telnumbers.forms import group_widget_data
        from externalnumbers.models import ExternalNumber
        from externalnumbers.consts import REGIONS
        from externalnumbers.forms import AddExternalNumberForm
        from services.models import AddSPTransaction, BalanceException
        from django.utils.translation import ugettext_lazy as _
        from django.http import HttpResponseRedirect

        bac = to_user.get_profile().billing_account

        n_lim = ExternalNumber.free_numbers_limited(10)
        nbr = {}
        have_numbers = False
        for n in n_lim:
            have_numbers = True
            row = nbr.get(n.region)
            if row:
                row.append(n)
            else:
                nbr[n.region] = [n, ]

        extra_context["have_free_numbers"] = have_numbers

        groups = bac.telnumbersgroup_set.all()
        choices, settings = group_widget_data(groups, -1)

        settings["add_url"] = "/admin/telnumbers/telnumbersgroup/add_group/%s/" % to_user.id

        extra_context["regions"] = REGIONS

        if request.POST:
            form = AddExternalNumberForm(request.POST.copy(), numbers_by_regions = nbr, choices = choices, settings = settings)
            if assign:
                if have_numbers:
                    if form.is_valid():
                        nums_ids = form.cleaned_data["numbers"]
                        group_id = form.cleaned_data["user_groups"]

                        # а вот тут добавляем эти номера
                        list_params = []

                        for num_id in nums_ids:
                            list_params.append(
                                {
                                    "redirect_after_sign": reverse("external_phones_list"),
                                    "redirect_after_cancel": reverse("external_phones_list"),
                                    "localnumbers_add_nums_ids": nums_ids,
                                    "localnumbers_add_group_id": group_id,
                                    "localnumbers_add_num_id": num_id,
                                }
                            )

                        try:
                            AddSPTransaction.connect_many(
                                "localphones_packet",
                                to_user,
                                list_params = list_params,
                            )
                        except BalanceException:
                            # не хватает баланса у пользователя
                            request.notifications.add(_(u"User have insufficient funds to perform this operation!"), "error")
                        else:
                            request.notifications.add(_(u"Numbers successfully assigned"), "success")
                            responce = HttpResponseRedirect("/admin/services/assignservicepacket/")
                    else:
                        extra_context["errors"] = True
                else:
                    responce = HttpResponseRedirect("/admin/services/assignservicepacket/")
        else:
            form = AddExternalNumberForm(numbers_by_regions = nbr, choices = choices, settings = settings)


        extra_context["form"] = form

        return template_name, extra_context, responce





    @classmethod
    def AdminServicePacketApplicationExtraText(cls, functional, packet, sp_app):
        "Вызывается для показа в колонке Extra Text в админке у заявок на пакеты услуг"
        num_id = sp_app.unpickle_params()["localnumbers_add_num_id"]
        from externalnumbers.models import ExternalNumber
        num = ExternalNumber.objects.get(id = num_id)
        return unicode(num)


    @classmethod
    def AdminAssignedPacketExtraText(cls, functional, packet, assigned_packet):
        "Вызывается для показа в колонке Extra Text в админке у назначенных пакетов услуг"
        num_id = assigned_packet.unpickle_params()["localnumbers_add_num_id"]
        from externalnumbers.models import ExternalNumber
        num = ExternalNumber.objects.get(id = num_id)
        return unicode(num)







    @classmethod
    def AvailableServicePacketApplicationCreated(cls, functional, packet, application, no_documents, params, transaction = None):
        "Вызывается при создании заявки на подключение доступный пакет услуг"
        # вот тут мы захватываем номер этому пользователю
        if application.application_type == PACKET_CONNECTING:
            num_id = application.unpickle_params()["localnumbers_add_num_id"]
            from externalnumbers.models import ExternalNumber
            num = ExternalNumber.free_numbers.get(id = num_id)
            num.account = application.assigned_to.get_profile().billing_account
            num.save(no_assigned_at_save = True)
        else:
            pass

    '''
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
    #'''

    @classmethod
    def ServicePacketApplicationCanceled(cls, functional, packet, sp_app, findoc_app, transaction = None):
        "Вызывается при отмене заявки на пакет услуг"
        # вот тут открепляем захваченный номер
        if sp_app.application_type == PACKET_CONNECTING:
            num_id = sp_app.unpickle_params()["localnumbers_add_num_id"]
            from externalnumbers.models import ExternalNumber
            num = ExternalNumber.objects.get(id = num_id)
            num.account = None
            num.phone_numbers_group = None
            num.save(no_assigned_at_save = True)
        else:
            pass

    @classmethod
    def ServicePacketApplicationAssigned(cls, functional, packet, sp_app, sp_assigned, transaction = None):
        "Вызывается, когда заявка на добавление пакета услуг была превращена в назначенную услугу"
        # вот тут назначаем захваченному номеру группу
        num_id = sp_app.unpickle_params()["localnumbers_add_num_id"]
        group_id = sp_app.unpickle_params()["localnumbers_add_group_id"]
        from externalnumbers.models import ExternalNumber
        from telnumbers.models import TelNumbersGroup
        num = ExternalNumber.objects.get(id = num_id)
        group = TelNumbersGroup.objects.get(id = group_id)
        num.account = sp_app.assigned_to.get_profile().billing_account
        num.phone_numbers_group = group
        num.save()

    @classmethod
    def AssignedServicePacketDetached(cls, functional, packet, sp_app, assigned_packet):
        "Вызывается после отключения пакета услуг"
        num_id = sp_app.unpickle_params()["localnumbers_add_num_id"]
        from externalnumbers.models import ExternalNumber
        num = ExternalNumber.objects.get(id = num_id)
        f_p = functional.unpickle_params()
        dm = f_p.get("detach_mode")
        if not dm:
            f_p["detach_mode"] = 2
            functional.pickle_params(f_p)
            functional.save()
            dm = 2
        if dm == 1:
            num.make_free()
        if dm == 2:
            num.make_reserved()




    '''
    @classmethod
    def CheckPacketAppBeforeAssign(cls, functional, packet, sp_app, transaction = None):
        "Вызывается при последней проверке перед назначением пакетов в транзакции. Если вернет False - транзакция будет отменена"
        return True



    @classmethod
    def NotEnoughBalanceWhenPacketAssign(cls, functional, packet, sp_app, transaction = None):
        "Вызывается, когда перед назначением услуги выяснилось, что не хватает баланса у пользователя"

    '''




FUNCTIONAL_CLASS = LocalnumberServiceFunctinal
