# -*- coding=utf-8 -*-
# $Id$

from django.utils.translation import ugettext_lazy as _

class BaseMail(object):
    """
    Base class for descripting of letter context
    @keys  ((template_var_name, var_description), ...)
    @code varchar - code for representation in model
    @verbose_name - unicode
    """
    code = None
    verbose_name = None
    keys = None


    def populate(self, context):
        """
        Populate context with keys
        @context - dict to populate context
        """
        if len(set([x for x, y in self.keys]) - set(context.keys())):
            raise Exception(_(u"You should provide the fallowing keys in context: %(keys)s") % \
                {'keys':', '.join([x for x, y in self.keys])})
        self.context = context


class Registry(object):
    def __init__(self):
        self.registry = []

    def items(self):
        for r in self.registry:
            yield r

    def register(self, klass):
        if klass not in self.registry:
            self.registry.append(klass)

    def get_by_code(self, code):
        for r in self.items():
            if r.code == code:
                return r

    def codes(self):
        for r in self.items():
            yield r.code

    def get_code_list(self):
        return list(self.codes)

    def get_choices(self):
        for r in self.items():
            yield (r.code, r.verbose_name)

registry = Registry()

class RegistrationConfirmEmail(BaseMail):
    code = 'REGISTRATION_CONFIRM'
    verbose_name = _(u"Registration confirm email")
    keys = (('activation_url', _(u"Activation URL")),
            ('password_restore_url', _(u"Password restore URL")),
            ('expiration_day', _(u"Expiration date")),
            ('password', _(u"Password")),
            ('username', _(u"User login name")),
            ('domain', _(u"Current domain")),)
registry.register(RegistrationConfirmEmail)


class NotificationOfLockoutEmail(BaseMail):
    code = 'NOTIFICATION_OF_LOCKOUT'
    verbose_name = _(u"Notification of lockout")
    keys = (('username', _(u"User login name")),
            ('domain', _(u"Current domain")),)
registry.register(NotificationOfLockoutEmail)



class ResetPasswordEmail(BaseMail):
    code = 'RESET_PASSWORD'
    verbose_name = _(u"Reset password email")
    keys = (
            ('action_key', _(u"Action key")),
            ('username', _(u"User login name")),
            ('activation_link', _(u"Activation link")),
            ('expired_in', _(u"Expiration date")),
          )
registry.register(ResetPasswordEmail)

class ResetPasswordConfirmedEmail(BaseMail):
    code = 'RESET_PASSWORD_CONFIRMED'
    verbose_name = _(u"Reset password request confirmed")
    keys = (
            ('username', _(u"User login name")),
            ('password', _(u"Password")),
          )
registry.register(ResetPasswordConfirmedEmail)

# class BuyCardEmail(BaseMail):
#    code = 'BUY_CARD'
#    verbose_name = _(u"Карта предоплаты GlobalHome.su")
#    keys = (
#            ('login', _(u"Логин карты")),
#            ('password', _(u"Pin-код карты")),
#            ('summ', _(u"Номинал карты")),
#          )
# registry.register(BuyCardEmail)
