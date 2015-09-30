from django.contrib import admin
from sorl.thumbnail.admin import AdminImageMixin

from .models import Image

class ImageAdmin(admin.ModelAdmin, AdminImageMixin):
    list_display = ('title', 'homepage', 'banner', 'admin_thumbnail')
    list_filter = ('homepage', 'banner')

admin.site.register(Image, ImageAdmin)
