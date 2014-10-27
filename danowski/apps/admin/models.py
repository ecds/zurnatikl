from django.contrib import admin
from django.db import models
from django.core.urlresolvers import reverse

def get_admin_url(obj):
    module_name = obj._meta.module_name.split('_')[0]
    id = obj.id
    url = "admin:%s_%s_change" % (obj._meta.app_label, module_name)
    for property, value in vars(obj).iteritems():
      if(property == module_name+"_id"):
        print property, ": ", value
        id = value
    return reverse(url, args=(id,))

class LinkedInline(admin.options.InlineModelAdmin):
    template = "admin/linked.html"
    admin_model_path = None
    admin_model_parent = 'people'

    def __init__(self, *args):
        super(LinkedInline, self).__init__(*args)
        if self.admin_model_path is None:
            self.admin_model_path = self.model.__name__.lower()
