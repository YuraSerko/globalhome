# -*- coding=utf-8 -*-

from my_ivr import list_ivr, ivr_delete, ivr_edit, create_ivr, ajax_check_ivr
from list_number import groups_list, groups_list_add, groups_list_delete, groups_list_fixedit
from django.conf import settings  # @UnusedImport
from django.db import connections  # @UnusedImport
from get_fax import list_getfax, create_getfax, delete_getfax, ajax_check
from voice_mail import list_vm, create_vm, delete_vm
from obzvon import obzvon, obzvon_new, obzvon_preold_ajax, obzvon_preold, obzvon_repeat, obzvon_delete, obzvon_edit
from queue import *
from record_talk import *
from models import Record_talk_tariff, Record_talk_activated_tariff, Record_talk
from settings import *
from gateway import list_gateway, add_gateway, delete_gateway
from account.views import RQ2QS
from lib.http import get_query_string
from django.http import HttpResponseRedirect, HttpResponse
from fs.models import NumberTemplateRule, NumberTemplates
from fs.forms import NumberTemplate
#from settings import BILLING_DB, MEDIA_ROOT, FREESWITCH
#import paramiko, scp
#from scp import SCPClient
#from django.http import Http404
#from string import split
#from ivr.models import create_myivr_temp, create_myivr
from lib.decorators import render_to, login_required
from django.utils.translation import ugettext_lazy as _
#from django.http import HttpResponseRedirect, HttpResponseNotFound
from lib.sms import send_sms1

@login_required
@render_to('transfer_call.html')
def send_esemes(request):
    context = {}
    send_sms1("375293151090", "sms_text", log=None)
    context["title"] = _(u"Перевод вызова smsmsmsms")
    context["text_help"] = """smsmsmsmsms"""
    context['current_view_name'] = 'transfer_call_help'
    return context

@login_required
@render_to('transfer_call.html')
def transfer_call_help(request):
    context = {}
    context["title"] = _(u"Перевод вызова")
    context["text_help"] = """Для того чтобы перевести вызов необходимо во время разговора набрать на своем телефоне *1номер абонента#. После этого Вы соединитесь с тем абонентом номер которого Вы набрали. В случае если абонент согласен принять вызов, Вам необходимо просто повесить трубку, после чего оба пользователя свяжуться между собой. В случае если абонент против принять вызов, то повесить трубку необходимо ему, после чего Вы вернетесь к предыдущему разговору."""
    context['current_view_name'] = 'transfer_call_help'
    return context


@login_required
@render_to('record_balance.html')
def record_balance(request):
    from lib.paginator import SimplePaginator
    from account.forms import BalanceFilterForm, first_date, last_date
    from datetime import timedelta
    import datetime, time


    profile = request.user.get_profile()
    try:
        record_talk_tariff_active = Record_talk_activated_tariff.objects.get(Q(billing_account_id=profile.billing_account_id) & \
                                                                            Q(date_activation__lt=datetime.datetime.now()) & \
                                                                            (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now())))
    except Exception, e:
        print "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
        print e
        request.notifications.add(_(u'У Вас не подключена данная услуга. Вы можете выбрать тариф и подключить её ниже'), 'success')
        return HttpResponseRedirect("/account/record_talk/list_record_tariff/")
    if 'filter' in request.GET:
        form = BalanceFilterForm(request.GET)
    else:
        form = BalanceFilterForm()
    filename = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")) + "%s" % request.user + ".csv"
    link = "/media/billed_calls_files/%s" % filename
    date_from = first_date()
    date_to = last_date()
    caller_number = called_number = group = call_type = call_length_type = ""
    order_by = "datetime"
    order_type = "DESC"
    if "order_by" in request.GET:
            order_by = request.GET.get("order_by")
    if "order_type" in request.GET:
            order_type = request.GET.get("order_type")
    download = False
    if request.GET.get("download"):
        download = True
    if form.is_valid():
        date_from = form.cleaned_data["date_from"]
        date_to = form.cleaned_data["date_to"]
        if date_from and date_to:
            if date_from > date_to:
                request.notifications.add(_(u"You have selected an incorrect date interval!"), "warning")
                return HttpResponseRedirect("/account/record_balance/")
            else:
                if (date_to.month - date_from.month) > 2 or date_from.year != date_to.year:
                    request.notifications.add("Разница между 'дата с' и  'дата по' должна быть не более двух месяцев!", "warning")
                    return HttpResponseRedirect("/account/record_balance/")
                if date_from < (datetime.date.today() - timedelta(days = 365)):
                    request.notifications.add("'Дата с' должна быть не более чем год назад!", "warning")
                    return HttpResponseRedirect("/account/record_balance/")
        caller_number = form.cleaned_data["caller_number"]
        called_number = form.cleaned_data["called_number"]
        group = form.cleaned_data["group"]
        call_length_type = form.cleaned_data["call_length_type"]
        call_type = form.cleaned_data["call_type"]
    if date_to:
        date_to += timedelta(days=1)

    rq = RQ2QS(# !!!!!!!!!! вероятно здесь все же стоит использовать обычный QuerySet,
               # но со всякими дополнительными параметрами, вроде QuerySet.extra(...)
               # (для увеличения производительности)
        profile.billing_account_id,
        date_from,
        date_to,
        caller_number = caller_number,
        called_number = called_number,
        download = download,
        filename = filename,
        group = group,
        call_length_type = call_length_type,
        call_type = call_type,
        order_by = order_by,
        order_type = order_type,
        record = True
    )
    ######################### ?подсчет статистики ################################
    statistics = {}
    cur = connections[settings.BILLING_DB].cursor()
    cur.execute(rq.make_query(count = True))
    rq_stat = cur.fetchone()
    transaction.commit_unless_managed(BILLING_DB)
    if rq_stat[0] > 0:
        stat_count = rq_stat[0]
        stat_time = "%s:%s" % divmod(int(rq_stat[1] / (rq_stat[0])), 60)
        stat_price = rq_stat[2]
        stat_count_held = 100.0 / float(stat_count) * rq_stat[3]
        stat_total_time = "%s" % (rq_stat[1]/ 60)
        statistics = {
                      'count' : stat_count,
                      'count_held' : stat_count_held,
                      'time' : stat_time,
                      'price' : stat_price,
                      'total_time' : stat_total_time
                      }
    else: statistics = None
    query = get_query_string(request, exclude=("page",))
    paginator = SimplePaginator(rq, 50, "?page=%%s&%s" % query)
    paginator.set_page(request.GET.get("page", 1))
    if request.GET.get("download"):
        fun = paginator.get_page()
        return HttpResponseRedirect(link)
    return {
        "title": _(u"Детализация записанных разговоров"),
        "form": form,
        "transactions": paginator.get_page(),
        "paginator": paginator,
        "language": "ru",  # TODO: implement some algorithm if needed
        "is_juridical": profile.is_juridical,
        "statistics" : statistics,
        "current_view_name": "account_show_tariffs",
    }

