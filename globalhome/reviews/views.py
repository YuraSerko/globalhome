# -*- coding=utf-8 -*-
from forms import FormForUser, FormForNotAuth, SectionForm
from models import Review, SECTIONS
from lib.paginator import SimplePaginator
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
import datetime
from lib.decorators import render_to
from page.models import LeftBlockMenuPage
from django.contrib.auth.models import User
from django.db.models import Q
from page.views import panel_base_auth
from django.contrib import messages
ALL_SECTIONS = {0:'Все отзывы'}
ALL_SECTIONS.update(SECTIONS)

SECTION_HEADER_ALL = {
    'def': u'Все отзывы',
    0: u'Посмотреть все отзывы',
    1: u'Отзывы о телефонии',
    2: u'Отзывы о дата-центре',
    3: u'Отзывы о доступе в интернет',
    4: u'Остальные отзывы',
}

SECTION_HEADER_MY = {
    'def': u'Мои отзывы',
    0: u'Посмотреть мои отзывы',
    1: u'Мои отзывы о телефонии',
    2: u'Мои отзывы о дата-центре',
    3: u'Мои отзывы о доступе в интернет',
    4: u'Другие мои отзывы',
}

SECTION_ALL = {
    'def': (u'Посмотреть все отзывы клиентов', u'Здесь Вы можете посмотреть все отзывы наших клиентов или оставить свой', u'отзывы, оставить отзыв, отзывы клиентов'),
    0: (u'Все отзывы наших клиентов', u'Посмотреть все отзывы наших клиентов', u'отзывы, оставить отзыв, отзывы клиентов'),
    1: (u'Отзывы о телефонии', u'Посмотреть все отзывы наших клиентов о телефонии', u'отзывы, оставить отзыв, отзывы о телефонии'),
    2: (u'Отзывы о дата-центре', u'Посмотреть все отзывы наших клиентов о дата-центре', u'отзывы, оставить отзыв, отзывы о дата-центре'),
    3: (u'Отзывы о доступе в интернет', u'Посмотреть все отзывы наших клиентов о доступе в интернет', u'отзывы, оставить отзыв, отзывы о доступе в интернет'),
    4: (u'Отзывы о качестве услуг', u'Посмотреть все отзывы наших клиентов о качестве услуг', u'отзывы, оставить отзыв, отзывы о качестве услуг'),
}

SECTION_MY = {
    'def': (u'Мои отзывы', u'Здесь Вы можете посмотреть все Ваши отзывы о нас', u'отзывы, оставить отзыв, мои отзывы'),
    0: (u'Ваши отзывы', u'Посмотреть все отзывы оставленные только Вами', u'отзывы, оставить отзыв, Ваши отзывы'),
    1: (u'Ваши отзывы о телефонии', u'Посмотреть все отзывы о телефонии оставленные только Вами', u'отзывы, отзывы о дата-центре, Ваши отзывы'),
    2: (u'Ваши отзывы о дата-центре', u'Посмотреть все отзывы о дата-центре оставленные только Вами', u'отзывы, отзывы о дата-центре, Ваши отзывы'),
    3: (u'Ваши отзывы о доступе в интернет', u'Посмотреть все отзывы о доступе в интернет оставленные только Вами', u'отзывы, отзывы о доступе в интернет, Ваши отзывы'),
    4: (u'Ваши отзывы о качестве услуг', u'Посмотреть все отзывы о качестве услуг оставленные только Вами', u': отзывы, отзывы о качестве услуг, Ваши отзывы'),
}


def isint(a):
    try:
        int(a)
        return True
    except ValueError:
        return False

