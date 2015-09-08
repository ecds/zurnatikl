from django.conf.urls import url
from zurnatikl.apps.journals.views import JournalList, JournalDetail, \
   IssueDetail, SearchView, AuthorEditorNetworkExport

urlpatterns = [
    url(r'^$', JournalList.as_view(), name='list'),
    url(r'^items/$', SearchView.as_view(), name='search'),
    url(r'^(?P<slug>[\w-]+)/$', JournalDetail.as_view(), name='journal'),
    url(r'^(?P<journal_slug>[\w-]+)/(?P<id>\d+)/$', IssueDetail.as_view(), name='issue'),
    url(r'^authors-editors.(?P<fmt>gexf|graphml)$', AuthorEditorNetworkExport.as_view(),
        name='authoreditor-graph-export'),
]