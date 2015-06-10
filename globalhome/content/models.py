# coding: utf-8
from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from content_variables.models import VariableSet
from content.TemplateVars import ModulesManager
import mptt
import log
from ckeditor.fields import RichTextField as HTMLField
from lib.db.models.fields import ExtendedURLField
from south.modelsinspector import add_introspection_rules
from django.db.transaction import managed
from page.models import Menu_on_globalhome, Menu_on_moscowdata

rules = [
            (
                (HTMLField,), [],
                {
                    "verbose_name": ["verbose_name", {"default": None}],
                }
            ),
        ]

add_introspection_rules(rules, ["^ckeditor\.fields"])

class BaseContent(models.Model):
    created_by = models.ForeignKey(User, editable=False, verbose_name=_('Created by'))
    created_at = models.DateTimeField(editable=False, verbose_name=_('Created at'),)
    modified_at = models.DateTimeField(editable=False, verbose_name=_('Modified at'))
    # modified_by = models.ForeignKey(User, editable = False, verbose_name = _('Modified by'), related_name = "modified_by_related")
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    text = HTMLField(null=True, blank=True, verbose_name=_('Text'))

    variablesets = models.ManyToManyField(VariableSet, verbose_name=_(u"Variables sets"), null=True, blank=True)

    def __unicode__(self):
        return self.name

    def processVars(self, fields, *args, **kwargs):
        "Заметь, я тут ничего не возвращаю, недотёпа ты!!!"

        #try:
        var_modules = self.variablesets.all()
        mm = ModulesManager()
        for mod in var_modules:
            mm.load(mod.module)
        for field in fields:
            if hasattr(self, field):
                kwargs["content_obj"] = self
                setattr(self, field, mm.processTemplate(getattr(self, field), *args, **kwargs))

        #except Exception, exc:
        #    log.add("Exception in BaseContent.processVars: '%s'" % exc)

    class Meta:
        abstract = True

class FrontendTextContentManager(models.Manager):

    def get_query_set(self):
        qs = super(FrontendTextContentManager, self).get_query_set()
        return qs.filter(is_published=True)

class BaseTextContent(BaseContent):

    class Meta:
        abstract = True


#    meta_title = models.CharField(max_length=255, blank=True, verbose_name=_('META TITLE'))
#    meta_description = models.TextField(null=True, blank=True, verbose_name=_('META DESCRIPTION'))
#    meta_keywords = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('META KEYWORDS'))

#    summary = HTMLField(null=True, blank=True, verbose_name=_('Summary'))
#    url = ExtendedURLField(max_length=255, null=True, blank=True, verbose_name=_('Url'), help_text=_(u'If not empty, user will be forwarded to this url. Relative (local) urls must start with "/" and must be valid site url.'))

    is_published = models.BooleanField(default=True, blank=True, verbose_name=_(u'Is published'))

    objects = models.Manager()
    frontend_objects = FrontendTextContentManager()

    def get_absolute_url(self):
        if self.url:
            return self.url
        return '/%s/%s/%s/' % (self._meta.app_label, self._meta.object_name.lower(), self.id)


# class Check(BaseContent):
#
#
#    type = models.CharField(max_length = 255)
#    sent = models.BooleanField(default = False, null = False)
#    number = models.IntegerField(null = True)
#    paid = models.BooleanField(default = True)
#    zakaz_id = models.BigIntegerField(null = True)
#    every_month = models.BooleanField(default = False)
#    message_on_warning = models.IntegerField(null = True, default = 0)
#    section_type = models.IntegerField(null = True)
#    class Meta:
#        verbose_name = _(u'Check')
#        verbose_name_plural = _(u'Check')


class Universityinform(models.Model):

    name = models.CharField(max_length=255, verbose_name=_('Password'), null=True, unique=True)

    class Meta:

        verbose_name = _(u'Information on university')
        verbose_name_plural = _(u'Information on university')

