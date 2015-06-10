# -*- coding: utf-8 -*-
from base64 import urlsafe_b64encode, urlsafe_b64decode
from urllib import unquote
from urlparse import urlparse, urlunparse
try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

from django.core.urlresolvers import reverse as _reverse
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils.http import urlquote, urlencode

def reverse(view_name, *args, **kwargs):
    return _reverse(view_name, args=args, kwargs=kwargs)


#def get_object_or_404_ajax(*args, **kwargs):
#    try:
#        return get_object_or_404(*args, **kwargs)
#    except Http404, e:
#        raise Ajax404, e
NEXT_CODING_PREFIX = 'b64-'

def redirect(request, next_only=None, with_query=True):
    """
    Get appropriate url for redirect.
    If ``next_only`` is not None:
    if ``next`` is not found in GET params, returns ``next_only`` (this should be a redirect url string).
    """
    reverse_url = request.META.get('HTTP_REFERER', '/') if not next_only else next_only
    next = request.REQUEST.get('next', '')
    if len(next) != 0:
        #::TODO:: - get a checking is this URL from our site

        # В next может передаваться урл, содержащий get-параметры,
        # в том числе и кириллические символы.
        # На данном этапе джанга уже перевела это всё в юникод,
        # то есть next - это юникодная строка. Поскольку результат этой
        # функции (redirect) как правило передаётся в HttpResponseRedirect,
        # а попадание в него юникодной строки, которую нельзя конвертировать в ANCII,
        # вызовет UnicodeEncodeError, мы должны закодировать здесь url и get-параметры.

        if next.startswith(NEXT_CODING_PREFIX):
            next = urlsafe_b64decode(next[len(NEXT_CODING_PREFIX):].encode('utf-8'))

        parse_result = urlparse(next)
        if with_query:
            query = parse_qs(parse_result.query)

            # По идее, здесь нужно было бы выполнить query = urlencode(query),
            # но при этом список значений кодируется почему-то как строка,
            # то есть [1] превращается в '[1]', и вот это, включая квадратные скобки,
            # кодируется. Пришлось написать вручную.
            # TODO: разобраться, в чём тут дело.
            newquery = {}
            for k, vlist in query.items():
                newquery[str(urlquote(k))] = ','.join([urlquote(v) for v in vlist])
            query = '&'.join(['%s=%s' % (k,v) for k,v in newquery.items()])
        else:
            query = ''

        reverse_url = urlunparse(parse_result[0:2] + (urlquote(parse_result[2]),) + (parse_result[3],) + (query,) + parse_result[5:])

    return reverse_url

def next(request):
    get_params = request.GET.copy()
    if 'next' in get_params:
        del get_params['next']
    url = "%s%s%s" % (request.path, get_params and "?" or "", "&".join(["%s=%s" % (i,j) for i,j in get_params.items()]))
    if isinstance(url, unicode):
        url = url.encode('utf-8')
    next = '%s%s' % (NEXT_CODING_PREFIX, urlsafe_b64encode(url))
    return next

def next_processor(request):
    """context processor to putting next into the context"""
    return {'next':next(request)}