def write_review(request):
    context = {}
    forms = get_forms(request)
    if(request.POST.has_key('submit_review')):
        form = form_clean(request, forms)
        if form._get_errors():
            messages = []
            errors = form._get_errors()
            for key, value in errors.items():
                messages.append("%s - %s\t" % (form.fields[key].label, value[0]))
            context['review_error'] = messages
            context['review_form'] = form
            context['section_form'] = None if len(forms) <= 1 else forms[1]
        else:
            forms = get_forms(request)
            if len(forms) > 1:
                context['section_form'] = forms[1]
            context['review_form'] = forms[0]
        return context
    if len(forms) > 1:
        context['section_form'] = forms[1]
    context['review_form'] = forms[0]
    return context


def get_forms(request):
    forms = []
    if (request.user.is_authenticated()):
        forms.append(FormForUser)
    else:
        forms.append(FormForNotAuth)
    urls_of_pages = LeftBlockMenuPage.objects.all().values_list('url', flat=True)
    if not(request.GET.has_key('section') and request.GET['section'] in SECTIONS.keys() or request.path_info in urls_of_pages):
        forms.append(SectionForm)
    return forms


def form_clean(request, forms):
    section = None
    message = ''
    if len(forms) > 1:
        section_form = forms[1]
        section_form = section_form(request.POST.copy())
        if section_form.is_valid():
            section = section_form.cleaned_data['section']
    form = forms[0]
    form = form(request.POST.copy())
    if form.is_valid():
        form.cleaned_data
        review = Review.objects.create()
        review.created_at = datetime.datetime.now()
        review.is_public = False
        review.comment = form.cleaned_data['comment']
        if (request.user.is_authenticated()):
            review.user = request.user
            review.user_name = request.user.username
            review.user_email = request.user.email
        else:
            review.user_name = form.cleaned_data['name']
            review.user_email = form.cleaned_data['email']
        parent = None
        if(request.GET.has_key('parent') and request.GET['parent']):
            try:
                parent = Review.objects.get(id=int(request.GET['parent']))
            except:
                message = '%s%s' % (message, '%s, некорректно указан адрес ответного сообщения. Ваш отзыв принят за новый.\n' % (review.user_name))
        if(request.GET.has_key('section') and request.GET['section'] in SECTIONS.keys()):
            review.section = request.GET['section']
        else:
            if request.path_info in LeftBlockMenuPage.objects.all().values_list('url', flat=True) and not(section):
                page = LeftBlockMenuPage.objects.all().filter(url=request.path_info)[0]
                while page.parent != None and not(page.name in SECTIONS.values()):
                    page = page.parent
                if page.name in SECTIONS.values():
                    index = SECTIONS.values().index(page.name)
                    section = SECTIONS.keys()[index]
            elif(parent):
                section = parent.section
            if(not(section)):
                section = '4'
        review.section = section
        review.parent = parent
        review.save()
        message = '%s%s' % (message, u'Спасибо %s за ваш отзыв, который будет рассмотрен администрацией сайта.\n И в случае корректности будет опубликован.' % (review.user_name))
        messages.add_message(request, 20, message, 'review')
    return form


def get_queryset_in_list(parent, level, is_public, id_list):
    queryset = Review.objects.all().filter(parent=parent).filter(is_public=is_public).filter(id__in=id_list).order_by('-created_at')if is_public != None else Review.objects.all().filter(parent=parent).filter(id__in=id_list).order_by('-created_at')
    result = [(level * 4, parent, ALL_SECTIONS[parent.section]), ]
    for qs in queryset:
        result += get_queryset_in_list(qs, level + 1, is_public, id_list)
    return result


@render_to('review/review_page.html')
def review_page(request):
    context = {'references':[]}
    context['breadcrumbs'] = [{'href':u'/', 'value':u'Главная', 'zspan':'->'}, {'href':'', 'value':u'Отзывы', 'zspan':''}]
    if (request.user.is_authenticated()):
       context['references'].append({'label':'Мои отзывы', 'href':'/reviews/my_reviews'})
    context['references'].append({'label':u'Просмотреть отзывы', 'href':'/reviews/all_reviews'})
    context['references'].append({'label':u'Оставить отзыв', 'href':'/reviews/write_review'})
    context['objects'] = []
    context['header1'] = u'Отзывы'
    return panel_base_auth(request, context)


