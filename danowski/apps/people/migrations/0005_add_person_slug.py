# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.text import slugify

def set_slug_from_name(apps, schema_editor):
    # set initial slugs based on person name
    Person = apps.get_model("people", "person")
    name_slugs = set()
    for p in Person.objects.all():
        p.slug = slug = slugify('%s %s' % (p.first_name, p.last_name))
        i = 1
        # if somehow a slug is not unique, add numbers until it is
        # (but warn because this is probably a data-entry error)
        while p.slug in name_slugs:
            print '\nWarning: duplicate name slug for %s' % p.slug
            p.slug = '%s%d' % (slug, i)
            i += 1

        name_slugs.add(p.slug)
        p.save()


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0004_person_allow_multiple_races'),
    ]

    operations = [
        # add slug as non-unique
        migrations.AddField(
            model_name='person',
            name='slug',
            field=models.SlugField(help_text=b'Short name for use in URLs. Change carefully, since editing this field this changes the URL on the site.', blank=True),
            preserve_default=False,
        ),
        # pre-set slug values
        migrations.RunPython(set_slug_from_name, migrations.RunPython.noop),
        # then set slug to be unique
        migrations.AlterField(
            model_name='person',
            name='slug',
            field=models.SlugField(help_text=b'Short name for use in URLs. Change carefully, since editing this field this changes the URL on the site.', unique=True, blank=False),
            preserve_default=False,
        ),
    ]
