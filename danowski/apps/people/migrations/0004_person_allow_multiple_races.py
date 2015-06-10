# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0003_person_dwelling_to_dwellings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='race',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, max_length=200, choices=[(b'American Indian or Alaska Native', b'American Indian or Alaska Native'), (b'Asian', b'Asian'), (b'Black or African American', b'Black or African American'), (b'Hispanic', b'Hispanic'), (b'Latino', b'Latino'), (b'Native Hawaiian or Other Pacific Islander', b'Native Hawaiian or Other Pacific Islander'), (b'White', b'White')]),
            preserve_default=True,
        ),
    ]
