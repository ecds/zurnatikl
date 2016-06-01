# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stdimage.models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=stdimage.models.StdImageField(upload_to=b''),
        ),
    ]
