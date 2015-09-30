from django.conf.urls import patterns, url
from zurnatikl.apps.content import views

urlpatterns = patterns('',
    url(r'^$', views.SiteIndex.as_view(), name='site-index'),
)