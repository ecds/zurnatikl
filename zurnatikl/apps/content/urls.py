from django.conf.urls import patterns, url
from zurnatikl.apps.content import views
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', views.SiteIndex.as_view(), name='site-index'),
    url(r'^download/$', TemplateView.as_view(template_name="download.html"), name='download'),
    url(r'^download/people_csv$', views.people_csv, name='people_csv'),
    url(r'^download/journal_csv$', views.journal_csv, name='journal_csv'),
    url(r'^download/genre_csv$', views.genre_csv, name='genre_csv'),
    url(r'^download/item_csv$', views.journal_csv, name='item_csv')
]
