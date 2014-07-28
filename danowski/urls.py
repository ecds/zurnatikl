from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
     url(r'^$', RedirectView.as_view(url='/admin', permanent=False)), # temp redirect to admin

    url(r'^admin/', include(admin.site.urls)),
)
