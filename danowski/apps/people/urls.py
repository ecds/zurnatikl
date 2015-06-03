from django.conf.urls import url
from .views import PeopleList, PersonDetail

urlpatterns = [
    url(r'^$', PeopleList.as_view(), name='list'),
    url(r'^(?P<slug>[\w-]+)/$', PersonDetail.as_view(), name='person'),
]