# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('journals', '0002_load_genres'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='IssueItem',
            new_name='Item'
        ),
        migrations.RenameField(
            model_name='Item',
            old_name='translator',
            new_name='translators'
        ),
        migrations.RenameField(
            model_name='PlaceName',
            old_name='issueItem',
            new_name='item'
        ),
        migrations.RenameField(
            model_name='CreatorName',
            old_name='issue_item',
            new_name='item'
        ),
        migrations.AlterField(
            model_name='issue',
            name='contributing_editors',
            field=models.ManyToManyField(related_name='issues_contrib_edited', null=True, to='people.Person', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='issue',
            name='editors',
            field=models.ManyToManyField(related_name='issues_edited', to='people.Person'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='issue',
            name='mailing_addresses',
            field=models.ManyToManyField(help_text=b'addresses where issue was mailed', related_name='issues_mailed_to', null=True, to='geo.Location', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='issue',
            name='print_address',
            field=models.ForeignKey(related_name='issues_printed_at', blank=True, to='geo.Location', help_text=b'address where issue was printed', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='issue',
            name='publication_address',
            field=models.ForeignKey(related_name='issues_published_at', blank=True, to='geo.Location', help_text=b'address of publication', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='creators',
            field=models.ManyToManyField(related_name='items_created', null=True, through='journals.CreatorName', to='people.Person', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='persons_mentioned',
            field=models.ManyToManyField(related_name='items_mentioned_in', null=True, to='people.Person', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='translators',
            field=models.ManyToManyField(related_name='items_translated', null=True, to='people.Person', blank=True),
            preserve_default=True,
        ),
    ]
