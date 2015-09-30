from zurnatikl.apps.content import views

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="network/index.html"),
        name='index'),
