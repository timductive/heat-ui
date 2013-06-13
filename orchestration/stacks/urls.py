from django.conf.urls import patterns, url
from django.views.generic import RedirectView

from orchestration.common.views import TopologyView, LogView
from .views import DetailView, IndexView, LaunchStackView, ResourceView

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='stacks/'), name='redirect'),
    url(r'^stacks/$', IndexView.as_view(), name='index'),


    url(r'^launch$', LaunchStackView.as_view(), name='launch'),
    url(r'^stacks/overview/(?P<stack_id>[^/]+)/$', DetailView.as_view(), name='detail'),
    url(r'^stacks/overview/(?P<stack_id>[^/]+)/(?P<resource_name>[^/]+)/$',ResourceView.as_view(), name='resource'),


    url(r'^stacks/topology/(?P<stack_name>\w*)/$', TopologyView.as_view(), name='topology'),
    url(r'^stacks/logs/(?P<stack_name>\w*)/$', LogView.as_view(), name='logs'),
)