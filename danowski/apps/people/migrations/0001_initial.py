# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'School'
        db.create_table(u'people_school', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('categorizer', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Location'], null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'people', ['School'])

        # Adding unique constraint on 'School', fields ['name', 'categorizer', 'location']
        db.create_unique(u'people_school', ['name', 'categorizer', 'location_id'])

        # Adding model 'Person'
        db.create_table(u'people_person', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('race', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('racial_self_description', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('uri', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'people', ['Person'])

        # Adding unique constraint on 'Person', fields ['first_name', 'last_name']
        db.create_unique(u'people_person', ['first_name', 'last_name'])

        # Adding M2M table for field schools on 'Person'
        m2m_table_name = db.shorten_name(u'people_person_schools')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('person', models.ForeignKey(orm[u'people.person'], null=False)),
            ('school', models.ForeignKey(orm[u'people.school'], null=False))
        ))
        db.create_unique(m2m_table_name, ['person_id', 'school_id'])

        # Adding M2M table for field dwelling on 'Person'
        m2m_table_name = db.shorten_name(u'people_person_dwelling')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('person', models.ForeignKey(orm[u'people.person'], null=False)),
            ('location', models.ForeignKey(orm[u'geo.location'], null=False))
        ))
        db.create_unique(m2m_table_name, ['person_id', 'location_id'])

        # Adding model 'Name'
        db.create_table(u'people_name', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
        ))
        db.send_create_signal(u'people', ['Name'])

        # Adding model 'PenName'
        db.create_table(u'people_penname', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
        ))
        db.send_create_signal(u'people', ['PenName'])


    def backwards(self, orm):
        # Removing unique constraint on 'Person', fields ['first_name', 'last_name']
        db.delete_unique(u'people_person', ['first_name', 'last_name'])

        # Removing unique constraint on 'School', fields ['name', 'categorizer', 'location']
        db.delete_unique(u'people_school', ['name', 'categorizer', 'location_id'])

        # Deleting model 'School'
        db.delete_table(u'people_school')

        # Deleting model 'Person'
        db.delete_table(u'people_person')

        # Removing M2M table for field schools on 'Person'
        db.delete_table(db.shorten_name(u'people_person_schools'))

        # Removing M2M table for field dwelling on 'Person'
        db.delete_table(db.shorten_name(u'people_person_dwelling'))

        # Deleting model 'Name'
        db.delete_table(u'people_name')

        # Deleting model 'PenName'
        db.delete_table(u'people_penname')


    models = {
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
        },
        u'people.name': {
            'Meta': {'object_name': 'Name'},
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Person']"})
        },
        u'people.penname': {
            'Meta': {'object_name': 'PenName'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Person']"})
        },
        u'people.person': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'unique_together': "(('first_name', 'last_name'),)", 'object_name': 'Person'},
            'dwelling': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['geo.Location']", 'symmetrical': 'False', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'race': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'racial_self_description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'schools': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['people.School']", 'symmetrical': 'False', 'blank': 'True'}),
            'uri': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'people.school': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('name', 'categorizer', 'location'),)", 'object_name': 'School'},
            'categorizer': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.Location']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['people']