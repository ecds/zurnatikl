from django.conf.urls import url
from zurnatikl.apps.journals import views


urlpatterns = [
    url(r'^$', views.JournalList.as_view(), name='list'),
    url(r'^items/$', views.SearchView.as_view(), name='search'),
    # journal contributor network urls
    url(r'^network/$', views.ContributorNetwork.as_view(), name='contributor-network'),
    url(r'^network.json$', views.ContributorNetworkJSON.as_view(), name='contributor-network-json'),
    url(r'^contributors.(?P<fmt>graphml|gml)$', views.ContributorNetworkExport.as_view(),
        name='contributor-network-export'),
    # greedier matching url patterns must come last
    url(r'^(?P<slug>[\w-]+)/$', views.JournalDetail.as_view(), name='journal'),
    url(r'^(?P<journal_slug>[\w-]+)/(?P<id>\d+)/$', views.IssueDetail.as_view(), name='issue'),

]