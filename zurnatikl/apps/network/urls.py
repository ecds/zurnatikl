from django.conf.urls import patterns, url
from zurnatikl.apps.network import views

urlpatterns = patterns('',
    url(r'^data.(?P<fmt>gexf|graphml)$', views.FullNetworkExport.as_view(),
        name='data'),
    # network graphs based on "schools"
    url(r'^schools/(?P<slug>[\w-]+)/$', views.SchoolsNetwork.as_view(),
        name='schools'),
    url(r'^schools/(?P<slug>[\w-]+).json$', views.SchoolsNetworkJSON.as_view(),
        name='schools-json'),
    url(r'^schools/(?P<slug>[\w-]+).(?P<fmt>gexf|graphml)$',
        views.SchoolsNetworkExport.as_view(), name='schools-export'),
)