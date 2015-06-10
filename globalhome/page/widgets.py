# coding: utf-8
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType

from lib.text_processing.html_parser import HtmlParser

from widget.core import Library, Widget, WidgetParamHtml, WidgetParamPlainText, WidgetParamUnicode, ImproperlyConfigured

class HomepageServiceListWidget(Widget):

    class Meta:
        verbose_name = _(u'Homepage servise list widget')
        description = _(u'List of services in the middle part of the homepage')

    content = WidgetParamHtml(value=u'', verbose_name=_(u'Content'))

    template = 'page/widgets/homepage_service_list_widget.html'

    def process(self):
        html = self.params['content'].value
        parser = HtmlParser(html).config(allowed_tags=['li', 'a'], allowed_attrs=['href'])
        cleaned = parser.clean()
        return {
                'content': cleaned,
                }

class HomepageServiseAnnounceWidget(Widget):
    class Meta:
        verbose_name = _(u'Homepage servise announce widget')
        description = _(u'Text with a brace at the left side')

    title = WidgetParamUnicode(value=u'', verbose_name=_(u'Title'), required=False)
    content = WidgetParamPlainText(value=u'', verbose_name=_(u'Content'))
    url = WidgetParamUnicode(value=u'', verbose_name=_(u'Url'), required=False)

    template = 'page/widgets/homepage_service_announce_widget.html'

    def process(self):
        title = HtmlParser(self.params['title'].value).clean()
        content = self.params['content'].value.strip().replace('\n', '<br />')

#        content = HtmlParser(self.params['content'].value).config(allowed_tags=['p', 'a', 'br'], allowed_attrs=['href']).clean()
        return {
                'title': title,
                'content': content,
                'url': self.params['url'].value,
                'widget': self.context.get('widget'),
                }

class HomepageBottomTextblockWidget(Widget):

    class Meta:
        verbose_name = _(u'Homepage bottom text block')
        description = _(u'Widget for publishing an arbitrary html code in columns at the bottom of homepage')

    content = WidgetParamHtml(value=u'', verbose_name=_(u'Content'))
    template = 'page/widgets/homepage_bottom_textblock.html'

    def process(self):
        return {
                'content': self.params['content'].value
                }

Library.register(HomepageServiceListWidget)
Library.register(HomepageServiseAnnounceWidget)
Library.register(HomepageBottomTextblockWidget)
