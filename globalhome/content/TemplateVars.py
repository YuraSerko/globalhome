# coding: utf-8
from django.template import Template, Context
from django.utils.safestring import mark_safe
import log
import datetime
from account.models import Profile
# переделываю подставляемые переменные

class VarValue(object):
    "Базовый класс для всех ЗНАЧЕНИЙ переменных"
    def __init__(self, *args, **kwargs):
        self.is_initialized = False
        self.mark_safe = False
        self.args = args
        self.kwargs = kwargs

    def initValue(self, *args, **kwargs):
        "Тут должно происходить просто какая-то инициализация внутренних переменных этого значения, которые потом будут нужны для получения значения"
        self.is_initialized = True
        self.init_args = args
        self.init_kwargs = kwargs

    def getValue(self):
        "Вот тут должно происходить реальное получение данных и их возвращение"
        if not self.is_initialized:
            #raise Exception("Non-initialized value!")
            return "" # эта функция всегда должна при ошибке вернуть пустую строку! Не должна кидаться исключениями!!!

class Variable(object):
    "Базовый класс для всех переменных"
    def __init__(self, name, description, value):
        self.name = name
        self.description = description
        self.value = value

    def initValue(self, *args, **kwargs):
        "Инициализирует значение. По сути - просто передает ему *args и **kwargs"
        if self.value:
            self.value.initValue(*args, **kwargs)
        else:
            raise Exception("Value object for variable %s is None!" % self.name)

    def __unicode__(self):
        if self.value:
            if self.value.is_initialized:
                result = unicode(self.value.getValue())
                if self.value.mark_safe:
                    return mark_safe(result)
                else:
                    return result
            else:
                return u"<UNINITIALIZED VARIABLE: '%s>'" % self.name
        else:
            return u"<UNASSIGNED VARIABLE: '%s>'" % self.name

class VariableManager(object):

    "Загружает указанный модуль и получает из него переменные"
    def __init__(self, module):
        self.module = module

    def load(self):
        "Загружает переменные из указанного модуля"
        if self.module:
            try:

                exec "from %s import GetVariables" % self.module
                self.variables = GetVariables() #@UndefinedVariable
                exec "del GetVariables"
            except ImportError:
                self.variables = None
                raise Exception("Error loading variables from module '%s'!" % self.module)
        else:
            self.variables = None

    def getNames(self):
        "Возвращает имена и описания загруженных переменных в виде списка tuple"
        names = []
        if self.variables:
            for variable in self.variables:
                names.append((variable.name, variable.description))
        return names

    def getNamesDict(self):
        "Возвращает имена и описания загруженных переменных в виде списка dict"
        names = []
        if self.variables:
            for variable in self.variables:
                names.append(   { "name": variable.name, "description": variable.description }   )
        return names

    def getVariablesDict(self):
        "Возвращает dict с парами (имя=значение переменной) для подставления в шаблон"
        vars = {}
        if self.variables:
            for variable in self.variables:
                vars[variable.name] = variable
        return vars

    def processTemplate(self, template, *args, **kwargs):
        "Подставляет загруженные переменные в указанный текст"
        variables = self.getVariablesDict()
        for varname in variables:
            variables[varname].initValue(*args, **kwargs)
        template = Template(template).render(Context(variables))
        return template

class ModulesManager(object):
    "Класс для загрузки переменных из нескольких модулей"
    def __init__(self):
        self.mans = []

    def load(self, module):
        "Загружает указанный модуль и добавляет его переменные к остальным"

        vm = VariableManager(module)
        vm.load()
        self.mans.append(vm)

    def processTemplate(self, template, *args, **kwargs):
        context = {}
        #try:
        for vm in self.mans:
            vars = vm.getVariablesDict()
            for varname in vars:
                vars[varname].initValue(*args, **kwargs)
            context.update(vars)
        #except Exception, exc:
        #    log.add("Exception '%s' raised when processing variables!" % exc)
        
        #!!!!!!победа!!!!!!!!#!!!!!!победа!!!!!!!!#!!!!!!победа!!!!!!!!#!!!!!!победа!!!!!!!!
        profile_obj = Profile.objects.get(id = 15)
        context['profile'] = profile_obj
        #!!!!!!победа!!!!!!!!#!!!!!!победа!!!!!!!!#!!!!!!победа!!!!!!!!#!!!!!!победа!!!!!!!!
        
        
        template = Template(template).render(Context(context))
        return template


