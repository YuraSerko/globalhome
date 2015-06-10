# coding: utf-8
from django.utils.translation import ugettext as _
from django.utils.html import mark_safe
from widget.core import Library, Widget, WidgetParamInteger, WidgetParamHtml, ImproperlyConfigured
#from django.conf import settings
from django.conf import settings

class LastNewsWidget(Widget):
    class Meta:
        verbose_name = _(u'Last news items')
        description = _(u'Last news items')

    amount = WidgetParamInteger(value=0, verbose_name=_(u'Amount'))

    template = 'content/news/widgets/last_news_widget.html'

    def process(self):
        from content.models import News
        amount = self.params['amount'].value
        news = News.frontend_objects.all()[0:amount]
        request = settings.GLOBAL_OBJECTS["request"]
        for n in news:
            n.processVars(("text", "summary"), request = request)
        return {
                'news': news,
                } 
class HtmlWidget(Widget):
    class Meta:
        verbose_name = _(u'Html')
        description = _(u'Text, formatted as html')

    content = WidgetParamHtml(verbose_name=_('Content'))

    def process(self):
        return {
                'content': self.params['content'].value,
                }

    def render(self):
        return mark_safe(self.process()['content'])

Library.register(LastNewsWidget)
Library.register(HtmlWidget)

