# -*- coding=utf-8 -*-
# $Id: managers.py 252 2010-12-09 15:53:35Z site $
import re
import os
from hashlib import sha1
import random
import datetime

from pytils.translit import slugify
from django.db import models
from django.contrib.sites.models import Site
from django.template import Context, loader
from django.conf import settings
from django import template
from django.template import Template, Context
from lib.mail import send_email
from lib.mail import send_mail_threaded
from django.utils.translation import get_language, ugettext_lazy as _
from django.core.urlresolvers import reverse
from adminmail.process import send_adminmail_simple
from lib.mail import send_mail

def lockout_notification_email(user, letter, mail_context):
    current_domain = Site.objects.get_current().domain
    subject = Template(letter.subject).render(Context(mail_context))
    text = Template(letter.texttemplate).render(Context(mail_context))
    send_email(subject, text, settings.DEFAULT_FROM_EMAIL, [user.email], user.id)


class RegistrationManager(models.Manager):
    """
    Custom manager for the ActionRecord.
    Holds registrations.
    """

    def get_query_set(self):
        """Custom queryset"""
        return super(RegistrationManager, self).get_query_set().filter(action_type='A')

    def activate_user(self, action_key):
        """
        Given the activation key, makes a User's account active if the
        activation key is valid and has not expired.

        Returns the User if successful, or False if the account was
        not found or the key had expired.
        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point even trying to look it up
        # in the DB.
        if re.match('[a-f0-9]{40}', action_key):
            try:
                record = self.get(action_key=action_key)
            except self.model.DoesNotExist:
                return None
            if not record.expired:
                # Account exists and has a non-expired key. Activate it.
                user = record.user
                user.is_active = True
                user.save()
                record.delete()
                return user
        return None

    def create_inactive_user_key(self, new_user, row_password, send_email=True):
        """
        Creates a a new ActionRecord for a new User instance that
        User, generates an activation key, and mails it.
        Pass ``send_email=False`` to disable sending the email.
        You can disable email_sending in settings: DISABLE_REGISTRATION_EMAIL=True
        """
        if settings.DISABLE_REGISTRATION_EMAIL:
            send_email = False

        # Generate a salted SHA1 hash to use as a key.
        salt = sha1(str(random.random())).hexdigest()[:5]
        action_key = sha1(salt + slugify(new_user.username)).hexdigest()

        # And finally create the record.
        self.create(user=new_user, action_key=action_key, action_type='A')
        if send_email:
            send_email = self.create_activation_email(action_key, row_password, new_user)

        return (action_key, send_email)

    def resend_activation_email(self, action=None, action_id=None):
        if action_id:
            try:
                action = self.get(id=action_id)
            except:
                return False
        if action:
            action.date = datetime.datetime.now()
            action.save()
            self.create_activation_email(action.action_key, None, action.user)


    def create_activation_email(self, action_key, password, user):

        current_domain = Site.objects.get_current().domain
        """
        subject = _(u"Account activation")
        try:
            message_template = loader.get_template('mail/registration_confirm_ru.txt') # TODO - make i18n
            message_context = Context({ 'site_url': '%s' % current_domain,
                                    'activation_key': action_key,
                                    'expiration_day': datetime.datetime.now() + datetime.timedelta(days=settings.ACTION_RECORD_DAYS),
                                    'password': password,
                                    'user': user,
                                    'domain': current_domain,
                                    })

            message = message_template.render(message_context)
            user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
            return True
        except Exception, e:
            return False
        """
        try:
            mail_context = {
                'activation_url': u"http://%s%s" % (current_domain, \
                                    reverse('account_activation', args=[action_key])),
                'password_restore_url': u"http://%s%s" % (current_domain, \
                    reverse('account_password_reset_request')),
                'expiration_day': datetime.datetime.now() + datetime.timedelta(days=settings.ACTION_RECORD_DAYS),
                'password': password,
                'username': user.username,
                'domain': current_domain,
            }
            send_adminmail_simple('REGISTRATION_CONFIRM', 'ru', mail_context, settings.DEFAULT_FROM_EMAIL, [user.email], user.id)
            return True
        except Exception, e:
            print e
            return False

    def delete_expired_users(self):
        """
        Removes unused records and their associated accounts.

        This is provided largely as a convenience for maintenance
        purposes; if a ActionRecord's key expires without the
        account being activated, then both the ActionRecord and
        the associated User become clutter in the database, and (more
        importantly) it won't be possible for anyone to ever come back
        and claim the username. For best results, set this up to run
        regularly as a cron job.

        If you have a User whose account you want to keep in the
        database even though it's inactive (say, to prevent a
        troublemaker from accessing or re-creating his account), just
        delete that User's ActionRecord and this method will
        leave it alone.

        """
        for record in self.all():
            if record.expired:
                user = record.user
                if not user.is_active:
                    user.delete()


class ResetManager(models.Manager):
    """
    Custom manager for ActionRecord.
    Holds password resets.
    """

    def get_query_set(self):
        """Custom queryset"""
        return super(ResetManager, self).get_query_set().filter(action_type='R')

    def password_reset(self, action_key, send_email=True, password=False):
        """
        Given activation key will reset user password and mail it to
        user's email if key is valid and not expired.

        Returns the User if successful, or None if the account was
        not found or the key had expired.

        Pass ``send_email=False`` to disable sending the email.
        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point even trying to look it up
        # in the DB.
        if not re.match('[a-f0-9]{40}', action_key):
            return None
        try:
            record = self.get(action_key=action_key)
        except self.model.DoesNotExist:
            return None
        if record.expired:
            return None
        # Key valid and not expired. Reset password.
        user = record.user
        if password:
            password = password.strip()
        else:
            import os, binascii
            password = binascii.b2a_base64(os.urandom(12)).strip()
        user.set_password(password)
        user.save()
        if send_email:
            """
            from lib.mail import send_mail
            current_domain = Site.objects.get_current().domain
            subject = u"Ваш пароль изменен"
            message_template = loader.get_template('mails/resetted_email_ru.txt')
            message_context = Context({ 'site_url': '%s://%s/' % (settings.SITE_PROTOCOL, current_domain),
                                        'password': password,
                                        'user': user })
            message = message_template.render(message_context)
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            """
            current_domain = Site.objects.get_current().domain
            mail_context = {'site_url': '%s://%s/' % \
                            (settings.SITE_PROTOCOL, current_domain),
                            'password': password,
                            'username': user.username,
                            'domain': current_domain, }
            send_adminmail_simple('RESET_PASSWORD_CONFIRMED', 'ru', mail_context, \
                                  settings.DEFAULT_FROM_EMAIL, [user.email], user.id)
        record.delete()
        return user

    def create_password_reset(self, users, send_email=True):
        """
        Create ActionRecord for password reset and mails link
        with activation key to user's email.

        Pass ``send_email=False`` to disable sending the email.
        """
        current_domain = Site.objects.get_current().domain
        actions_reset = []
        for user in users:
            # Generate a salted SHA1 hash to use as a key.
            salt = sha1(str(random.random())).hexdigest()[:5]
            action_key = sha1(salt + slugify(user.username)).hexdigest()

            # And finally create the record.
            record, created = self.get_or_create(user=user, \
                                                 action_type='R', \
                                                 action_key=action_key)

            actions_reset.append({
                                  'user' : user,
                                  u'activation_link': '%s://%s/activation/%s/' % (settings.SITE_PROTOCOL, current_domain, action_key),
                                  u'expired_in': datetime.datetime.now() + datetime.timedelta(days=settings.ACTION_RECORD_DAYS),
                                   })
        email = users[0].email
        if send_email:
            """
            from lib.mail import send_mail_threaded

            current_domain = Site.objects.get_current().domain
            subject = "%s: восстановление пароля" % current_domain
            message_template = loader.get_template('mail/reset_email_ru.txt')
            message_context = Context({
                               'action_key': record.action_key,
                               'actions_reset' : actions_reset,
                              })
            message = message_template.render(message_context)
            send_mail_threaded(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
            """
            mail_context = {
                'action_key': record.action_key,
                'username': actions_reset[0]['user'].username,
                'activation_link': actions_reset[0]['activation_link'],
                'expired_in': actions_reset[0]['expired_in'],
                'domain': current_domain,
            }
            send_adminmail_simple('RESET_PASSWORD', 'ru', mail_context, settings.DEFAULT_FROM_EMAIL, [email], user.id)
        return record

    def delete_expired_records(self):
        """Removes unused expired password reset records"""
        for record in self.all():
            if record.expired:
                record.delete()

