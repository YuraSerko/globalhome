# -*- coding=utf-8 -*-
from lib.decorators import render_to, login_required
from django.http import HttpResponseRedirect
from models import Queue, Agent
from forms import QueueForm, NumberDynForm, ExtNumberDynForm  # , QueueEditForm
from datetime import datetime
from telnumbers.models import TelNumber  # , TelNumbersGroup, TelNumbersGroupNumbers
from externalnumbers.models import ExternalNumber
# from django.db.utils import IntegrityError
from django.http import Http404
from django.core.urlresolvers import reverse
from django.db import transaction, connections
# from django.db.models import Q
# from django.forms import ValidationError
from fs.models import Record_talk_activated_tariff
from django.conf import settings
# from settings import BILLING_DB, FREESWITCH
from django.forms.formsets import formset_factory
from django.utils.functional import curry
# import os

def display(number, name):
    if name:
        number += '(%s)' % name
    return number

def get_context(**kwargs):
    context = {}
    for key in kwargs:
        context[key] = kwargs[key]
    return context

def check_record_talk_activated_tariff(billing_account_id):
    tariffs = Record_talk_activated_tariff.objects.filter(billing_account_id=billing_account_id)
    now = datetime.now()
    for tariff in tariffs:
        if not tariff.date_deactivation or (not tariff.blocked and tariff.date_deactivation > now):
            return True
    return False

def work_days_to_week_array(work_days):
    '''Переводит строку '1..7' - номера дней недели в список коротких названий дней недели'''
    if work_days == '1234567':
        return [u'Каждый день']
    week_days = {'1' : u'Пн', '2' : u'Вт', '3' : u'Ср',
                 '4' : u'Чт', '5' : u'Пт', '6' : u'Сб', '7' : u'Вс'}
    week_array = [week_days[day] for day in list(work_days)]
    return week_array

def get_formated_time(time_begin, time_end, enabled):
    '''Возвращает время в формате "%H:%M - %H:%M" или "Всегда"'''
    if enabled:
        return time_begin.strftime('%H:%M') + " - " + time_end.strftime('%H:%M')
    else: return 'Всегда'

def formsets_init(account_id, queue=None):
    check = lambda all, q: False if q in all else all
    intnumbers = [number for number in TelNumber.objects.filter(account=account_id) if not check(number.queue_set.all(), queue)]
    extnumbers = [number for number in ExternalNumber.objects.filter(account=account_id) if not check(number.queue_set.all(), queue)]
    formset_intnumber = formset_factory(NumberDynForm)
    formset_intnumber.form = staticmethod(curry(NumberDynForm, numbers=intnumbers))
    formset_extnumber = formset_factory(ExtNumberDynForm)
    formset_extnumber.form = staticmethod(curry(ExtNumberDynForm, extnumbers=extnumbers))
    return intnumbers, extnumbers, formset_intnumber, formset_extnumber

def formsets_post_init(request, formset_intnumber, formset_extnumber):
    formset_intnumber = formset_intnumber(request.POST, prefix='number')
    formset_extnumber = formset_extnumber(request.POST, prefix='extnumber')
    return formset_intnumber, formset_extnumber

def formsets_get_init(formset_intnumber, formset_extnumber, *init):
    if init:
        init_intnumbers, init_extnumbers = init
        formset_intnumber = formset_intnumber(initial=init_intnumbers, prefix='number')
        formset_extnumber = formset_extnumber(initial=init_extnumbers, prefix='extnumber')
    else:
        formset_intnumber = formset_intnumber(prefix='number')
        formset_extnumber = formset_extnumber(prefix='extnumber')
    return formset_intnumber, formset_extnumber

def formsets_save(queue, formset_intnumber, formset_extnumber, intnumbers, extnumbers):
    if formset_intnumber.is_valid():
        internal_number_ids = [form_intnumber.cleaned_data.get('number_dyn') for form_intnumber in formset_intnumber.forms]
        internal_numbers = [number for number in intnumbers or () if str(number.id) in internal_number_ids]
        queue.internal_numbers = internal_numbers
    if formset_extnumber.is_valid():
        external_number_ids = [form_extnumber.cleaned_data.get('extnumber') for form_extnumber in formset_extnumber.forms]
        external_numbers = [number for number in extnumbers or () if str(number.id) in external_number_ids]
        queue.external_numbers = external_numbers

