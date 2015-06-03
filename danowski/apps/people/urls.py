from django.conf.urls import url
from .views import PeopleList

urlpatterns = [
    url(r'^$', PeopleList.as_view(), name='list'),
]