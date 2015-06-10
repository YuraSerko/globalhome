# coding: utf-8
from django.contrib import admin
from finoperations.models import BalanceOperation

class BalanceOperationAdmin(admin.ModelAdmin):
    list_display = ("date", "user", "operation_type", "value", "cause")
    readonly_fields = ("operation_type", "user", "date", "value", "cause")
    actions = None
    date_hierarchy = "date"
    list_filter = ("operation_type",)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, *args, **kwargs):
        return False
    
    class Meta:
        app_label = "billing"
    
# admin.site.register(BalanceOperation, BalanceOperationAdmin)


