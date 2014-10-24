from django.contrib import admin
from django.db import models

class LinkedInline(admin.options.InlineModelAdmin):
    template = "admin/linked.html"
    admin_model_path = None
    admin_model_parent = 'people'

    def __init__(self, *args):
        super(LinkedInline, self).__init__(*args)
        if self.admin_model_path is None:
            self.admin_model_path = self.model.__name__.lower()
