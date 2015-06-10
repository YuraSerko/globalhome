# -*- coding=utf-8 -*-

import os

import threading
from django.core.mail import EmailMessage, EmailMultiAlternatives#, SMTPConnection,
from django.conf import settings

from BeautifulSoup import BeautifulSoup
from os.path import basename, splitext

from django.template import Template, Context
from settings import CHARSET
from django.conf import settings

from lib.mail import send_email

from models import Letter

def get_language():
    try:
        return settings.ADMINMAIL_LANGUAGE
    except AttributeError:
        return 'en'

def src2cid(html):
    """
    Process html body and replace all img src with subsequent cid
    Returns:
    (
        parsed_html_body,
        images=(('email_images/logo.gif','img1'),('email_images/footer.gif','img2'))
    )
    """
    soup = BeautifulSoup(html)
    images = []
    for i, img in enumerate(soup.findAll('img')):
        cid = u"img%d" % i
        images.append((os.path.join(settings.MEDIA_ROOT,img['src']),cid))
        img['src'] = 'cid:%s' % cid
    return (unicode(soup), images)


class EmbeddedImageEmailMessage(EmailMultiAlternatives):
    #multipart_subtype = 'related'

    def attach_image(self, image_data, content_id):
        attachment = MIMEImage(image_data)
        attachment.add_header('Content-ID', '<%s>' % content_id)

        self.attach(attachment)

def named(mail,name):
   if name: return '%s <%s>' % (name,mail)
   return mail

def createmail(subject, htmltemplate='',texttemplate='', context={}, attachments=[]):
    """
    if you want to use Django template system:
       use `context` as template context (dict)
       and define `htmltemplate` and optionally `texttemplate` variables.
    """

    htmltemplate, images = src2cid(htmltemplate)

    html = Template(htmltemplate).render(Context(context))
    text = Template(texttemplate).render(Context(context))
    subject = Template(subject).render(Context(context))

    # creating mail object
    msg = EmailMultiAlternatives(subject='', body=text, from_email=None, to=None)
    msg.attach_alternative(html, "text/html")

    for img_path, img_cid in images:
        try:
            fp = open(os.path.join(settings.MEDIA_ROOT,img_path, 'rb'))
            cnt = fp.read()
            fp.close()
            msg.attach_image(cnt, img_cid)
        except:
            pass
    for attachment in attachments:
        msg.attach_file(attachment)
    return msg

def render(context,template):
    if template:
       t = loader.get_template(template)
       return t.render(Context(context))
    return context

def named(mail,name):
    if name: return '%s <%s>' % (name,mail)
    return mail

def msg_from_letter(letter_object, context={}, email_from=settings.DEFAULT_FROM_EMAIL, to=[]):
    attachments = []
    for a in letter_object.attachment_set.all():
        print os.path.join(settings.MEDIA_ROOT, a.attached.path)
        attachments.append(os.path.join(settings.MEDIA_ROOT, a.attached.path))
    msg = createmail(subject=letter_object.subject, \
                     htmltemplate=letter_object.htmltemplate, \
                     texttemplate=letter_object.texttemplate, \
                     context=context,
                     attachments=attachments
                     )
    msg.email_from = email_from
    msg.to = to
    return msg

class MassMailLetterWithCommonSubject(threading.Thread):
    def __init__(self, code, language_code, context, email_from, to):
        try:
            self.letter = Letter.objects.get(code=code, language_code=language_code)
        except Letter.DoesNotExist:
            return False
        self.context = context
        self.email_from = email_from
        self.to = to
        threading.Thread.__init__(self)

    def run(self):
        connection = SMTPConnection(settings.EMAIL_HOST, settings.EMAIL_PORT, settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD, False, False)
        for email in self.to:
            message = msg_from_letter(self.letter, self.context, self.email_from, [email])
            connection.send_messages([message])

def send_adminmail_simple(code, language_code, context, email_from, to, user_id):
    """
    Render textfield only
    """
    try:
        letter = Letter.objects.get(code=code, language_code=language_code)
    except Letter.DoesNotExist:
        return False
    subject = Template(letter.subject).render(Context(context))
    text = Template(letter.texttemplate).render(Context(context))
    return send_email(subject, text, email_from, to, user_id)

