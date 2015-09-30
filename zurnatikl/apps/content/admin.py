from django.contrib import admin

from .models import Image

class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'homepage', 'banner', 'admin_thumbnail')
    list_filter = ('homepage', 'banner')

admin.site.register(Image, ImageAdmin)
