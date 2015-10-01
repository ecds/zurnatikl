# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def copy_location_to_locations(apps, schema_editor):
    # forward migration:
    # copy single location to multiple location field
    School = apps.get_model("people", "School")
    for s in School.objects.all():
        if s.location:
            s.locations.add(s.location)
            s.save()

def copy_locations_to_location(apps, schema_editor):
    # backward migration:
    # copy first of multiple locations to single location field
    School = apps.get_model("people", "School")
    for s in School.objects.all():
        s.location = s.locations.first()
        s.save()


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0002_continents_countries_states'),
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='locations',
            field=models.ManyToManyField(related_name='schools', null=True, to='geo.Location', blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='school',
            unique_together=set([('name', 'categorizer')]),
        ),
        migrations.RunPython(
            copy_location_to_locations,
            copy_locations_to_location),
        migrations.RemoveField(
            model_name='school',
            name='location',
        ),
    ]
