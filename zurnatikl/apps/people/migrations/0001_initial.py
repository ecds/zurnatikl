# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Name',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=100, blank=True)),
                ('last_name', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PenName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=100, blank=True)),
                ('last_name', models.CharField(max_length=100)),
                ('race', models.CharField(blank=True, max_length=50, choices=[(b'American Indian or Alaska Native', b'American Indian or Alaska Native'), (b'Asian', b'Asian'), (b'Black or African American', b'Black or African American'), (b'Hispanic', b'Hispanic'), (b'Latino', b'Latino'), (b'Native Hawaiian or Other Pacific Islander', b'Native Hawaiian or Other Pacific Islander'), (b'White', b'White')])),
                ('racial_self_description', models.CharField(max_length=100, blank=True)),
                ('gender', models.CharField(blank=True, max_length=1, choices=[(b'F', b'Female'), (b'M', b'Male')])),
                ('uri', models.URLField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('dwelling', models.ManyToManyField(related_name='dwelling_info', to='geo.Location', blank=True)),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
                'verbose_name_plural': 'People',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('categorizer', models.CharField(blank=True, max_length=100, choices=[(b'Donald Allen', b'Donald Allen')])),
                ('notes', models.TextField(blank=True)),
                ('location', models.ForeignKey(blank=True, to='geo.Location', null=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='school',
            unique_together=set([('name', 'categorizer', 'location')]),
        ),
        migrations.AddField(
            model_name='person',
            name='schools',
            field=models.ManyToManyField(to='people.School', blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='person',
            unique_together=set([('first_name', 'last_name')]),
        ),
        migrations.AddField(
            model_name='penname',
            name='person',
            field=models.ForeignKey(to='people.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='name',
            name='person',
            field=models.ForeignKey(to='people.Person'),
            preserve_default=True,
        ),
    ]
