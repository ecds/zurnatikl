# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0002_continents_countries_states'),
        ('people', '0002_schools_multiple_locations'),
    ]

    operations = [
        migrations.RenameField(
            model_name='person',
            old_name='dwelling',
            new_name='dwellings'
        ),
        migrations.AlterField(
            model_name='person',
            name='dwellings',
            field=models.ManyToManyField(related_name='people', to='geo.Location', blank=True),
            preserve_default=True,
        ),
    ]
