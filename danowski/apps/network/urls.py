from django.conf.urls import patterns, url
from danowski.apps.network import views

urlpatterns = patterns('',
    url(r'^data.(?P<fmt>gexf|graphml)$', views.FullNetworkExport.as_view(),
        name='data'),
)