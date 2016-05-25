# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('journals', '0006_add_journal_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='issue',
            options={'ordering': ['journal', 'sort_order', 'volume', 'issue']},
        ),
        migrations.AlterModelOptions(
            name='item',
            options={'ordering': ['issue', 'start_page', 'end_page', 'title']},
        ),
        migrations.AlterField(
            model_name='issue',
            name='contributing_editors',
            field=models.ManyToManyField(related_name='issues_contrib_edited', to='people.Person', blank=True),
        ),
        migrations.AlterField(
            model_name='issue',
            name='mailing_addresses',
            field=models.ManyToManyField(help_text=b'addresses where issue was mailed', related_name='issues_mailed_to', to='geo.Location', blank=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='addresses',
            field=models.ManyToManyField(to='geo.Location', blank=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='creators',
            field=models.ManyToManyField(related_name='items_created', through='journals.CreatorName', to='people.Person', blank=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='end_page',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='item',
            name='persons_mentioned',
            field=models.ManyToManyField(related_name='items_mentioned_in', to='people.Person', blank=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='start_page',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='item',
            name='translators',
            field=models.ManyToManyField(related_name='items_translated', to='people.Person', blank=True),
        ),
        migrations.AlterField(
            model_name='journal',
            name='slug',
            field=models.SlugField(help_text=b'Short name for use in URLs. Leave blank to have a slug automatically generated. Change carefully, since editing this field this changes the site URL.', unique=True, blank=True),
        ),
    ]