@render_to('review/review_page.html')
def my_reviews_page(request):
    context = {}
    message = ''
    filter_by_section = None
    context.update(write_review(request))
    if request.POST.has_key('submit_review'):
        return HttpResponseRedirect(request.path)
    if not(request.user.is_authenticated()):
        message = '%s%s' % (message, u'Извините, для просмотра ваших отзывов необходимо авторизоваться')
        messages.add_message(request, 20, message, 'review')
        return HttpResponseRedirect('/reviews/')
    user = request.user
    if (request.GET.has_key('section') and isint(request.GET['section']) and int(request.GET['section']) in ALL_SECTIONS.keys()):
        filter_by_section = None if not(int(request.GET['section']) in SECTIONS.keys()) else int(request.GET['section'])
        context['title'] = 'Мои отзывы' if not(filter_by_section) else u'Отзывы в разделе %s' % (SECTIONS[filter_by_section])
        context['section'] = None if not(filter_by_section) else(SECTIONS[filter_by_section])
        if filter_by_section:
            queryset = Review.objects.all().filter(user=user).filter(section=filter_by_section).order_by('-created_at')
        else:
            queryset = Review.objects.all().filter(user=user).order_by('-created_at')
    else:
        if request.GET.has_key('section'):
            return HttpResponseRedirect(request.path)
        context['title'] = 'Мои отзывы'
        queryset = Review.objects.all().filter(user=user).order_by('-created_at')
        filter_by_section = None
    context['sections'] = ALL_SECTIONS
    is_public = None if not(request.GET.has_key('is_public')) else request.GET['is_public'] == '1'
    if (request.GET.has_key('delete')):
        try:
            review_object = Review.objects.get(id=int(request.GET['delete']))
            if (user == review_object.user):
                review_object.delete()
        except Exception:
            pass

    id_list, review_list = Review.objects.all().filter(Q(is_public=True) | Q(user=user)), []
    for review in queryset:
        while review.parent != None and (review.parent.is_public == True or review.parent.user == user):
            review = review.parent
        if review not in review_list:
            review_list.append(review)
    context['breadcrumbs'] = [{'href':u'/', 'value':u'Главная', 'zspan':'->'}, {'href':'/reviews/', 'value':u'Отзывы', 'zspan':'->'},
                               {'href':'', 'value':context['title'], 'zspan':''}]
    paginator = Paginator(review_list, 5)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        review_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        review_list = paginator.page(paginator.num_pages)
    result = []
    for qs in review_list:
        result += get_queryset_in_list(qs, 0, is_public, id_list)
    context['objects'] = result
    context['page'] = review_list
    context['user_reviews'] = True

    if not request.GET.has_key('section') or filter_by_section == None:
        filter_by_section = 'def'
    has_page = request.GET.has_key('page')

    context['header1'] = SECTION_HEADER_MY[filter_by_section]
    context['meta_title'] = SECTION_MY[filter_by_section][0] + (u'. Страница %s' % page if has_page else '')
    context['meta_description'] = SECTION_MY[filter_by_section][1] + (u'. Страница %s' % page if has_page else '')
    context['meta_keywords'] = SECTION_MY[filter_by_section][2] + (u', страница %s' % page if has_page else '')

    return panel_base_auth(request, context)


