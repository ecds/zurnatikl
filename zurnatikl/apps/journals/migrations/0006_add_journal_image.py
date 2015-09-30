# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stdimage.models


class Migration(migrations.Migration):

    dependencies = [
        ('journals', '0005_add_issue_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal',
            name='image',
            field=stdimage.models.StdImageField(upload_to=b'', blank=True),
        ),
    ]