@login_required
@render_to('queue_list.html')
def queue_list(request):
    bac = request.user.get_profile().billing_account
    context = {}
    context['record_activated'] = check_record_talk_activated_tariff(bac.id)
    queues = Queue.objects.filter(billing_account_id=bac.id).order_by('created_date')
    queues = [{'id' : q.id,
               'name' : q.name,
               'internal_numbers' : [display(number.tel_number, number.person_name) for number in q.internal_numbers.all()],
               'external_numbers' : q.external_numbers.all().values_list('number', flat=True),
               'number_queue' : q.number_queue,
               'record' : q.record_enabled,
               'time' : get_formated_time(q.time_begin, q.time_end, q.time_enabled),
               'work_day' : work_days_to_week_array(q.work_day)} for q in queues]
    context['queues'] = queues or None
    return context

@login_required
@render_to('queue_form.html')
def queue_create(request):
    bac = request.user.get_profile().billing_account
    intnumbers, extnumbers, formset_intnumber, formset_extnumber = formsets_init(bac.id)
    if request.POST:
        if request.POST.get('save'):
            form = QueueForm(request.POST, request.FILES, bac=bac)
            formset_intnumber, formset_extnumber = formsets_post_init(request, formset_intnumber, formset_extnumber)
            if form.is_valid():
                queue = form.save(request=request)
                try:
                    with transaction.commit_on_success(using=settings.BILLING_DB):
                        formsets_save(queue, formset_intnumber, formset_extnumber, intnumbers, extnumbers)
                except Exception, e:
                    print 'queue_create Exception', e
                    raise Http404
                return HttpResponseRedirect(reverse('queue_list'))
        else:
            return HttpResponseRedirect(reverse('queue_list'))
    else:
        formset_intnumber, formset_extnumber = formsets_get_init(formset_intnumber, formset_extnumber)
        form = QueueForm(bac=bac)
    return get_context(form=form, formset_intnumber=formset_intnumber, formset_extnumber=formset_extnumber, title=u'Подключение очереди', button=u'Создать')

@login_required
@render_to('queue_form.html')
def queue_edit(request, queue_id):
    queue_id = int(queue_id)
    bac = request.user.get_profile().billing_account
    try:
        queue = Queue.objects.get(pk=queue_id)
        if queue.billing_account_id != bac.id:
            print 'queue_edit queue.billing_account_id != billing_account_id'
            raise Http404
    except Queue.DoesNotExist, e:
        raise Http404  # не нашли очередь с таким id => 404
    intnumbers, extnumbers, formset_intnumber, formset_extnumber = formsets_init(bac.id, queue=queue)
    if request.POST:
        if request.POST.get("save"):
            form = QueueForm(request.POST, request.FILES, bac=bac, queue=queue)
            formset_intnumber, formset_extnumber = formsets_post_init(request, formset_intnumber, formset_extnumber)
            if form.is_valid():
                queue = form.save(request=request)
                try:
                    with transaction.commit_on_success(using=settings.BILLING_DB):
                        formsets_save(queue, formset_intnumber, formset_extnumber, intnumbers, extnumbers)
                except Exception, e:
                    print 'queue_create Exception', e
                    raise Http404
                return HttpResponseRedirect(reverse('queue_list'))
        else:
            return HttpResponseRedirect(reverse('queue_list'))
    else:
        init_intnumbers = [{'number_dyn' : number.id} for number in queue.internal_numbers.all()]
        init_extnumbers = [{'extnumber' : number.id} for number in queue.external_numbers.all()]
        formset_intnumber, formset_extnumber = formsets_get_init(formset_intnumber, formset_extnumber, init_intnumbers, init_extnumbers)
        form = QueueForm(bac=bac, instance=queue)
    return get_context(form=form, formset_intnumber=formset_intnumber, formset_extnumber=formset_extnumber, title=u'Редактирование очереди', button=u'Сохранить')

