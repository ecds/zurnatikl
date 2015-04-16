from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from danowski.apps.network import views

urlpatterns = patterns('',
    url(r'^data.(?P<fmt>gexf|graphml)$', views.export_network, name='network-data'),
)