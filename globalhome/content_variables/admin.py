# coding: utf-8
from django.contrib import admin
from models import VariableSet

class VariableSetAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("name", "module", "description")

admin.site.register(VariableSet, VariableSetAdmin)


