# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PlaceName'
        db.create_table(u'journals_placename', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Location'], null=True, blank=True)),
            ('issueItem', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['journals.IssueItem'])),
        ))
        db.send_create_signal(u'journals', ['PlaceName'])

        # Adding model 'Journal'
        db.create_table(u'journals_journal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('uri', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('publisher', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('issn', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'journals', ['Journal'])

        # Adding M2M table for field schools on 'Journal'
        m2m_table_name = db.shorten_name(u'journals_journal_schools')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('journal', models.ForeignKey(orm[u'journals.journal'], null=False)),
            ('school', models.ForeignKey(orm[u'people.school'], null=False))
        ))
        db.create_unique(m2m_table_name, ['journal_id', 'school_id'])

        # Adding model 'Issue'
        db.create_table(u'journals_issue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('journal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['journals.Journal'])),
            ('volume', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('issue', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('publication_date', self.gf('django_date_extensions.fields.ApproximateDateField')(max_length=10)),
            ('season', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('publication_address', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='publication_address', null=True, to=orm['geo.Location'])),
            ('print_address', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='print_address', null=True, to=orm['geo.Location'])),
            ('physical_description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('numbered_pages', self.gf('django.db.models.fields.BooleanField')()),
            ('price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=7, decimal_places=2, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'journals', ['Issue'])

        # Adding M2M table for field editors on 'Issue'
        m2m_table_name = db.shorten_name(u'journals_issue_editors')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('issue', models.ForeignKey(orm[u'journals.issue'], null=False)),
            ('person', models.ForeignKey(orm[u'people.person'], null=False))
        ))
        db.create_unique(m2m_table_name, ['issue_id', 'person_id'])

        # Adding M2M table for field contributing_editors on 'Issue'
        m2m_table_name = db.shorten_name(u'journals_issue_contributing_editors')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('issue', models.ForeignKey(orm[u'journals.issue'], null=False)),
            ('person', models.ForeignKey(orm[u'people.person'], null=False))
        ))
        db.create_unique(m2m_table_name, ['issue_id', 'person_id'])

        # Adding M2M table for field mailing_addresses on 'Issue'
        m2m_table_name = db.shorten_name(u'journals_issue_mailing_addresses')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('issue', models.ForeignKey(orm[u'journals.issue'], null=False)),
            ('location', models.ForeignKey(orm[u'geo.location'], null=False))
        ))
        db.create_unique(m2m_table_name, ['issue_id', 'location_id'])

        # Adding model 'Genre'
        db.create_table(u'journals_genre', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'journals', ['Genre'])

        # Adding model 'IssueItem'
        db.create_table(u'journals_issueitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['journals.Issue'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('anonymous', self.gf('django.db.models.fields.BooleanField')()),
            ('no_creator', self.gf('django.db.models.fields.BooleanField')()),
            ('start_page', self.gf('django.db.models.fields.IntegerField')(max_length=6)),
            ('end_page', self.gf('django.db.models.fields.IntegerField')(max_length=6)),
            ('abbreviated_text', self.gf('django.db.models.fields.BooleanField')()),
            ('literary_advertisement', self.gf('django.db.models.fields.BooleanField')()),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'journals', ['IssueItem'])

        # Adding M2M table for field translator on 'IssueItem'
        m2m_table_name = db.shorten_name(u'journals_issueitem_translator')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('issueitem', models.ForeignKey(orm[u'journals.issueitem'], null=False)),
            ('person', models.ForeignKey(orm[u'people.person'], null=False))
        ))
        db.create_unique(m2m_table_name, ['issueitem_id', 'person_id'])

        # Adding M2M table for field genre on 'IssueItem'
        m2m_table_name = db.shorten_name(u'journals_issueitem_genre')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('issueitem', models.ForeignKey(orm[u'journals.issueitem'], null=False)),
            ('genre', models.ForeignKey(orm[u'journals.genre'], null=False))
        ))
        db.create_unique(m2m_table_name, ['issueitem_id', 'genre_id'])

        # Adding M2M table for field persons_mentioned on 'IssueItem'
        m2m_table_name = db.shorten_name(u'journals_issueitem_persons_mentioned')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('issueitem', models.ForeignKey(orm[u'journals.issueitem'], null=False)),
            ('person', models.ForeignKey(orm[u'people.person'], null=False))
        ))
        db.create_unique(m2m_table_name, ['issueitem_id', 'person_id'])

        # Adding M2M table for field addresses on 'IssueItem'
        m2m_table_name = db.shorten_name(u'journals_issueitem_addresses')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('issueitem', models.ForeignKey(orm[u'journals.issueitem'], null=False)),
            ('location', models.ForeignKey(orm[u'geo.location'], null=False))
        ))
        db.create_unique(m2m_table_name, ['issueitem_id', 'location_id'])

        # Adding model 'CreatorName'
        db.create_table(u'journals_creatorname', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('issue_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['journals.IssueItem'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
            ('name_used', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal(u'journals', ['CreatorName'])


    def backwards(self, orm):
        # Deleting model 'PlaceName'
        db.delete_table(u'journals_placename')

        # Deleting model 'Journal'
        db.delete_table(u'journals_journal')

        # Removing M2M table for field schools on 'Journal'
        db.delete_table(db.shorten_name(u'journals_journal_schools'))

        # Deleting model 'Issue'
        db.delete_table(u'journals_issue')

        # Removing M2M table for field editors on 'Issue'
        db.delete_table(db.shorten_name(u'journals_issue_editors'))

        # Removing M2M table for field contributing_editors on 'Issue'
        db.delete_table(db.shorten_name(u'journals_issue_contributing_editors'))

        # Removing M2M table for field mailing_addresses on 'Issue'
        db.delete_table(db.shorten_name(u'journals_issue_mailing_addresses'))

        # Deleting model 'Genre'
        db.delete_table(u'journals_genre')

        # Deleting model 'IssueItem'
        db.delete_table(u'journals_issueitem')

        # Removing M2M table for field translator on 'IssueItem'
        db.delete_table(db.shorten_name(u'journals_issueitem_translator'))

        # Removing M2M table for field genre on 'IssueItem'
        db.delete_table(db.shorten_name(u'journals_issueitem_genre'))

        # Removing M2M table for field persons_mentioned on 'IssueItem'
        db.delete_table(db.shorten_name(u'journals_issueitem_persons_mentioned'))

        # Removing M2M table for field addresses on 'IssueItem'
        db.delete_table(db.shorten_name(u'journals_issueitem_addresses'))

        # Deleting model 'CreatorName'
        db.delete_table(u'journals_creatorname')


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
        u'journals.creatorname': {
            'Meta': {'object_name': 'CreatorName'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue_item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['journals.IssueItem']"}),
            'name_used': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Person']"})
        },
        u'journals.genre': {
            'Meta': {'ordering': "['name']", 'object_name': 'Genre'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'journals.issue': {
            'Meta': {'ordering': "['journal', 'volume', 'issue']", 'object_name': 'Issue'},
            'contributing_editors': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'contributing_editors'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['people.Person']"}),
            'editors': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['people.Person']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'journal': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['journals.Journal']"}),
            'mailing_addresses': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'mailing_addresses'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['geo.Location']"}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'numbered_pages': ('django.db.models.fields.BooleanField', [], {}),
            'physical_description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'print_address': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'print_address'", 'null': 'True', 'to': u"orm['geo.Location']"}),
            'publication_address': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'publication_address'", 'null': 'True', 'to': u"orm['geo.Location']"}),
            'publication_date': ('django_date_extensions.fields.ApproximateDateField', [], {'max_length': '10'}),
            'season': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'volume': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'journals.issueitem': {
            'Meta': {'object_name': 'IssueItem'},
            'abbreviated_text': ('django.db.models.fields.BooleanField', [], {}),
            'addresses': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['geo.Location']", 'null': 'True', 'blank': 'True'}),
            'anonymous': ('django.db.models.fields.BooleanField', [], {}),
            'creators': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'creators_name'", 'to': u"orm['people.Person']", 'through': u"orm['journals.CreatorName']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'end_page': ('django.db.models.fields.IntegerField', [], {'max_length': '6'}),
            'genre': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['journals.Genre']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['journals.Issue']"}),
            'literary_advertisement': ('django.db.models.fields.BooleanField', [], {}),
            'no_creator': ('django.db.models.fields.BooleanField', [], {}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'persons_mentioned': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'persons_mentioned'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['people.Person']"}),
            'start_page': ('django.db.models.fields.IntegerField', [], {'max_length': '6'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'translator': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'translator_name'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['people.Person']"})
        },
        u'journals.journal': {
            'Meta': {'ordering': "['title']", 'object_name': 'Journal'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'publisher': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'schools': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['people.School']", 'symmetrical': 'False', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'uri': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'journals.placename': {
            'Meta': {'object_name': 'PlaceName'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issueItem': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['journals.IssueItem']"}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.Location']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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

    complete_apps = ['journals']