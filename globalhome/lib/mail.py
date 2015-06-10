# -*- coding: utf-8 -*-
# $Id: mail.py 1988 2008-12-12 14:45:48Z dmitry $

from django.core.mail import EmailMessage  # , SMTPConnection
# from django.core.mail import send_mail as _send_mail
from page.models import Send_mail
import datetime
from django.conf import settings
from django.core.mail.message import EmailMessage as em

from django.core.mail import EmailMessage, EmailMultiAlternatives, SafeMIMEText
from page.models import Send_mail
from django.contrib.auth.models import User
from page.models import UserFiles
# from data_centr.views import send_mail_check
# from account.models import Profile
from page.models import Sender
from django.conf import settings
import mimetypes
DEFAULT_ATTACHMENT_MIME_TYPE = 'application/octet-stream'
from django.utils.encoding import smart_str
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
import os
from django.core import mail

class EmailMultiAlternativesWithEncoding(EmailMultiAlternatives):
    def _create_attachment(self, filename, content, mimetype=None):
            """
            Converts the filename, content, mimetype triple into a MIME attachment
            object. Use self.encoding when handling text attachments.
            """
            if mimetype is None:
                mimetype, _ = mimetypes.guess_type(filename)
                if mimetype is None:
                    mimetype = DEFAULT_ATTACHMENT_MIME_TYPE
            basetype, subtype = mimetype.split('/', 1)
            if basetype == 'text':
                encoding = self.encoding or settings.DEFAULT_CHARSET
                attachment = SafeMIMEText(smart_str(content,
                    settings.DEFAULT_CHARSET), subtype, encoding)
            else:
                # Encode non-text attachments with base64.
                attachment = MIMEBase(basetype, subtype)
                attachment.set_payload(content)
                encoders.encode_base64(attachment)
            if filename:
                try:
                    filename = filename.encode('ascii')
                except UnicodeEncodeError:
                    filename = Header(filename, 'utf-8').encode()
                attachment.add_header('Content-Disposition', 'attachment',
                                       filename=filename)
            return attachment



def send_mail(subject='', body='', from_email=None, to=None, bcc=None, connection=None, attachments=None, headers=None, cc=None, spis_file=[]):
    content_subtype = 'plain'
    msg = EmailMessage(subject, body, from_email, to, bcc, connection, attachments, headers, cc)
    if spis_file:
        for file_name in spis_file:
            msg.attach(file_name.name, file_name.read(), file_name.content_type)
    msg.content_subtype = content_subtype
    return msg.send(fail_silently=True)

import threading

def send_mail_threaded(*args, **kwargs):
    """
    Wrapper for send_mail for use asynchronously in a thread
    """
    class Sender(threading.Thread):
        def run(self):
            try:
                send_mail(*args, **kwargs)
            except:
                pass
    Sender().start()
    return True

def send_mass_mail(datatuple, user_id, sender_id=None, fail_silently=False):

    connection = mail.get_connection()
    connection.open()
    success = 0
    fail = 0
    for subject, message, sender, recipient, attachments, html in datatuple:
        content_subtype = 'plain'
        if html:
            content_subtype = 'html'
        msg = EmailMultiAlternativesWithEncoding(subject, message, sender, [recipient])
        msg.content_subtype = content_subtype
        for attach in attachments:
            x = os.path.join(settings.MEDIA_ROOT, attach)
            msg.attach_file(x)
        try:
            msg.send(fail_silently=fail_silently)  # Send the email
            status_mail = True
            success += 1
        except:
            status_mail = False
            fail += 1
        mail_obj = Send_mail(
                subject=subject,
                message=message,
                date=datetime.datetime.now(),
                user_id=user_id,
                email=recipient,
                status_mail=status_mail,
                sender_id=sender_id,
                spis_file=', '.join(attachments),
                )
        mail_obj.save()
    connection.close()
    if sender_id:
        sender = Sender.objects.get(id=sender_id)
        sender.stop_date = datetime.datetime.now()
        sender.common_message = len(datatuple)
        sender.success_message = success
        sender.failed_message = fail
        sender.save()

def send_mass_mail_threaded(*args, **kwargs):
    """
    Wrapper for send_mass_mail for use asynchronously in a thread
    """
    class Sender(threading.Thread):
        def run(self):
            try:
                send_mass_mail(*args, **kwargs)
            except:
                pass
    thread = Sender()
    thread.daemon = True
    thread.start()
    return True

def send_email(subject, message, from_email, recipient_list, user_id=None, spis_file=[]):
    str_mail = ", ".join([item_mail for item_mail in recipient_list])
    if settings.SEND_EMAIL:
        str_filenames = ", ".join([item.name for item in spis_file]) if spis_file else ''
        try:
            send_mail(subject, message, from_email, recipient_list, spis_file=spis_file)
            status_mail = True
        except Exception, e:
            print 'send mail error = %s' % e
            status_mail = False
        mail_obj = Send_mail(
            subject=subject,
            message=message,
            date=datetime.datetime.now(),
            user_id=user_id,
            email=str_mail,
            spis_file=str_filenames,
            status_mail=status_mail)
        mail_obj.save()
