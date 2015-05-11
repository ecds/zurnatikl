from django.conf.urls import url
from danowski.apps.journals.views import JournalList, Journal

urlpatterns = [
    url(r'^$', JournalList.as_view(), name='list'),
    url(r'^journal/(?P<slug>[\w-]+)/$', Journal.as_view(), name='journal'),
]