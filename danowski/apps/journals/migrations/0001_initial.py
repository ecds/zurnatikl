# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_date_extensions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0001_initial'),
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreatorName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_used', models.CharField(max_length=200, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('volume', models.CharField(max_length=255, blank=True)),
                ('issue', models.CharField(max_length=255, blank=True)),
                ('publication_date', django_date_extensions.fields.ApproximateDateField(help_text=b'YYYY , MM/YYYY, DD/MM/YYYY', max_length=10)),
                ('season', models.CharField(blank=True, max_length=10, choices=[(b'Fall', b'Fall'), (b'Spring', b'Spring'), (b'Summer', b'Summer'), (b'Winter', b'Winter')])),
                ('physical_description', models.CharField(max_length=255, blank=True)),
                ('numbered_pages', models.BooleanField(default=False)),
                ('price', models.DecimalField(null=True, max_digits=7, decimal_places=2, blank=True)),
                ('notes', models.TextField(blank=True)),
                ('contributing_editors', models.ManyToManyField(related_name='contributing_editors', null=True, to='people.Person', blank=True)),
                ('editors', models.ManyToManyField(to='people.Person')),
            ],
            options={
                'ordering': ['journal', 'volume', 'issue'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IssueItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('anonymous', models.BooleanField(default=False, help_text=b'check if labeled as by Anonymous')),
                ('no_creator', models.BooleanField(default=False, help_text=b'check if no author is listed [including Anonymous]')),
                ('start_page', models.IntegerField(max_length=6)),
                ('end_page', models.IntegerField(max_length=6)),
                ('abbreviated_text', models.BooleanField(default=False, help_text=b'check if the text contains abbreviations such as wd, yr, etc')),
                ('literary_advertisement', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
                ('addresses', models.ManyToManyField(to='geo.Location', null=True, blank=True)),
                ('creators', models.ManyToManyField(related_name='creators_name', null=True, through='journals.CreatorName', to='people.Person', blank=True)),
                ('genre', models.ManyToManyField(to='journals.Genre')),
                ('issue', models.ForeignKey(to='journals.Issue')),
                ('persons_mentioned', models.ManyToManyField(related_name='persons_mentioned', null=True, to='people.Person', blank=True)),
                ('translator', models.ManyToManyField(related_name='translator_name', null=True, to='people.Person', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('uri', models.URLField(blank=True)),
                ('publisher', models.CharField(max_length=100, blank=True)),
                ('issn', models.CharField(max_length=50, blank=True)),
                ('notes', models.TextField(blank=True)),
                ('schools', models.ManyToManyField(to='people.School', blank=True)),
            ],
            options={
                'ordering': ['title'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlaceName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('issueItem', models.ForeignKey(to='journals.IssueItem')),
                ('location', models.ForeignKey(blank=True, to='geo.Location', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='issue',
            name='journal',
            field=models.ForeignKey(to='journals.Journal'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='issue',
            name='mailing_addresses',
            field=models.ManyToManyField(help_text=b'addresses where issue was mailed', related_name='mailing_addresses', null=True, to='geo.Location', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='issue',
            name='print_address',
            field=models.ForeignKey(related_name='print_address', blank=True, to='geo.Location', help_text=b'address where issue was printed', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='issue',
            name='publication_address',
            field=models.ForeignKey(related_name='publication_address', blank=True, to='geo.Location', help_text=b'address of publication', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='creatorname',
            name='issue_item',
            field=models.ForeignKey(to='journals.IssueItem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='creatorname',
            name='person',
            field=models.ForeignKey(to='people.Person'),
            preserve_default=True,
        ),
    ]