def delete_rt(request):
    try:
        print MEDIA_ROOT[:-6] + request.GET['file']
        os.remove(MEDIA_ROOT[:-6] + request.GET['file'])
    except Exception,e:
        print e
    return HttpResponseRedirect("/account/record_talk/listen/%s/" % request.GET['id'])

def ret_context(context, formset_number):
    context["formset_number"] = formset_number
    return context

@login_required
@render_to('number_template.html')
def number_template(request, id_number):
    """
        Новый шаблон
    """
    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    profile = request.user.get_profile()
    context["title"] = _(u"Создание нового шаблона")

    model_template_rules=[]
    existing_number = TelNumber.objects.get(id = id_number)
    ArticleFormSetNumber = formset_factory(NumberTemplate,extra=0)
    ArticleFormSetNumber.form = staticmethod(curry(NumberTemplate))
    #context["select_all_rule"] = NumberTemplateRule.objects.filter(billing_account_id=profile.billing_account_id)
    if not request.POST:
        context["all_account_template"] = NumberTemplates.objects.filter(billing_account_id=profile.billing_account_id)
        try:
            model_template = NumberTemplates.objects.get(id=existing_number.template_out_call_id)
            numb_templ_rule = NumberTemplateRule.objects.filter(numbertemplates=model_template)
            context["select_template"] = model_template.id
            context["select_template_name"] = model_template.name
            for x in numb_templ_rule:
                model_template_rules.append({'name_template':x.name,'template':x.number_template_rule})
            formset_number = ArticleFormSetNumber(initial = model_template_rules, prefix='number')
        except NumberTemplates.DoesNotExist:
            print "DOES NoT EXIST"
            model_template_rules.append({'name_template':'','template':''})
            formset_number = ArticleFormSetNumber(initial = model_template_rules, prefix='number')
    else:
        formset_number = ArticleFormSetNumber(request.POST, prefix='number')
        if formset_number.is_valid():
            if request.POST.get('name_ready_template') != '0':
                model_template = NumberTemplates.objects.get(id=request.POST.get('name_ready_template'))
                model_template.number_template.all().delete()
            else:
                model_template = NumberTemplates()
            model_template.billing_account_id = profile.billing_account_id
            model_template.name = request.POST.get('name_template')
            model_template.save()
            existing_number.template_out_call = model_template
            existing_number.save()

            for form_set_number in formset_number.forms:
                model = NumberTemplateRule()
                model.number_template_rule = form_set_number.cleaned_data['template']
                model.name = form_set_number.cleaned_data['name_template']
                model.billing_account_id = profile.billing_account_id
                model.save()
                model_template.number_template.add(model)

            request.notifications.add(_(u"Шаблон успешно сохранен"), "success")
            return HttpResponseRedirect("/account/phones/") # перейти на страницу со списком
        else:
            return ret_context(context, formset_number)
    return ret_context(context, formset_number)

@render_to('number_template_dynamicform.html')
def changetemplate(request):
    context = {}
    profile = request.user.get_profile()
    model_template_rules=[]
    ArticleFormSetNumber = formset_factory(NumberTemplate,extra=0)
    ArticleFormSetNumber.form = staticmethod(curry(NumberTemplate))
    try:
        model_template = NumberTemplates.objects.get(id=request.GET['templ'])
        numb_templ_rule = NumberTemplateRule.objects.filter(numbertemplates=model_template)
        context["select_template"] = model_template.name
        context["all_account_template"] = NumberTemplates.objects.filter(billing_account_id=profile.billing_account_id)
        for x in numb_templ_rule:
            model_template_rules.append({'name_template':x.name,'template':x.number_template_rule})
        formset_number = ArticleFormSetNumber(initial = model_template_rules, prefix='number')
    except NumberTemplates.DoesNotExist:
        model_template_rules.append({'name_template':'','template':''})
        formset_number = ArticleFormSetNumber(initial = model_template_rules, prefix='number')
        context["select_template"] = 'Новый шаблон'
    return ret_context(context, formset_number)