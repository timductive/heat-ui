from django.conf.urls import patterns, url
from django.views.generic import RedirectView

from heat.common.views import TopologyView, LogView
from .views import IndexView

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='stacks/'), name='redirect'),
    url(r'^stacks/$', IndexView.as_view(), name='index'),
    url(r'^stacks/topology/(?P<stack_name>\w*)/$', TopologyView.as_view(), name='topology'),
    url(r'^stacks/logs/(?P<stack_name>\w*)/$', LogView.as_view(), name='logs'),
)