class EmailManager(models.Manager):
    """
    Custom manager for ActionRecord model.
    Holds email changes.
    """
    def get_query_set(self):
        """Custom queryset, returns only ActionRecords for password resets"""
        return super(EmailManager, self).get_query_set().filter(action_type='E')

    def change_email(self, action_key):
        """
        Given activation key will change user email if key
        is valid and not expired.

        Returns the User if successful, or None if the account was
        not found or the key had expired.
        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point even trying to look it up
        # in the DB.
        if not re.match('[a-f0-9]{40}', action_key):
            return None
        try:
            record = self.get(action_key=action_key)
        except self.model.DoesNotExist:
            return None
        if record.expired:
            return None
        # Key valid and not expired. Change email.
        user = record.user
        if user.email_new:
            user.email = user.email_new
            user.email_new = ''
        user.save()
        record.delete()
        return user

    def create_email_change(self, user, new_email, send_email=True):
        """
        Create ActionRecord for email change and mails link
        with activation key to user's email.

        Pass ``send_email=False`` to disable sending the email.
        """
        # Generate a salted SHA1 hash to use as a key.
        salt = sha1(str(random.random())).hexdigest()[:5]
        action_key = sha1(salt + user.username).hexdigest()

        # And finally create the record.
        user.email_new = new_email
        user.save()
        record, created = self.get_or_create(user=user,
                                             action_type='E',
                                             defaults={'action_key': action_key})

        if send_email:
            current_domain = Site.objects.get_current().domain
            subject = "Change your email address at %s" % current_domain
            message_template = loader.get_template('mail_templates/password_reset.txt')
            message_context = Context({'site_url': '%s://%s/' % (settings.SITE_PROTOCOL, current_domain),
                                       'action_key': record.action_key,
                                       'expiration_days': settings.ACTION_RECORD_DAYS,
                                       'user': user})
            message = message_template.render(message_context)
            user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
        return record

    def delete_expired_records(self):
        """Removes unused expired password reset records"""
        for record in self.all():
            if record.expired:
                record.delete()

