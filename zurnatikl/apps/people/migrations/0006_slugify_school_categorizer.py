# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def slugify_school_categorizer(apps, schema_editor):
    'Convert plain-text school categorizer into slug format.'

    School = apps.get_model('people', 'School')
    for s in School.objects.all():
        if s.categorizer == 'Donald Allen':
            s.categorizer = 'donald-allen'
            s.save()
        # warn otherwise?


def unslugify_school_categorizer(apps, schema_editor):
    'Convert slug format school categorizer back into plain-text version.'

    School = apps.get_model('people', 'School')
    for s in School.objects.all():
        if s.categorizer == 'donald-allen':
            s.categorizer == 'Donald Allen'
            s.save()
        # warn otherwise?


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0005_add_person_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='categorizer',
            field=models.CharField(blank=True, max_length=100, choices=[(b'donald-allen', b'Donald Allen')]),
        ),
        migrations.RunPython(slugify_school_categorizer, reverse_code=unslugify_school_categorizer)
    ]
