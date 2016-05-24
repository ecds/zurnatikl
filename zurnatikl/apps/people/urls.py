from django.conf.urls import url
from .views import PeopleList, PersonDetail, Egograph, \
   EgographJSON, EgographExport

urlpatterns = [
    url(r'^$', PeopleList.as_view(), name='list'),
    url(r'^(?P<slug>[\w-]+)/$', PersonDetail.as_view(), name='person'),
    url(r'^(?P<slug>[\w-]+)/egograph/$', Egograph.as_view(),
        name='egograph'),
    url(r'^(?P<slug>[\w-]+)/egograph.json$', EgographJSON.as_view(),
        name='egograph-json'),
    url(r'^(?P<slug>[\w-]+)/egograph.(?P<fmt>graphml|gml)$', EgographExport.as_view(),
        name='egograph-export'),
]