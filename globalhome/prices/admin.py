# coding: utf-8
from django.contrib import admin
from prices.models import PricesGroup, Price

class PricesGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    actions = None

    # def save_model(self, request, obj, form, change):
    #    pass

#    def has_delete_permission(self, request, obj = None):
#        if obj:
#            if obj.id == 1:
#                return False
#        return True

class PriceAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "value", "slug")
    save_as = True

# admin.site.register(PricesGroup, PricesGroupAdmin)
# admin.site.register(Price, PriceAdmin)

