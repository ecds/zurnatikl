# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.core.management import call_command


fixture = 'data_entry_group'

def load_fixture(apps, schema_editor):
    'Load fixture with Data Entry group permissions.'
    call_command('loaddata', fixture, app_label='danowski_admin')

def unload_fixture(apps, schema_editor):
    'Remove Data Entry group.'

    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name="Data Entry").delete()

class Migration(migrations.Migration):

    dependencies = [
        ('danowski_admin', '0001_initial'),
        ('auth', '0001_initial'),
    ]

    operations = [
       migrations.RunPython(load_fixture, reverse_code=unload_fixture)
    ]
