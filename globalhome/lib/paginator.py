# -*- coding: utf-8 -*-
# $Id: paginator.py 2097 2009-01-12 12:16:30Z valera $

import copy

from lib.django_paginator import ObjectPaginator, InvalidPage
from django.db import connection
from django.http import Http404
from django.db import transaction

class SimplePaginator(ObjectPaginator):
    def __init__(self, query_set, page_size, link_template='?page=%s', total='?'):
        self.current_page = 1
        self.page_size = page_size
        self.link_template = link_template
        self.total = total
        ObjectPaginator.__init__(self, query_set, page_size)

    def set_page(self, page_num):
        try:
            self.current_page = int(page_num)
        except (ValueError, TypeError):
            raise Http404

    def has_next_page(self, page_num=None):
        try:
            if page_num is None:
                return ObjectPaginator.has_next_page(self, self.current_page-1)
            else:
                return ObjectPaginator.has_next_page(self,page_num)
        except InvalidPage:
            raise Http404

    def has_previous_page(self, page_num=None):
        try:
            if page_num is None:
                return ObjectPaginator.has_previous_page(self, self.current_page-1)
            else:
                return ObjectPaginator.has_previous_page(self,page_num)
        except InvalidPage:
            raise Http404

    def get_page(self, page_num=None):
        try:
            if page_num is None:
                return ObjectPaginator.get_page(self, self.current_page-1)
            else:
                return ObjectPaginator.get_page(self, page_num)
        except InvalidPage:
            raise Http404

    def get_page_num(self, item):
        """
        Returns a number of page on which the item is located.
        """
        for page in self.page_range:
            if item.id in [i.id for i in self.get_page(page)]:
                return page
        return 1
    
    def first_link(self):
        return self.link_template % (1)
    
    def last_link(self):
        return self.link_template % (self.pages)
    
    def previous_link(self):
        if ObjectPaginator.has_previous_page(self, self.current_page-1):
            return self.link_template % (self.current_page - 1)
        else:
            return '#'

    def next_link(self):
        if ObjectPaginator.has_next_page(self, self.current_page-1):
            return self.link_template % (self.current_page + 1)
        else:
            return '#'

    def start_index(self):
        return (self.current_page-1) * self.page_size + 1

    def end_index(self):
        return min(self.current_page * self.page_size, self.hits)

    def make_page_links(self, start, end):
        return [(p+1, self.link_template % (p+1), (p+1 == self.current_page)) for p in range(start, end)]

    def page_links(self):
        return self.make_page_links(0, self.pages)

    def windowed_page_links(self, window_size=10):
        links = []
        if self.pages <= 12:
            links = [self.page_links()]
        elif self.current_page - window_size/2 <= 3:
            links = [self.make_page_links(0, window_size), self.make_page_links(self.pages-2, self.pages)]
        elif self.current_page + window_size/2 > self.pages - 2:
            links = [self.make_page_links(0, 2), self.make_page_links(self.pages-window_size, self.pages)]
        else:
            links = [self.make_page_links(0, 2),
                             self.make_page_links(self.current_page-window_size/2-1, self.current_page+window_size/2-1),
                             self.make_page_links(self.pages-2, self.pages)]
        response = []
        for g in links:
            r = []
            for i in g:
                r.append({'page':i[0],'link':i[1],'current':i[2]})
            response.append(r)
        return response

class TreePaginator(SimplePaginator):
    """
    Paginates hierarchical structures by first-level elements.
    Hierarchy should be implemented by mptt.
    """

    def _get_hits(self):
        query_set = copy.copy(self.query_set)
        self.query_set = self.query_set.filter(level=0)
        hits = super(TreePaginator, self)._get_hits()
        self.query_set = query_set
        return hits

    def get_page(self, page_num=None):
        page_num = page_num or self.current_page
        start = (page_num-1) * self.page_size
        finish = (page_num-1) * self.page_size + self.page_size
        page = self.query_set.filter(level=0).values('id','tree_id')[start:finish]
        if page:
            return self.query_set.filter(tree_id__in=[i['tree_id'] for i in page])
        else:
            return []

class SqlQuerySet(list):

    def __init__(self, sql_query, sql_len_query, model_class):
        self.query = sql_query
        self.sql_len_query = sql_len_query
        self.model_class = model_class

    def __len__(self):
        cur = connection.cursor()
        cur.execute(self.sql_len_query)
        length = int(cur.fetchone()[0])
        transaction.commit_unless_managed()
        return length

    def __getslice__(self, start, finish):
        cur = connection.cursor()
        query = self.query + ' OFFSET %d LIMIT %d' % (start, finish-start)
        cur.execute(query)
        getslice = self.model_class.objects.select_related().filter(pk__in=[x[0] for x in cur.fetchall()])
        transaction.commit_unless_managed()
        return getslice
