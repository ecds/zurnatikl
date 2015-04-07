# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.core.management import call_command


fixtures = ['continents', 'countries', 'states']

def load_fixture(apps, schema_editor):
    'Load fixtures for continents, countries, and states.'
    for f in fixtures:

        print '%sLoading %s...   ' % \
              ('\n' if f == fixtures[0] else '', f),
        call_command('loaddata', f, app_label='geo')

def unload_fixture(apps, schema_editor):
    'Remove all entries for continents, countries, and states.'

    # These geographic models are not user-editable,
    # so removing all of them should be fine.

    print '\nRemoving states'
    StateCode = apps.get_model("geo", "StateCode")
    StateCode.objects.all().delete()
    print 'Removing countries'
    GeonamesCountry = apps.get_model("geo", "GeonamesCountry")
    GeonamesCountry.objects.all().delete()
    print 'Removing continents'
    GeonamesContinent = apps.get_model("geo", "GeonamesContinent")
    GeonamesContinent.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0001_initial'),
    ]

    operations = [
    migrations.RunPython(load_fixture, reverse_code=unload_fixture, atomic=False)
    ]
