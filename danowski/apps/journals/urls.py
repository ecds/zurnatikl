from django.conf.urls import url
from danowski.apps.journals.views import JournalList

urlpatterns = [
    url(r'^$', JournalList.as_view(), name='list'),
]