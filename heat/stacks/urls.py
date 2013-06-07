from django.conf.urls import patterns, url

from heat.common.views import TopologyView, LogView
from .views import IndexView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^topology/(?P<stack_name>\w*)/$', TopologyView.as_view(), name='topology'),
    url(r'^logs/(?P<stack_name>\w*)/$', LogView.as_view(), name='logs'),
)