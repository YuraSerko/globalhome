# coding: utf-8
from findocs.models import FinDocTemplate, FinDoc, FinDocSignApplication, FinDocSigned, Package_on_connection_of_service
import log
from lib.utils import get_now
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from data_centr.models import Service_type, Zakazy

NEEDED_DOCS = ("telematic_services_contract",)  # тут перечислены слаги документов, которые должны быть всегда подписаны у пользователей

def get_application(user, slug):
    try:
        app = FinDocSignApplication.objects.filter(assigned_to=user, findoc__slug=slug)
    except:
        # log.add("Exception 1 in findocs.get_application: '%s'" % e)
        app = None
    if app.count() > 0:
        return app[0]

def get_signed(user, slug):
    sd = FinDocSigned.objects.filter(signed_by=user, findoc__slug=slug, cancellation_date=None)
    if sd.count() > 0:
        return sd[0]

def check_and_add_needed_docs(user):
    "Проверяет на наличие необходимых подписанных документов. При их отсутствии - создает на них заявки"
    profile = user.get_profile()
    if not profile.is_card:
        for doc_slug in NEEDED_DOCS:
            sd = get_signed(user, doc_slug)
            if not sd:
                # если нету заявок на этот документ - создаем заявку.
                app = get_application(user, doc_slug)
                if not app:
                    doc = FinDoc.objects.get(slug=doc_slug)
                    sd = FinDocSignApplication(
                        assigned_to=user,
                        assigned_at=get_now(),
                        findoc=doc,
                    )
                    sd.save()

#===============================================================================
# декоратор для проверки на наличие заявок пользователю на подписание документов указанного типа
#===============================================================================
def check_for_sign_applications(slugs_list=[]):  # проверять на наличие заявки на подписание документа указанного слага
    "декоратор проверяет наличие заявок пользователю на подписание документов с указанными слагами"
    def decor(func):
        def wrapper(request, *args, **kwargs):
            for s in NEEDED_DOCS:
                if s not in slugs_list:
                    slugs_list.append(s)
            if slugs_list:
                user = request.user
                try:
                    profile = user.get_profile()
                except:
                    pass
                else:
                    if profile.activated_at:
                        if not (profile.is_card or profile.is_hostel):
                            if profile.is_juridical:
                                if (profile.company_name and profile.legal_form and profile.general_director and\
                                    profile.sign_face and profile.sign_cause and profile.bank_name and\
                                    profile.settlement_account and profile.correspondent_account and\
                                    profile.bik and profile.bank_address and profile.kpp and profile.okpo and\
                                    profile.phones):
                                    check_and_add_needed_docs(user)
                                    for slug in slugs_list:
                                        app = get_application(user, slug)
                                        if app:
                                            url = reverse("signing_application_to_financial_document", kwargs={ "app_id": app.id })
                                            return HttpResponseRedirect(url)
                            if not profile.is_juridical:
                                if (profile.last_name and profile.first_name and profile.second_name and profile.sex != None\
                                    and profile.birthday and profile.pasport_serial and profile.when_given_out and \
                                    profile.by_whom_given_out and profile.phones):
                                    check_and_add_needed_docs(user)
                                    for slug in slugs_list:
                                        app = get_application(user, slug)
                                        if app:
                                            url = reverse("signing_application_to_financial_document", kwargs={ "app_id": app.id })
                                            return HttpResponseRedirect(url)
            result = func(request, *args, **kwargs)
            return result
        return wrapper
    return decor


#===============================================================================
# новый декоратор
#===============================================================================

def get_real_application(user):
    try:
        app = FinDocSignApplication.objects.filter(assigned_to=user)
    except:
        app = None
    return app

def create_and_delete_application(request, slug, redirect_after_sign):
    "Удаляет старые заявки и создает новые"
    user = request.user
    app_list = get_real_application(user)
    for app in app_list:  # удаляем все существующие заявки для данного пользователя
        app.delete()
    doc = FinDoc.objects.get(slug=slug)
    if not request.POST:
        request.POST = request.GET
    user_can_cancel = True
    if slug in ('dop_soglashenie_izmenenie_requisites',):
        user_can_cancel = False
    sd = FinDocSignApplication(
        assigned_to=user,
        assigned_at=get_now(),
        findoc=doc,
        user_can_cancel=user_can_cancel,
        service_for_billing="application_from_a_package"
        )
    sd.pickle_params({"redirect_after_sign": redirect_after_sign})
    sd.save()

def decorator_for_sign_applications():
    def decor(func):
        def wrapper(request, *args, **kwargs):
            url_meta = request.META['PATH_INFO']
            user = request.user
            try:
                package_obj = Package_on_connection_of_service.objects.get(url_after_sign=url_meta, user=user, activate=False, deactivate=False)
            except Package_on_connection_of_service.DoesNotExist:
                result = func(request, *args, **kwargs)
                return result

            data = {}
            if package_obj.data:
                data = eval(package_obj.data)
            slugs_list_temp = package_obj.slugs_document
            if data.has_key('package_cancel') or not slugs_list_temp:
                result = func(request, *args, **kwargs)
                return result

            slugs_list = slugs_list_temp.split(', ')
            url_after_sign = package_obj.url_after_sign
            create_and_delete_application(request, slugs_list[0], url_after_sign)
            app = get_application(user, slugs_list[0])
            if app:
                url = reverse("signing_application_to_financial_document", kwargs={ "app_id": app.id })
                return HttpResponseRedirect(url)
            result = func(request, *args, **kwargs)
            return result
        return wrapper
    return decor








