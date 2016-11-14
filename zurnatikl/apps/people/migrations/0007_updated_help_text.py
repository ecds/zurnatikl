# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0006_slugify_school_categorizer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='slug',
            field=models.SlugField(help_text=b'Short name for use in URLs. Leave blank to have a slug automatically generated. Change carefully, since editing this field this changes the URL on the site.', unique=True, blank=True),
        ),
        migrations.AlterField(
            model_name='school',
            name='locations',
            field=models.ManyToManyField(related_name='schools', to='geo.Location', blank=True),
        ),
    ]
