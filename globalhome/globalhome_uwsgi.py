import os
import sys
import django.core.handlers.wsgi
# Redirect stdout to comply with WSGI
#sys.stdout = sys.stderr
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings_globalhome'
application = django.core.handlers.wsgi.WSGIHandler()
