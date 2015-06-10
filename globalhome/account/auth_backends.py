# -*- coding=utf-8 -*-
# $Id: auth_backends.py 186 2010-08-04 14:16:00Z oleg $
import datetime

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model
from django.db import connection
from account.models import User
from account.models import ActionRecord
from django.db import transaction

class LoginBackend(object):
    def authenticate(self, username=None, password=None, activation_key=None, action=None):
        if action and hasattr(self, '%s_action' % action):
            return getattr(self, '%s_action' % action)(activation_key)
        try:
            user = User.objects.get(username=username)
        except:
            return None
        if user.check_password(password):
            #if not user.is_active and not self.check_action_record(user):
                #return None
            return user
        else:
            return None

    def activate_action(self, activation_key):
        user = ActionRecord.registrations.activate_user(activation_key.lower())
        return user

    def reset_password_action(self, activation_key):
        user = ActionRecord.resets.password_reset(activation_key.lower())
        return user

    def activate_by_key_action(self, activation_key):
        """ Use for instantly log in just registered user """
        try:
            user = ActionRecord.objects.get(action_key=activation_key, type='A').user
        except:
            return None
        return user

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except:
            return None
        if not user.is_active and not self.check_action_record(user):
            return None
        return user

    def check_action_record(self, user):
        try:
            action = ActionRecord.objects.get(user=user, type='A')
        except:
            return False
        return ((datetime.datetime.now() - action.date).days*86400 + (datetime.datetime.now() - action.date).seconds) < settings.NON_ACTIVE_USER_ACCESS_TIME


    #
    def get_group_permissions(self, user_obj):
        "Returns a list of permission strings that this user has through his/her groups."
        if not hasattr(user_obj, '_group_perm_cache'):
            cursor = connection.cursor()
            # The SQL below works out to the following, after DB quoting:
            # cursor.execute("""
            #     SELECT ct."app_label", p."codename"
            #     FROM "auth_permission" p, "auth_group_permissions" gp, "auth_user_groups" ug, "django_content_type" ct
            #     WHERE p."id" = gp."permission_id"
            #         AND gp."group_id" = ug."group_id"
            #         AND ct."id" = p."content_type_id"
            #         AND ug."user_id" = %s, [self.id])
            qn = connection.ops.quote_name
            sql = """
                SELECT ct.%s, p.%s
                FROM %s p, %s gp, %s ug, %s ct
                WHERE p.%s = gp.%s
                    AND gp.%s = ug.%s
                    AND ct.%s = p.%s
                    AND ug.%s = %%s""" % (
                qn('app_label'), qn('codename'),
                qn('auth_permission'), qn('auth_group_permissions'),
                qn('auth_user_groups'), qn('django_content_type'),
                qn('id'), qn('permission_id'),
                qn('group_id'), qn('group_id'),
                qn('id'), qn('content_type_id'),
                qn('user_id'),)
            cursor.execute(sql, [user_obj.id])
            user_obj._group_perm_cache = set(["%s.%s" % (row[0], row[1]) for row in cursor.fetchall()])
            transaction.commit_unless_managed()
        return user_obj._group_perm_cache

    def get_all_permissions(self, user_obj):
        if not hasattr(user_obj, '_perm_cache'):
            user_obj._perm_cache = set([u"%s.%s" % (p.content_type.app_label, p.codename) for p in user_obj.user_permissions.select_related()])
            user_obj._perm_cache.update(self.get_group_permissions(user_obj))
        return user_obj._perm_cache

    def has_perm(self, user_obj, perm):
        return perm in self.get_all_permissions(user_obj)

    def has_module_perms(self, user_obj, app_label):
        return bool(len([p for p in self.get_all_permissions(user_obj) if p[:p.index('.')] == app_label]))


class AccountModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = self.user_class.objects.get(username=username)
            if user.check_password(password):
                return user
        except self.user_class.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return self.user_class.objects.get(pk=user_id)
        except self.user_class.DoesNotExist:
            return None

    @property
    def user_class(self):
        if not hasattr(self, '_user_class'):
            self._user_class = get_model(*settings.CUSTOM_USER_MODEL.split('.', 2))
            if not self._user_class:
                raise ImproperlyConfigured('Could not get custom user model')
        return self._user_class

