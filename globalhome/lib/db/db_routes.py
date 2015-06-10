from settings import BILLING_DB_TABLE_LIST as TABLE_LIST

class MyAppRouter(object):
    """A router to control all database operations on models in
    the myapp application"""

    def db_for_read(self, model, **hints):
        "Point all operations on myapp models to 'other'"
        if model._meta.db_table in TABLE_LIST:
            return 'billing'
        return None

    def db_for_write(self, model, **hints):
        "Point all operations on myapp models to 'other'"
        if model._meta.db_table in TABLE_LIST:
            return 'billing'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in myapp is involved"
        if obj1._meta.db_table in TABLE_LIST or obj2._meta.db_table in TABLE_LIST:
            return True
        return None
#        if obj1._meta.app_label == 'myapp' or obj2._meta.app_label == 'myapp':
#            return True
#        return None

    def allow_syncdb(self, db, model):
        "Make sure the myapp app only appears on the 'other' db"
        if db == 'billing':
            if model._meta.db_table in TABLE_LIST:
                print "object=%s" % model._meta.object_name
                print "meta=%s" % model._meta.app_label
                print model._meta.db_table in TABLE_LIST
            return model._meta.db_table in TABLE_LIST
        else:
            return model._meta.db_table not in TABLE_LIST
        return None

#        if db == 'other':
#            return model._meta.app_label == 'myapp'
#        elif model._meta.app_label == 'myapp':
#            return False
#        return None


