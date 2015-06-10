# coding: utf-8
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode 

ASC = "ASC"
DESC = "DESC"

class FakeQuerySet:
    def __init__(self, model = None, using = None, where = None, sort = None, order = None, fields = None):
        self.results = []
        self.r_count = 0
        self.model = model
        self.using = using
        self.where = where
        self.sort = sort
        self.order = order
        self.fields = fields
        self.have_results = False
    
    def get_results(self):
        #qs = QuerySet(model = self.model, using = self.using).select_related()
        qs = QuerySet(model = self.model, using = self.using)
        if self.where:
            qs = qs.extra(where = [self.where])
        
        self.results = list(qs)
        # вот тут мы применяем сортировки
        
        def cmp_func(a, b):
            #try:
            v1 = getattr(a, self.fields[self.sort][0])
            v2 = getattr(b, self.fields[self.sort][0])
            
            if self.order == ASC:
                if v1 < v2:
                    return -1
                elif v1 > v2:
                    return 1
            
            if self.order == DESC:
                if v1 < v2:
                    return 1
                elif v1 > v2:
                    return -1
            
            #except Exception, e:
            #    print "Exception in cmp_func:", e
            #    pass
            
            return 0
        
        if not self.sort is None and not self.order is None:
            self.results.sort(cmp = cmp_func)
        
        self.r_count = len(self.results)
        self.have_results = True
    
    def __getitem__(self, *args, **kwargs):
        
        sl = args[0]
        if type(sl) is slice:
            min = sl.start
            max = sl.stop
            if not self.have_results:
                self.get_results()
            return self.results[min:max]
        
        if type(sl) is int:
            if not self.have_results:
                self.get_results()
            return self.results[sl]
    
    def count(self):
        if not self.have_results:
            self.get_results()
        return self.r_count
    
    def __len__(self):
        if not self.have_results:
            self.get_results()
        return self.r_count

class ColumnsManager:
    """
        Класс, который есть менеджер колонок таблицы указанной модели
    """
    def __init__(self, model, using = None, sort = None, order = None):
        self.fields = {}
        self.model = model
        self.using = using
        self.items = None
        self.sort = sort
        self.order = order
        self.where = ""
        
        self.header_items_class = "table-header-column"
        self.header_items_style = ""#"text-align: left;"
        self.header_row_class = "table-header-row"
        self.header_row_style = ""#"text-align: left;"
        
        self.content_row_class = "table-content-row"
        self.content_row_style = "text-align: left;"
        self.content_item_class = "table-content-item"
        self.content_item_style = "text-align: left;"
        
        self.get_add = ""
    
    def AddColumn(self, name, verbose_name):
        """
            Добавляет колонку в таблицу
            @sort - может быть пустой строкой, "DESC" или "ASC"
        """
        
        if not name in self.fields.keys():
            self.fields[len(self.fields.keys())] = [name, verbose_name]
        else:
            raise Exception("Column with name '%s' is already in table!" % name)
    
    def GetQuerySet(self):
        "Возвращает соответствующий таблице QuerySet"
        
        qs = FakeQuerySet(
            model = self.model,
            using = self.using,
            where = self.where,
            sort = self.sort,
            order = self.order,
            fields = self.fields
        )
        
        return qs

    
    def GetHeaderRow(self, use_names = False):
        "Возвращает строку с заголовком таблицы"
        s = '<tr class="%(class)s" style="%(style)s">\n' % {
            "class": self.header_row_class,
            "style": self.header_row_style,
        }
        keys = self.fields.keys()[:]
        keys.sort()
        for field in keys:
            if field == self.sort:
                if self.order == ASC:
                    if self.header_items_style:
                        s += '<th scope="col" class="%(class)s-sort-%(sort)s" style="%(style)s">' % {
                            "class": self.header_items_class,
                            "style": self.header_items_style,
                            "sort": ASC
                        }
                    else:
                        s += '<th scope="col" class="%(class)s-sort-%(sort)s">' % {
                            "class": self.header_items_class,
                            "sort": ASC
                        }
                    sort_get = "sort=%s&order=DESC" % field
                if self.order == DESC:
                    if self.header_items_style:
                        s += '<th scope="col" class="%(class)s-sort-%(sort)s" style="%(style)s">' % {
                            "class": self.header_items_class,
                            "style": self.header_items_style,
                            "sort": DESC
                        }
                    else:
                        s += '<th scope="col" class="%(class)s-sort-%(sort)s">' % {
                            "class": self.header_items_class,
                            "sort": DESC
                        }
                    sort_get = "sort=%s&order=ASC" % field
            else:
                sort_get = "sort=%s&order=DESC" % field
                if self.header_items_style:
                    s += '<th scope="col" class="%(class)s" style="%(style)s">' % {
                        "class": self.header_items_class,
                        "style": self.header_items_style,
                    }
                else:
                    s += '<th scope="col" class="%(class)s">' % {
                        "class": self.header_items_class,
                    }
            
            if self.get_add:
                s += '<a href="./?%(get_add)s&%(get_sort)s">' % { "get_add": self.get_add, "get_sort": sort_get }
            else:
                s += '<a href="./?%s">' % sort_get
            if use_names:
                s += self.fields[field][0]
            else:
                s += force_unicode(self.fields[field][1])
            s += "</a></th>\n"
        s += "</tr>"
        
        return mark_safe(s)
    
    def GetTableRows(self):
        "Возвращает строки таблицы"
        if self.items:
            # используем self.items
            items = self.items
        else:
            items = self.GetQuerySet()
        
        keys = self.fields.keys()[:]
        keys.sort()
        html = ""
        for item in items:
            row = '<tr class="%(class)s" style="%(style)s">' % {
                "class": self.content_item_class,
                "style": self.content_item_style,
            }
            for key in keys:
                row += '<td class="%(class)s" style="%(style)s">' % {
                    "class": self.content_item_class,
                    "style": self.content_item_style,
                }
                '''
                try:
                    row += str(getattr(item, self.fields[key][0], "-"))
                except:
                    row += "-"
                '''
                row += str(getattr(item, self.fields[key][0], "-"))
                row += "</td>"
            
            row += "</tr>"
            html += row
        
        return mark_safe(html)
    
    
    
    
    
    

