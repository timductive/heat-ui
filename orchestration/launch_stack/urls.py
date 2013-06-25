from django.conf.urls import patterns, url

from orchestration.stacks.views import LaunchStackView, LaunchHeatView
from .views import IndexView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^launch/new/$', LaunchStackView.as_view(), name='launchnew'),
    url(r'^launch$', LaunchHeatView.as_view(), name='launch'),
)