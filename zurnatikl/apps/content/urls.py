from django.conf.urls import patterns, url
from zurnatikl.apps.content import views
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', views.SiteIndex.as_view(), name='site-index'),
    url(r'^download/$', TemplateView.as_view(template_name="download.html"),
        name='download'),
]
