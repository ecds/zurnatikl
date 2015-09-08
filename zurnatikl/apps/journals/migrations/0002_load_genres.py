# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from django.db import models, migrations
from django.core.management import call_command
from django.core import serializers

fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'fixtures'))
fixture = 'genres'

def load_fixture(apps, schema_editor):
    'Load fixture with predefined genres.'
    call_command('loaddata', fixture, app_label='journals')

def unload_fixture(apps, schema_editor):
    'Remove predefined genres.'
    fixture_file = os.path.join(fixture_dir, '%s.json' % fixture)

    # load the fixture and remove genres with matching ids
    with open(fixture_file, 'rb') as fixture_data:
        objects = serializers.deserialize('json', fixture_data,
            ignorenonexistent=True)
        fixture_ids = [obj.object.pk for obj in objects]

    Genre = apps.get_model('journals', 'Genre')
    Genre.objects.filter(pk__in=fixture_ids).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('journals', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture)
    ]
