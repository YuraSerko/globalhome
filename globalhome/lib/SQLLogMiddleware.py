# -*- coding: utf-8 -*-
# $Id: SQLLogMiddleware.py 133 2009-06-16 12:40:55Z oleg $

"""
$Id: SQLLogMiddleware.py 133 2009-06-16 12:40:55Z oleg $

This middleware
in settings.py you need to set

DEBUG=True
DEBUG_SQL=True

# Since you can't see the output if the page results in a redirect,
# you can log the result into a directory:
# DEBUG_SQL='/mypath/...'

MIDDLEWARE_CLASSES = (
    'YOURPATH.SQLLogMiddleware.SQLLogMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    ...)

"""

# Python
import os
import time
import datetime

# Django
from django.conf import settings
from django.db import connection
from django.template import Template, Context

class SQLLogMiddleware:

    start=None

    def process_request(self, request):
        self.start=time.time()
        
        if getattr(settings, 'DEBUG_SQL_SESSION', None):
            if not 'sql_log' in request.session:
                request.session['sql_log'] = []

    def process_response (self, request, response):
        # self.start is empty if an append slash redirect happened.
        debug_sql=getattr(settings, "DEBUG_SQL", False)
        if (not self.start) or not (settings.DEBUG and debug_sql):
            return response

     #   if request.path[:24]=='/ajax/nomenclature_init/':
    #        return response

        timesql=0.0

        for q in connection.queries:
            timesql+=float(q['time'])
        seen={}
        duplicate=0
        for q in connection.queries:
            sql=(q["sql"])
            c=seen.get(sql, 0)
            if c:
                duplicate += 1
            q["seen"]=c
            seen[sql]=c + 1

        t = Template(u'''
            <p>
             <em>request.path:</em> {{ request.path|escape }}<br />
             <em>Total query count:</em> {{ queries|length }}<br/>
             <em>Total duplicate query count:</em> {{ duplicate }}<br/>
             <em>Total SQL execution time:</em> {{ timesql }}<br/>
             <em>Total Request execution time:</em> {{ timerequest }}<br/>
            </p>
            <table class="sqllog">
             <tr>
              <th>Time</th>
              <th>Seen</th>
              <th>SQL</th>
             </tr>
                {% for sql in queries %}
                    <tr>
                     <td>{{ sql.time }}</td>
                     <td align="right">{{ sql.seen }}</td>
                     <td>{{ sql.sql }}</td>
                    </tr>
                {% endfor %}
            </table>
        ''')
        timerequest = round(time.time()-self.start, 3)
        queries = connection.queries
        html = t.render(Context(locals()))
        if debug_sql == True:
            if response.get("content-type", "").startswith("text/html") and not request.path.startswith(settings.MEDIA_URL):
                #Add to response
                in_session_amount = getattr(settings, 'DEBUG_SQL_SESSION', 0)
                if in_session_amount and 'sql_log' in request.session:
                    current = request.session['sql_log'][-(in_session_amount-1):]
                    current.append(html)
                    response.write('<br><br><br>'.join(current))
                    request.session['sql_log'] = current
                    request.session.modified = True
                else:
                    response.write(html)
            return response

        assert os.path.isdir(debug_sql), debug_sql
        outfile=os.path.join(debug_sql, "%s.html" % time.time())
        fd=open(outfile, "wt")
        fd.write('''<html><head><title>SQL Log %s</title></head><body>%s</body></html>''' % (request.path, html.encode('utf-8')))
        fd.close()
        return response
