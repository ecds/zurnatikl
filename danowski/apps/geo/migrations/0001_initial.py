# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GeonamesContinent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(unique=True, max_length=2)),
                ('geonames_id', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GeonamesCountry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(unique=True, max_length=2)),
                ('numeric_code', models.IntegerField()),
                ('continent', models.CharField(max_length=2)),
                ('geonames_id', models.IntegerField()),
            ],
            options={
                'verbose_name_plural': 'geonames countries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('street_address', models.CharField(help_text=b'Street name and number', max_length=255, blank=True)),
                ('city', models.CharField(help_text=b'City name', max_length=255)),
                ('zipcode', models.CharField(max_length=10, blank=True)),
                ('country', models.ForeignKey(help_text=b'Country name', to='geo.GeonamesCountry')),
            ],
            options={
                'ordering': ['street_address', 'city', 'state', 'zipcode', 'country'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StateCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(unique=True, max_length=2)),
                ('fips', models.IntegerField()),
            ],
            options={
                'verbose_name_plural': 'geonames statecode',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='location',
            name='state',
            field=models.ForeignKey(blank=True, to='geo.StateCode', help_text=b'State name', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='location',
            unique_together=set([('street_address', 'city', 'state', 'zipcode', 'country')]),
        ),
    ]
