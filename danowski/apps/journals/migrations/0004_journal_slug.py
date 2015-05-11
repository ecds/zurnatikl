# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.text import slugify


def set_slug_from_title(apps, schema_editor):
    # set initial slugs based on object title
    Journal = apps.get_model("journals", "Journal")
    for j in Journal.objects.all():
        j.slug = slugify(j.title)
        j.save()

class Migration(migrations.Migration):

    dependencies = [
        ('journals', '0003_clean_field_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal',
            name='slug',
            field=models.SlugField(blank=True),
            preserve_default=False,
        ),
        migrations.RunPython(set_slug_from_title),
        # then set slug to be unique
        migrations.AlterField(
            model_name='journal',
            name='slug',
            field=models.SlugField(unique=True),
            preserve_default=False,
        ),
    ]
