# coding: utf-8
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
import datetime
from page.models import LeftBlockMenuPage

COMMENT_MAX_LENGTH = 3000

SECTIONS = {3: u'Доступ в интернет',
            1: u'Телефония',
            2: u'Услуги дата-центра',
            4: u'Другое',
            }




class Review(models.Model):
    user = models.ForeignKey(User, verbose_name=_('user'),
                    null=True, related_name="%(class)s_comments")
    parent = models.ForeignKey('self', null=True, verbose_name=u'Ответ на отзыв') 
    user_name = models.CharField(_("user's name"), max_length=50, blank=True)
    user_email = models.EmailField(_("user's email address"), blank=True)
#     section = models.CharField(max_length=127, verbose_name=u'Раздел')
    section = models.IntegerField(verbose_name=u'Раздел', null=True, choices=[[key, value] for key, value in SECTIONS.items()])
    comment = models.TextField(_('review'), max_length=COMMENT_MAX_LENGTH)
    created_at = models.DateTimeField(_('date/time submitted'), default=datetime.datetime.now())
    is_public = models.BooleanField(_(u'Подтверждено администратором'), default=False,
                    help_text=_('Uncheck this box to make the comment effectively ' \
                                'disappear from the site.'))


    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.comment = self.comment.strip()
        self.created_at = self.created_at if(self.created_at) else datetime.datetime.now()
        return super(Review, self).save(force_insert, force_update, using, update_fields)


    def __unicode__(self):
        return '%s section %s: %s' % (self.user_name, self.section, self.comment[:20])


    class Meta:
        db_table = u'reviews_review'
        verbose_name = u'Отзыв'
        verbose_name_plural = u'Отзывы пользователей'
        

