# -*- coding=UTF-8 -*-
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import REDIRECT_FIELD_NAME
from lib.http import JsonResponse, render_response
from lib.helpers import next
from django.utils.decorators import available_attrs
from findocs.models import Package_on_connection_of_service
from account.models import Profile
from account.forms import ADDRESS_TYPE_LEGAL, ADDRESS_TYPE_POSTAL, ADDRESS_TYPE_PHYSICAL, AddressLegalForm, AddressPostalForm, ProfileJuridicalDataForm, ProfilePhisicalDataForm, AddressPhysicalForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
import datetime
from django.utils import simplejson
from django.core.serializers import serialize
import os, sys
from billing.models import BillserviceAccount
from data_centr.models import Limit_connection_service

try:
    from functools import update_wrapper, wraps
except ImportError:
    from django.utils.functional import update_wrapper, wraps  # Python 2.4 fallback.


def render_to(tmpl):
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if not isinstance(output, dict):
                return output
            return render_to_response(tmpl, output,
                   context_instance=RequestContext(request))
        return wrapper
    return renderer

def ajax_request(func):
    """
    Checks request.method is POST. Return error in JSON in other case.

    If view returned dict, returns JsonResponse with this dict as content.
    """
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if isinstance(response, (dict, list)):
            return JsonResponse(response)
        else:
            return response
    return wrapper
