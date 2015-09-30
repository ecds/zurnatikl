from django.db import models
from django.utils.safestring import mark_safe

from stdimage.models import StdImageField


class ImageQuerySet(models.QuerySet):
    def homepage_images(self):
        return self.filter(homepage=True)

    def banner_images(self):
        return self.filter(banner=True)

class ImageManager(models.Manager):
    def get_queryset(self):
        return ImageQuerySet(self.model, using=self._db)

    def homepage_images(self):
        return self.get_queryset().homepage_images()

    def banner_images(self):
        return self.get_queryset().banner_images()

class Image(models.Model):
    image = StdImageField(
        variations={
            # for convenience / display in admin
            'thumbnail': {'width': 50, 'height': 50, 'crop': True},
            # sizes needed for site design use
            'homepage': {'width': 479, 'height': 273, 'crop': True},
            'homepage_sm': {'width': 320, 'height': 176, 'crop': True},
            'banner': {'width': 479, 'height': 190, 'crop': True},
            'banner_sm': {'width': 320, 'height': 127, 'crop': True},
        })
    title = models.CharField(max_length=255)
    alt_text = models.CharField(max_length=255, blank=True)
    caption = models.TextField(blank=True)
    # future: rights/permissions statement?

    homepage = models.BooleanField(default=False,
        help_text='Use as a homepage image')
    banner = models.BooleanField(default=False,
        help_text='Use as a site banner image')

    objects = ImageManager()

    def __unicode__(self):
        return self.title

    def admin_thumbnail(self):
        return mark_safe('<img src="%s"/>' % self.image.thumbnail.url)

    admin_thumbnail.short_description = 'thumbnail'

