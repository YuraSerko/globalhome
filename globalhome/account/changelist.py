
# coding: utf8

from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.options import IncorrectLookupParameters
import operator
from django.core.exceptions import SuspiciousOperation, ImproperlyConfigured
from account.models import Profile
from django.db import models
from django.contrib.admin.util import  lookup_needs_distinct
from admin import compare
from django.db.models.query import EmptyQuerySet


class SpecialChangeList(ChangeList):
    def get_query_set(self, request):
        '''qs = self.root_query_set
        if not(request.GET.has_key('q')):
            return EmptyQuerySet()
        (self.filter_specs, self.has_filters, remaining_lookup_params, use_distinct) = self.get_filters(request)
        for filter_spec in self.filter_specs:
            new_qs = filter_spec.queryset(request, qs)
            if new_qs is not None:
                qs = new_qs
        try:
            qs = qs.filter(**remaining_lookup_params)
        except (SuspiciousOperation, ImproperlyConfigured):
            raise
        except Exception as e:
            raise IncorrectLookupParameters(e)

        order_queryset = qs
        if self.search_fields and self.query:
            orm_lookups = ["%s__icontains" % (str(search_field)) for search_field in self.search_fields]
            for bit in self.query.split():
                or_queries = [models.Q(**{orm_lookup: bit})for orm_lookup in orm_lookups]
                qs = qs.filter(reduce(operator.or_, or_queries))
            queryset = set(qs.values_list('id', flat=True))
            search_world = (request.GET['q']).lower().strip()
            profile_objects = Profile.objects.select_related().exclude(user__id__in=qs)
            for pr in profile_objects:
                if compare(pr.get_company_name_or_family().lower(), search_world):
                    queryset.add(pr.user.id)
            qs = order_queryset.filter(pk__in=queryset)
            if not use_distinct:
                for search_spec in orm_lookups:
                    if lookup_needs_distinct(self.lookup_opts, search_spec):
                        use_distinct = True
                        break'''
        #--------startMy--------------------
        qs = self.root_query_set
        if not(request.GET.has_key('q')):
            return EmptyQuerySet()
        (self.filter_specs, self.has_filters, remaining_lookup_params, use_distinct) = self.get_filters(request)
        for filter_spec in self.filter_specs:
            new_qs = filter_spec.queryset(request, qs)
            if new_qs is not None:
                qs = new_qs
        try:
            qs = qs.filter(**remaining_lookup_params)
        except (SuspiciousOperation, ImproperlyConfigured):
            raise
        except Exception as e:
            raise IncorrectLookupParameters(e)

        if self.search_fields and self.query:
            orm_lookups = ["user__%s__icontains" % (str(search_field)) for search_field in self.search_fields]
            search_fields2 = ["first_name", "last_name", "company_name", "legal_form"]
            orm_lookups3 = ["%s__icontains" % (str(search_field)) for search_field in self.search_fields]
            orm_lookups2 = ["%s__icontains" % (str(search_field)) for search_field in search_fields2]
            orm_lookups += orm_lookups2
            print orm_lookups
            profls = Profile.objects.select_related("user").all()
            for bit in self.query.split():
                or_queries = [models.Q(**{orm_lookup: bit})for orm_lookup in orm_lookups]
                profls = profls.filter(reduce(operator.or_, or_queries))
            ids = [profl.user_id for profl in profls]
            qs = qs.filter(pk__in=ids)
            if not use_distinct:
                for search_spec in orm_lookups3:
                    if lookup_needs_distinct(self.lookup_opts, search_spec):
                        use_distinct = True
                        break
        #--------endMy--------------------
        ordering = self.get_ordering(request, qs)
        qs = qs.order_by(*ordering)
        if use_distinct:
            return qs.distinct()
        else:
            return qs

