from django.conf.urls import patterns, url
from zurnatikl.apps.content import views
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', views.SiteIndex.as_view(), name='site-index'),
    url(r'^download/$', TemplateView.as_view(template_name="download.html"),
        name='download'),
    url(r'^download/people.csv$', views.PeopleCSV.as_view(), name='people_csv'),
    url(r'^download/journal-issues.csv$', views.JournalIssuesCSV.as_view(),
        name='journal_csv'),
    url(r'^download/journal-items.csv$', views.JournalItemsCSV.as_view(), name='item_csv')
]