@login_required
@render_to('queue_delete.html')
def queue_delete(request, queue_id):
    bac = request.user.get_profile().billing_account
    try:
        queue = Queue.objects.get(pk=queue_id)
        if queue.billing_account_id != bac.id:
            print 'queue_edit queue.billing_account_id != billing_account_id'
            raise Http404
    except Queue.DoesNotExist, e:
        raise Http404  # не нашли очередь с таким id => 404
    name = queue.name
    if request.POST:
        if request.POST.get('delete'):
            try:
                with transaction.commit_on_success(using=settings.BILLING_DB):
                    agents = Agent.objects.filter(queue_id=queue.id)
                    for agent in agents: agent.delete_from_freeswitch()
                    queue.delete()
            except Exception, e:
                print 'queue_delete Exception', e
                raise Http404
        else:
            return HttpResponseRedirect(reverse('queue_list'))
    else:
        context = {'queue' : name}
        return context
    request.notifications.add(u'Очередь "%s" успешно удалена' % name, 'success')
    return HttpResponseRedirect(reverse('queue_list'))


@login_required
@render_to('queue_agents.html')
def queue_agents(request, queue_id):
    def get_agents_with_state(queue):
        agents = Agent.objects.filter(queue_id=queue.id).order_by('internal_number__tel_number')
        cur = connections[settings.BILLING_DB].cursor()
        cur.execute("SELECT originate_string FROM fifo_outbound WHERE fifo_name = '%s'" % queue.id)
        agents_freeswitch = [a[0][-7:] for a in cur.fetchall()]
        transaction.commit_unless_managed(settings.BILLING_DB)
        agents = [{'id' : a.id, 'number' : a.internal_number.tel_number, 'owner' : a.internal_number.person_name, 'password' : a.internal_number.password, 'online' : a.internal_number.tel_number in agents_freeswitch} for a in agents]
        return agents

    def delete_agents(queue, agents):
        for agent_id in agents:
            agent = Agent.objects.get(pk=agent_id)
            agent.delete_from_freeswitch()

    def add_agents(queue, agents):
        # import ESL
        from lib.esl import ESL
        con = ESL.ESLconnection(settings.FREESWITCH['fs2']['ESL_HOST'], settings.FREESWITCH['fs2']['ESL_PORT'], settings.FREESWITCH['fs2']['ESL_PASSWORD'])
        for agent_id in agents:
            agent = Agent.objects.get(pk=agent_id)
            command = str('api fifo_member add %s {fifo_member_wait=nowait,ignore_early_media=true,loopback_bowout=false}loopback/%s' % (queue.id, agent.internal_number.tel_number))
            con.sendRecv(command)

    try:
        queue = Queue.objects.get(pk=queue_id)
        name = queue.name
        try:
            with transaction.commit_on_success(using=settings.BILLING_DB):
                if request.POST:
                    if request.POST.get('submit_block'):
                        delete_agents(queue, [request.POST.get('submit_block')])
                    elif request.POST.get('submit_unblock'):
                        add_agents(queue, [request.POST.get('submit_unblock')])
                    elif request.POST.get('connect_all'):
                        agents = [a.id for a in Agent.objects.filter(queue_id=queue.id)]
                        add_agents(queue, agents)
                    elif request.POST.get('disconnect_all'):
                        agents = [a.id for a in Agent.objects.filter(queue_id=queue.id)]
                        delete_agents(queue, agents)
                    elif request.POST.get('back'):
                        return HttpResponseRedirect(reverse('queue_list'))
                agents = get_agents_with_state(queue)
        except Exception, e:
            print 'queue_agents Exception', e
            raise Http404
        return {'name' : name, 'agents' : agents, 'fs' : 'fs1'}
    except Exception, e:
        print 'queue_agents Exception', e
        raise Http404
