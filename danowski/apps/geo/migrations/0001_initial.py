# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GeonamesCountry'
        db.create_table(u'geo_geonamescountry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=2)),
            ('numeric_code', self.gf('django.db.models.fields.IntegerField')()),
            ('continent', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('geonames_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'geo', ['GeonamesCountry'])

        # Adding model 'GeonamesContinent'
        db.create_table(u'geo_geonamescontinent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=2)),
            ('geonames_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'geo', ['GeonamesContinent'])

        # Adding model 'StateCode'
        db.create_table(u'geo_statecode', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=2)),
            ('fips', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'geo', ['StateCode'])

        # Adding model 'Location'
        db.create_table(u'geo_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('street_address', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.StateCode'], null=True, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.GeonamesCountry'])),
        ))
        db.send_create_signal(u'geo', ['Location'])

        # Adding unique constraint on 'Location', fields ['street_address', 'city', 'state', 'zipcode', 'country']
        db.create_unique(u'geo_location', ['street_address', 'city', 'state_id', 'zipcode', 'country_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Location', fields ['street_address', 'city', 'state', 'zipcode', 'country']
        db.delete_unique(u'geo_location', ['street_address', 'city', 'state_id', 'zipcode', 'country_id'])

        # Deleting model 'GeonamesCountry'
        db.delete_table(u'geo_geonamescountry')

        # Deleting model 'GeonamesContinent'
        db.delete_table(u'geo_geonamescontinent')

        # Deleting model 'StateCode'
        db.delete_table(u'geo_statecode')

        # Deleting model 'Location'
        db.delete_table(u'geo_location')


    models = {
        u'geo.geonamescontinent': {
            'Meta': {'object_name': 'GeonamesContinent'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'geonames_id': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'geo.geonamescountry': {
            'Meta': {'object_name': 'GeonamesCountry'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'continent': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'geonames_id': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'numeric_code': ('django.db.models.fields.IntegerField', [], {})
        },
        u'geo.location': {
            'Meta': {'ordering': "['street_address', 'city', 'state', 'zipcode', 'country']", 'unique_together': "(('street_address', 'city', 'state', 'zipcode', 'country'),)", 'object_name': 'Location'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.GeonamesCountry']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.StateCode']", 'null': 'True', 'blank': 'True'}),
            'street_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        u'geo.statecode': {
            'Meta': {'object_name': 'StateCode'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'fips': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['geo']