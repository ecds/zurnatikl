from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView

from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin

from ajax_select import urls as ajax_select_urls


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="site_index.html"),
        name='site-index'),
    url(r'^about/$', TemplateView.as_view(template_name="about.html"),
        name='about'),
    url(r'^network/', include('zurnatikl.apps.network.urls',
        namespace='network')),
    url(r'^journals/', include('zurnatikl.apps.journals.urls',
        namespace='journals')),
    url(r'^people/', include('zurnatikl.apps.people.urls',
        namespace='people')),
    (r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^admin/', include(admin.site.urls) ),

)

urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
