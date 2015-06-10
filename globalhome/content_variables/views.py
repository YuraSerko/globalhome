# coding: utf-8
from lib.decorators import render_to
from django.contrib.admin.views.decorators import staff_member_required
from models import VariableSet
from django.utils.translation import ugettext as _
from content.TemplateVars import VariableManager
import datetime

@staff_member_required
@render_to("show.html")
def show_vars(request, varset_id):
    context = {}
    start=str(datetime.date.today())
    stop='31.12.9999'
    vs = VariableSet.objects.get(id = varset_id)
    context["title"] = _('All variables in variable set "%s"' % vs.name)
    context["vars_count"] = None
    try:
        VariableManager.start=str(datetime.date.today())
        VariableManager.stop='31.12.9999'
        vm = VariableManager(vs.module)
        vm.load()
        vars = vm.getNamesDict()
        context["vars_count"] = len(vars)
        context["variables"] = vars
    except Exception, e:
        print e

    return context


@staff_member_required
@render_to("show_many.html")
def show_many_vars(request):
    context = {}
    VariableManager.start=str(datetime.date.today())
    VariableManager.stop='31.12.9999'
    if request.GET:
        ids_str = request.GET.get("ids")
        ids = ids_str.split(",")
        variables = []
        for id in ids:
            if id:
                id = int(id)
                try:
                    vs = VariableSet.objects.get(id = id)
                    vm = VariableManager(vs.module)
                    vm.load()
                    variables.append( { "name": vs.name, "vars": vm.getNamesDict() } )
                except Exception, e:
                    print e
                    pass
        context["variables"] = variables
        context["vars_count"] = len(variables)
    else:
        context["error"] = True
    return context


