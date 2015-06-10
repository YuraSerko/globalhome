# coding: utf-8
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.sites.models import Site

class HighMiddleware(object):
    def process_request(self, request):
        settings.GLOBAL_OBJECTS["request"] = request
        host = request.get_host()
        if host[:3].upper() == "WWW":
            return HttpResponseRedirect("http://%s" % (Site.objects.get_current().domain) + request.path)


