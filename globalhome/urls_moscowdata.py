# coding: utf-8
from urls import *

urlpatterns += patterns('data_centr.views',
    url("^service/colocation-server/$", "colocation", name="colocation"),
    url("^service/dedicated-server/$", "dedicated", name="dedicated"),
    url("^service/server-rack/$", "rack", name="rack"),
)

urlpatterns += patterns('content.views',
    url(r'^(?P<prefix>[-\w]+)/(?P<slug>[-\w]+)/$', 'moscow_article_by_slug', name='moscow_article_by_slug'),
    url(r'^news/$', 'news_list', name='news_list'),
    url(r'^news/(?P<id>\d+)/$', 'news', name='news'),
    url("^service/$", "data_centr", name="data_centr"),
    url("^payment/$", "payment", name="payment"),
    url("^type_service/$", "type_service", name="type_service"),
)
