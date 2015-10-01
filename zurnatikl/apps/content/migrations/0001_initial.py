# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=b'')),
                ('title', models.CharField(max_length=255)),
                ('alt_text', models.CharField(max_length=255, blank=True)),
                ('caption', models.TextField(blank=True)),
                ('homepage', models.BooleanField(default=False, help_text=b'Use as a homepage image')),
                ('banner', models.BooleanField(default=False, help_text=b'Use as a site banner image')),
            ],
        ),
    ]