class Hostelinform(models.Model):
    mac = models.CharField(max_length=17, verbose_name=_('Mac'), null=True, blank=True,)
    floor = models.CharField(max_length=2, verbose_name=_('Floor'), null=True, blank=True)
    block = models.CharField(max_length=32, verbose_name=_('Block'), null=True, blank=True)
    room = models.CharField(max_length=32, verbose_name=_('Room'), null=True, blank=True)
    install_date = models.DateTimeField(verbose_name=_('Install date'), blank=True,)
    install_name = models.CharField(max_length=255, verbose_name=_("Who's install"), null=True, blank=True,)
    signed_act = models.CharField(max_length=255, verbose_name=_('Signed the act'), null=True, blank=True,)
    install_note = models.CharField(max_length=255, verbose_name=_("Note Installer"), null=True, blank=True,)

    ip = models.IPAddressField(verbose_name=_('IP'))
    number = models.CharField(max_length=7, verbose_name=_('Number'), null=True, blank=True)
    short_number = models.CharField(max_length=4, verbose_name=_('Short_number'), null=True, blank=True)
    password = models.CharField(max_length=255, verbose_name=_('Password'), null=True, blank=True)
    settings = models.BooleanField(default=False, verbose_name=_('settings'), blank=True,)
    note = models.TextField(null=True, blank=True, verbose_name=_('Note'))

    status = models.BooleanField(default=True, blank=True, verbose_name=_(u'Activated'))
    university_name = models.ForeignKey(Universityinform, blank=True, null=True)
    hostel_number = models.CharField(max_length=255, verbose_name=_('Hostel number'), null=True, blank=True,)

    class Meta:

        verbose_name = _(u'Information on hostel')
        verbose_name_plural = _(u'Information on hostel')


class Prefix_article(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    prefix = models.CharField(max_length=255)
    def __unicode__(self):
        return u'%s' % self.prefix

    class Meta:
        verbose_name = u'Префиксы статей'

class Article(BaseTextContent):

    class Meta:
        ordering = ('lft',)
        verbose_name = _(u'Article')
        verbose_name_plural = _(u'Articles')

    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', editable=False)
    slug = models.SlugField(max_length=255, null=True, blank=True, verbose_name=_(u'Slug'), help_text=_(u'Character identifier of the article. Can be used in url instead of numerical ID.'))

class Article_moscowdata(BaseTextContent):

    class Meta:
        ordering = ('lft',)
        verbose_name = u'Статьи moscowdata'

    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', editable=False)
    slug = models.CharField(max_length=255, null=True, blank=True, verbose_name=_(u'Slug'), help_text=_(u'Character identifier of the article. Can be used in url instead of numerical ID.'))
    prefix = models.ForeignKey(Prefix_article)


NEWS_CATEGORY_COMMON = 0
NEWS_CATEGORY_CHOICES = (
                         (NEWS_CATEGORY_COMMON, _('Common')),
                         )



class News(BaseTextContent):

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _(u'News story')
        verbose_name_plural = _(u'News stories')

    category = models.IntegerField(choices=NEWS_CATEGORY_CHOICES, default=NEWS_CATEGORY_COMMON, verbose_name=_('Category'))


class News_Moscowdata(BaseTextContent):
    class Meta:
        ordering = ('-created_at',)


try:
    mptt.register(Article)
    mptt.register(Article_moscowdata)
except:
    pass

class Section_type(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    name = models.CharField(max_length=50)
    about = models.CharField(max_length=255, blank=True, null=True)
    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "section_type"



class ButtonPanelHref(models.Model):
    key = models.CharField(max_length=50, primary_key=True,)
    description_action = models.CharField(max_length=150)
    description_key = models.CharField(max_length=150)
    how_much_action = models.CharField(max_length=150)
    how_much_key = models.CharField(max_length=150)
    how_to_connect_action = models.CharField(max_length=150)
    how_to_connect_key = models.CharField(max_length=150)
    where_to_go_action = models.CharField(max_length=150)
    where_to_go_key = models.CharField(max_length=150)

    def __unicode__(self):
        return self.key

    class Meta:
        db_table = "buttons_panel_href"
        verbose_name = (u'конфигурация URL')
        verbose_name_plural = (u'конфигурация URL')


class ButtonPanelUrls(models.Model):
    key = models.ForeignKey(ButtonPanelHref)
    urls = models.CharField(max_length=150)

    class Meta:
        db_table = "button_panel_urls"
        verbose_name = (u' URL по умолчанию')
        verbose_name_plural = (u'URL по умолчанию')

