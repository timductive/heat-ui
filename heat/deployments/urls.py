from django.conf.urls import patterns, url

from .views import IndexView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    #url(r'^launch/$', IndexView.as_view(), name='launch'),
    #url(r'^launch/(?P<template_name>[^/]+)/$', IndexView.as_view(), name='launch'),
)