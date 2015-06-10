from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.template import RequestContext


def render_response(request, tmpl, output):
    return render_to_response(tmpl, output, context_instance=RequestContext(request))

class JsonResponse(HttpResponse):
    """
    HttpResponse descendant, which return response with ``application/json`` mimetype.
    """
    def __init__(self, data):
        super(JsonResponse, self).__init__(content=simplejson.dumps(data,ensure_ascii=False), mimetype='application/json')
        
def get_query_string(request, exclude=None):
    params = request.GET.copy()
    if exclude:
        for name in exclude:
            params.pop(name, None)
    return '&'.join(['%s=%s' % (k, v) for k, v in params.items()])
