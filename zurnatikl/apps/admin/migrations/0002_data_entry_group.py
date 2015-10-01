# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.core.management import call_command
from django.core.serializers.base import DeserializationError


fixture = 'data_entry_group'

def load_fixture(apps, schema_editor):
    'Load fixture with Data Entry group permissions.'

    # NOTE: this migration is problematic because it depends on
    # other models *and* their permissions to be created
    # See the relevant bug (closed as won't fix):
    # https://code.djangoproject.com/ticket/23422

    try:
        call_command('loaddata', fixture, app_label='zurnatikl_admin')
    except DeserializationError:
        print '**WARNING**: failed to load Data Entry group fixture.'
        print 'To load manually, run: python manage.py loaddata data_entry_group'


def unload_fixture(apps, schema_editor):
    'Remove Data Entry group.'

    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name="Data Entry").delete()

class Migration(migrations.Migration):

    dependencies = [
        ('zurnatikl_admin', '0001_initial'),
        ('auth', '0001_initial'),
        ('contenttypes', '0001_initial'),
        # apps whose permissions we want to include
        ('geo', '0002_continents_countries_states'),
        ('people', '0001_initial'),
        ('journals', '0002_load_genres'),
    ]

    operations = [
       migrations.RunPython(load_fixture, reverse_code=unload_fixture)
    ]
