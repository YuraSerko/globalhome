# utf-8
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.options import IncorrectLookupParameters
from django.core.paginator import InvalidPage
from django.db.models.query import QuerySet
import operator
from collections import OrderedDict
from functools import reduce

from django.core.exceptions import SuspiciousOperation, ImproperlyConfigured

from django.db import models


from django.contrib.admin.util import    lookup_needs_distinct

      

class SpecialForSearchingChangeList(ChangeList):
    
    def get_query_set(self, request):
        # First, we collect all the declared list filters.
        (self.filter_specs, self.has_filters, remaining_lookup_params,
         use_distinct) = self.get_filters(request)

        # Then, we let every list filter modify the queryset to its liking.
        qs = self.root_query_set
        for filter_spec in self.filter_specs:
            new_qs = filter_spec.queryset(request, qs)
            if new_qs is not None:
                qs = new_qs

        try:
            # Finally, we apply the remaining lookup parameters from the query
            # string (i.e. those that haven't already been processed by the
            # filters).
            qs = qs.filter(**remaining_lookup_params)
        except (SuspiciousOperation, ImproperlyConfigured):
            # Allow certain types of errors to be re-raised as-is so that the
            # caller can treat them in a special way.
            raise
        except Exception as e:
            # Every other error is caught with a naked except, because we don't
            # have any other way of validating lookup parameters. They might be
            # invalid if the keyword arguments are incorrect, or if the values
            # are not in the correct type, so we might get FieldError,
            # ValueError, ValidationError, or ?.
            raise IncorrectLookupParameters(e)

        # Use select_related() if one of the list_display options is a field
        # with a relationship and the provided queryset doesn't already have
        # select_related defined.
        if not qs.query.select_related:
            if self.list_select_related:
                qs = qs.select_related()
            else:
                for field_name in self.list_display:
                    try:
                        field = self.lookup_opts.get_field(field_name)
                    except models.FieldDoesNotExist:
                        pass
                    else:
                        if isinstance(field.rel, models.ManyToOneRel):
                            qs = qs.select_related()
                            break

        # Set ordering.
        ordering = self.get_ordering(request, qs)
        qs = qs.order_by(*ordering)
        # Apply keyword searches.
        def construct_search(field_name):
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name


        if self.search_fields and self.query:
            orm_lookups = [construct_search('username')]
            subAccounts = self.model_admin.subAccounts
            for bit in self.query.split():
                or_queries = [models.Q(**{orm_lookup: bit})
                              for orm_lookup in orm_lookups]
            subAccounts = subAccounts.filter(reduce(operator.or_, or_queries))
            orm_lookups = [construct_search(str(search_field))
                           for search_field in self.search_fields]
            for bit in self.query.split():
                or_queries = [models.Q(**{orm_lookup: bit}) for orm_lookup in orm_lookups]
                queryset = qs.filter(reduce(operator.or_, or_queries))
                qs = qs.filter(models.Q(id__in=queryset.values_list('id', flat=True)) | models.Q(bill_account__in=subAccounts.values_list('account', flat=True)))
            if not use_distinct:
                for search_spec in orm_lookups:
                    if lookup_needs_distinct(self.lookup_opts, search_spec):
                        use_distinct = True
                        break

        if use_distinct:
            return qs.distinct()
        else:
            return qs
