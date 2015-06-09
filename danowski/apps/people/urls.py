from django.conf.urls import url
from .views import PeopleList, PersonDetail, PersonEgograph, \
   PersonEgographJSON

urlpatterns = [
    url(r'^$', PeopleList.as_view(), name='list'),
    url(r'^(?P<slug>[\w-]+)/$', PersonDetail.as_view(), name='person'),
    url(r'^(?P<slug>[\w-]+)/egograph.json$', PersonEgographJSON.as_view(),
        name='egograph-json'),
    url(r'^(?P<slug>[\w-]+)/egograph/$', PersonEgograph.as_view(),
        name='egograph'),
]