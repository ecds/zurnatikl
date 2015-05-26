from django.conf.urls import url
from danowski.apps.journals.views import JournalList, JournalDetail, \
   IssueDetail

urlpatterns = [
    url(r'^$', JournalList.as_view(), name='list'),
    url(r'^(?P<slug>[\w-]+)/$', JournalDetail.as_view(), name='journal'),
    url(r'^(?P<journal_slug>[\w-]+)/(?P<id>\d+)/$', IssueDetail.as_view(), name='issue'),
]