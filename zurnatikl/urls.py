from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin

from ajax_select import urls as ajax_select_urls


admin.autodiscover()

urlpatterns = patterns('',
    # until we have a public-facing site homepage, redirect to journals
    url(r'^$', RedirectView.as_view(url='/journals/', permanent=False),
        name='site-index'),
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