@render_to('review/review_page.html')
def all_reviews_page(request):
    context = {}
    context['breadcrumbs'] = [{'href':u'/', 'value':u'Главная', 'zspan':'->'}, {'href':'/reviews/', 'value':u'Отзывы', 'zspan':'->'},
                              {'href':'', 'value':u'Просмотреть отзывы', 'zspan':''}]
    filter_by_section = None
    if (request.GET.has_key('section')and isint(request.GET['section']) and int(request.GET['section']) in ALL_SECTIONS.keys()):
        filter_by_section = None if not(int(request.GET['section']) in SECTIONS.keys()) else int(request.GET['section'])
        context['title'] = u'Все отзывы' if not(filter_by_section) else  u'Отзывы раздела %s' % (SECTIONS[filter_by_section])
        context['section'] = None if not(filter_by_section) else(SECTIONS[filter_by_section])
    else:
        if request.GET.has_key('section'):
            return HttpResponseRedirect(request.path)
        context['title'] = 'Все отзывы'
        filter_by_section = None
    context['sections'] = ALL_SECTIONS
    context.update(write_review(request))
    if request.POST.has_key('submit_review') and not(context.has_key('review_error')):
        return HttpResponseRedirect(request.path)

    superuser = True if request.user in User.objects.all().filter(is_staff=True).filter(is_active=True) else False
    if (request.GET.has_key('public') or request.GET.has_key('hide') or request.GET.has_key('delete')):
        review_object = Review.objects.get(id=int(request.GET['public'] if request.GET.has_key('public') else\
                                                  request.GET['hide'] if request.GET.has_key('hide') else request.GET['delete']))
        user = review_object.user if review_object.user else None
        if superuser or user:
            if (request.GET.has_key('delete')):
                review_object.delete()
            if (request.GET.has_key('public') or request.GET.has_key('hide'))and superuser:
                review_object.is_public = True if (request.GET.has_key('public')) else False
                review_object.save()
        return HttpResponseRedirect(request.path + '?%spage=%s' % ('' if not(request.GET.has_key('section')) else 'section=%s&' % request.GET['section'] ,
                                                                     1 if not(request.GET.has_key('page')) else request.GET['page']))
    queryset = Review.objects.all().order_by('-created_at') if superuser else Review.objects.all().filter(is_public=True).order_by('-created_at')
    if filter_by_section:
        queryset = queryset.filter(section=filter_by_section)

    id_list, review_list = queryset.values_list('id', flat=True), []
    for  qs in queryset:
        if qs.parent == None:
            review_list.append(qs)
    paginator = Paginator(review_list, 5)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError as e:
        page = 1
    try:
        review_list = paginator.page(page)
    except Exception as e:
        review_list = paginator.page(paginator.num_pages)
    result = []
    for qs in review_list:
        result += get_queryset_in_list(qs, 0, None if superuser else True, id_list)
    context['objects'] = result
    context['superuser'] = superuser
    context['page'] = review_list
    context['user_reviews'] = superuser == True

    if not request.GET.has_key('section') or filter_by_section == None:
        filter_by_section = 'def'
    has_page = request.GET.has_key('page')

    context['header1'] = SECTION_HEADER_ALL[filter_by_section]
    context['meta_title'] = SECTION_ALL[filter_by_section][0] + (u'. Страница %s' % page if has_page else '')
    context['meta_description'] = SECTION_ALL[filter_by_section][1] + (u'. Страница %s' % page if has_page else '')
    context['meta_keywords'] = SECTION_ALL[filter_by_section][2] + (u', страница %s' % page if has_page else '')

    return panel_base_auth(request, context)


@render_to('review/review_page.html')
def write_review_page(request, update_context={}):
    context = {}
    context['title'] = u''
    context['breadcrumbs'] = [{'href':u'/', 'value':u'Главная', 'zspan':'->'},
                              {'href':'/reviews/', 'value': u'Отзывы', 'zspan': '->'}, {'href':'', 'value': u'Оставить отзыв', 'zspan':''}]
    context['objects'] = []
    context['header1'] = u'Написать отзыв'
    context['page_text'] = True
    context.update(write_review(request))
    if(context.has_key('review_error')):
        return context
    if request.POST.has_key('submit_review'):
        return HttpResponseRedirect('/reviews/all_reviews/')
    return panel_base_auth(request, context)




