from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from internet.models import Connection_address
from models import Mikrotik
from django.contrib.admin.options import IncorrectLookupParameters
from django.core.paginator import InvalidPage
from django.db.models.query import QuerySet
import operator
from collections import OrderedDict
    
    
class UnsplitableUnicode(unicode):
    def split(self, *args, **kwargs):
        return [self.lower().replace(' ', '')]

        
def qs_sort_by_fields(queryset, field, order_by):
    list_of_id_and_interesting_field, list_of_values, id_of_objects_without_information = [], {}, []
    for k, v in queryset.items():
        list_of_id_and_interesting_field.append([k, v[field]])
         
    for i_id, i_field in list_of_id_and_interesting_field:
        if not(i_field):
            id_of_objects_without_information.append(i_id)
        elif not (list_of_values.has_key(i_field)):
            list_of_values[i_field] = [i_id]
        else:
            list_of_values[i_field].append(i_id)
              
    if int(order_by[field]) < 0:
        list_of_interesting_value_and_ids = [('', id_of_objects_without_information)] + sorted(list_of_values.items(), reverse=True)
    else:
        list_of_interesting_value_and_ids = sorted(list_of_values.items()) + [['', id_of_objects_without_information]]
        
    new_qs = OrderedDict()
    if (field != len(order_by) - 1):
        for i in list_of_interesting_value_and_ids:
            new_queryset = {}
            for id in i[1]:
                new_queryset.update({id: queryset[id]})
            new_qs.update(new_queryset if len(new_queryset.keys()) == 1 else qs_sort_by_fields(new_queryset, field + 1, order_by))
    else:
        for i in list_of_interesting_value_and_ids:
            for id in i[1]:
                new_qs[id] = queryset[id]
    return new_qs



class SpecialOrderingChangeList(ChangeList):

    def special_ordering(self, queryset):
        order_by = '' if not(self.params.has_key('o')) else self.params.get('o').split('.')
        if not(order_by):
            return queryset
        
        special_field = self.model_admin.special_field
        number_of_ordering_fields = []
        for i in order_by:
            number_of_ordering_fields.append(abs(int(i)))
            
        if self.list_display.index(special_field) in number_of_ordering_fields:
            order_list = {}
            for qs in queryset:
                order_list.update({qs.id:[]})
            for field in number_of_ordering_fields:
                for i, qs in enumerate(queryset):
                    if cmp(self.model_admin.list_display[field - 1], special_field):
                        field_item = self.model_admin.list_display[field - 1]
                        order_list.get(qs.id).append(qs.__dict__.get(field_item))
                    else:
                        order_list.get(qs.id).append(self.model_admin.special_action(qs))
            qs = qs_sort_by_fields(order_list, 0, order_by)
            tmp_queryset = []
            for i in qs.keys():
                tmp_queryset.append(self.model.objects.all().get(id=i))
            queryset._result_cache = tmp_queryset
        return queryset


    def special_search_by_field_address(self, queryset):
        from internet.models import Connection_address, Internet_city
        order_by = '' if not(self.params.has_key('q')) else self.params.get('q').split(' ')
        if not(order_by):
            return queryset
        cities = []
        for x in Internet_city.objects.all().values_list('city'):
            for i in x:
                cities.append(i.lower())
        check_on_search_address = True if order_by[0].lower() in cities else False
        if check_on_search_address:
            qs = []
            searching_address = ''.join(x for x in order_by)
            for i in queryset:
                if i.address:
                    address_obj = Connection_address.objects.get(id=i.address)
                    address = '%s%s%s' % (address_obj.city, address_obj.street, address_obj.house)
                    address = address.decode('utf-8').replace(' ', '')
                    if address.find(searching_address.lower()):
                        qs.append(i)
            queryset._result_cache = qs
        return queryset

    def get_query_set(self, request):
        self.query = UnsplitableUnicode(self.query)
        queryset = super(SpecialOrderingChangeList, self).get_query_set(request)
        queryset = self.special_ordering(queryset)
#         queryset = self.special_search_by_field_address(queryset)
        return queryset