def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """
    if not login_url:
        from django.conf import settings
        login_url = settings.LOGIN_URL

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                try:
                    profile = Profile.objects.get(user=request.user)
                    bill_acc = BillserviceAccount.objects.get(id=profile.billing_account_id)
                    if bill_acc.status == 4:
                        if request.META['PATH_INFO'] in ('/account/block/',):
                            pass
                        else:
                            return HttpResponseRedirect(reverse('account_block'))
                    if not profile.activated_at:
                        if request.META['PATH_INFO'] in ("/account/",):
                            pass
                        else:
                            return HttpResponseRedirect(reverse("account_profile"))
                    if profile.activated_at:
                        if request.META['PATH_INFO'] in ("/account/profile/",):
                            pass
                        else:
                            if not (profile.is_card or profile.is_hostel):
                                data_valid = True
                                package = False
                                try:
                                    package_obj = Package_on_connection_of_service.objects.get(user=request.user,
                                                                           activate=False,
                                                                           deactivate=False)
                                    url = package_obj.url_after_sign
#                                    if url == reverse('account_profile_edit'):
#                                        data_valid = False
                                    package = True
                                except Package_on_connection_of_service.DoesNotExist:
                                    pass
                                if data_valid:
                                    if package:
                                        if profile.is_juridical:
                                            if profile and profile.address(ADDRESS_TYPE_LEGAL) and profile.address(ADDRESS_TYPE_POSTAL):
                                                profile_dict = simplejson.loads(serialize('json', [profile]))[0]['fields']
                                                legal_address_dict = simplejson.loads(serialize('json', [profile.address(ADDRESS_TYPE_LEGAL)]))[0]['fields']
                                                postal_address_dict = simplejson.loads(serialize('json', [profile.address(ADDRESS_TYPE_POSTAL)]))[0]['fields']
                                                corporate_form = ProfileJuridicalDataForm(profile_dict)
                                                legal_address_form = AddressLegalForm(legal_address_dict)
                                                postal_address_form = AddressPostalForm(postal_address_dict)
                                                if not 3 == len(filter(lambda x: x.is_valid(), [corporate_form, legal_address_form, postal_address_form])):
                                                    request.notifications.add(_(u'В Вашем профиле заполнены не все поля!'), "warning")
                                                    return HttpResponseRedirect(reverse("account_profile_edit"))
                                            else:
                                                request.notifications.add(_(u'В Вашем профиле заполнены не все поля!'), "warning")
                                                return HttpResponseRedirect(reverse("account_profile_edit"))
                                        if not profile.is_juridical:
                                            if profile and profile.address(ADDRESS_TYPE_PHYSICAL):
                                                profile_dict = simplejson.loads(serialize('json', [profile]))[0]['fields']
                                                personal_address_dict = simplejson.loads(serialize('json', [profile.address(ADDRESS_TYPE_PHYSICAL)]))[0]['fields']
                                                personal_form = ProfilePhisicalDataForm(profile_dict)
                                                physical_address_form = AddressPhysicalForm(personal_address_dict)
                                                if not 2 == len(filter(lambda x: x.is_valid(), [personal_form, physical_address_form])):
                                                    request.notifications.add(_(u'В Вашем профиле заполнены не все поля!'), "warning")
                                                    return HttpResponseRedirect(reverse("account_profile_edit"))
                                            else:
                                                request.notifications.add(_(u'В Вашем профиле заполнены не все поля!'), "warning")
                                                return HttpResponseRedirect(reverse("account_profile_edit"))
                                        if url == reverse('add_inet_final'):
                                            data = eval(package_obj.data)
                                            if (profile.is_juridical and not data['type_face'] in ('legal_entity',)) or \
                                                (not profile.is_juridical and not data['type_face'] in ('individual', 'cottage_settlement',)):
                                                package_obj.deactivate = True
                                                package_obj.save()
                                                if (profile.is_juridical and not data['type_face'] in ('legal_entity',)):
                                                    request.notifications.add(_(u'Вы зарегистрированы как юридическое лицо и попытались подключить интернет для физических лиц!'), "warning")
                                                elif (not profile.is_juridical and not data['type_face'] in ('individual', 'cottage_settlement',)):
                                                    request.notifications.add(_(u'Вы зарегистрированы как физическое лицо и попытались подключить интернет для юридических лиц!'), "warning")
                                                return HttpResponseRedirect(reverse("account_profile"))
                                        url_cancel = package_obj.url_after_cancel
                                        meta = request.META['PATH_INFO']
                                        a = meta.find("/account/findocs/applications/sign/")
#                                        if meta == url or meta == url_cancel or a != -1:
                                        if meta == url or a != -1:
                                            pass
                                        else:
                                            return HttpResponseRedirect(url)
                except Exception, e:
                    print "error in decorators: %s" % e
                    exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print "Exception in decorators: file:%s line:%s" % (fname, exc_tb.tb_lineno)
                return view_func(request, *args, **kwargs)
            path = next(request)
            tup = login_url, redirect_field_name, path
            return HttpResponseRedirect('%s?%s=%s' % tup)
        return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
    return decorator


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user is logged in and not preliminary logged,
    redirecting to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(), redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def login_required_job(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user is logged in and not preliminary logged,
    redirecting to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(), redirect_field_name=redirect_field_name, login_url='/work/work_need_login'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

url_reverse = {'no service':'service_choice', 'telephony':'account_profile', 'data centr':'my_data_centr', 'internet':'internet'}
def limit_con_service(spis_service=[], section_type='no service'):
    def renderer(func):
        def wrapper(request, *args, **kwargs):
            print 'wrap 1'
            def out(request):
                request.notifications.add(u'К сожалению, Вы больше не можете подключать данную услугу \
                                            в связи с многочисленными неуплатами по данному типу услуг. \
                                            Для подключения обратитесь в администрацию', "error")
                return url_reverse[section_type]
            if spis_service:
                user = request.user
                bill_acc = Profile.objects.get(user=user).billing_account
                limit_qs = Limit_connection_service.objects.filter(bill_acc=bill_acc, service_type__id__in=spis_service)
                if not limit_qs:
                    return func(request, *args, **kwargs)
                else:
                    for limit_obj in limit_qs:
                        if limit_obj.count_limit <= 0:
                            print 0
                            return HttpResponseRedirect(reverse(out(request)))
                return func(request, *args, **kwargs)
            else:
                return HttpResponseRedirect(reverse(out(request)))
        return wrapper
    return renderer


def check_perm(perm):
    def renderer(func):
        def wrapped(request, *args, **kwargs):
            user = request.user
            if user.is_authenticated():
                if user.has_perm(perm):
                    return func(request, *args, **kwargs)
                raise PermissionDenied()
            raise Http404
        return wrapped
    return renderer

