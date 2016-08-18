# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.test import TestCase

from zurnatikl.apps.geo.models import Location
from zurnatikl.apps.journals.models import Journal
from .models import Person, School
from .views import PeopleCSV


class SchoolTestCase(TestCase):
    fixtures = ['test_network.json']

    def test_network_properties(self):
        # one with a location
        blackmtn = School.objects.filter(name='Black Mountain').first()
        # one without
        beats = School.objects.filter(name='The Beat Generation').first()

        # network id
        for s in [blackmtn, beats]:
            self.assertEqual('school:%d' % s.id, s.network_id)

        # network attributes
        net_attrs = blackmtn.network_attributes
        self.assertEqual(unicode(blackmtn), net_attrs['label'])
        self.assertEqual(blackmtn.categorizer, net_attrs['categorizer'])

        # network edges
        # - no location = no edge
        self.assertFalse(beats.has_network_edges,
            'school with no location should have no network edges')
        self.assertEqual([], beats.network_edges)

    def test_schools_network(self):
        schools = School.objects.all()
        # generate network from all schools in our fixture data
        graph = School.schools_network(schools)

        # each school and every associated person, place, and journal
        # should be included in the network and have an edge
        # connecting school and corresponding person/place/journal

        for s in schools:
            school_node = graph.vs.find(name=s.network_id)
            self.assert_(school_node)
            self.assertEqual('School', school_node['type'])
            self.assertEqual(unicode(s), school_node['label'])

        # people associated with schools should be in the network
        for p in Person.objects.filter(schools__isnull=False):
            node = graph.vs.find(name=p.network_id)
            self.assert_(node)
            self.assertEqual('Person', node['type'])
            self.assertEqual(p.firstname_lastname, node['label'])

            for sch in p.schools.all():
                sch_node = graph.vs.find(name=sch.network_id)
                self.assert_(graph.es.find(_source=sch_node.index,
                                           _target=node.index))

        # journals associated with schools should be in the network
        for j in Journal.objects.filter(schools__isnull=False):
            node = graph.vs.find(name=j.network_id)
            self.assert_(node)
            self.assertEqual('Journal', node['type'])
            self.assertEqual(unicode(j), node['label'])

            for sch in j.schools.all():
                sch_node = graph.vs.find(name=sch.network_id)
                self.assert_(graph.es.find(_source=sch_node.index,
                                           _target=node.index))

        for loc in Location.objects.filter(schools__isnull=False):
            node = graph.vs.find(name=loc.network_id)
            self.assert_(node)
            self.assertEqual('Place', node['type'])
            self.assertEqual(loc.short_label, node['label'])

            for sch in loc.schools.all():
                sch_node = graph.vs.find(name=sch.network_id)
                self.assert_(graph.es.find(_source=sch_node.index,
                                           _target=node.index))


class PeopleTestCase(TestCase):
    fixtures = ['test_network.json']

    def test_slug_generation(self):
        p = Person(first_name='Joe', last_name='Schmoe')
        p.save()
        # autogenerate slug
        self.assertEqual('joe-schmoe', p.slug)
        # clear out, should reset to the same, even though
        # this slug is already in the db
        p.slug = None
        p.save()
        self.assertEqual('joe-schmoe', p.slug)

        # single name
        p = Person(last_name='Madonna')
        p.save()
        self.assertEqual('madonna', p.slug)

    def test_network_properties(self):
        berrigan = Person.objects.get(last_name='Berrigan')

        # network id
        self.assertEqual('person:%d' % berrigan.id, berrigan.network_id)

        # network attributes
        net_attrs = berrigan.network_attributes
        self.assertEqual(unicode(berrigan), net_attrs['label'])
        self.assertEqual(berrigan.first_name, net_attrs['first name'])
        self.assertEqual(berrigan.last_name, net_attrs['last name'])
        self.assertTrue(net_attrs['editor'])
        self.assertFalse(net_attrs['creator'])
        self.assertFalse(net_attrs['translator'])
        self.assertFalse(net_attrs['mentioned'])

        # network edges - no location or school
        zhang = Person.objects.get(last_name='Zhang')
        self.assertFalse(zhang.has_network_edges,
            'person with no location or school should have no network edges')
        self.assertEqual([], zhang.network_edges)

        # construct a fictional person with all fields
        sf = Location.objects.filter(city='San Francisco').first()
        fifthschool = School.objects.get(name="5th group")
        person = Person(first_name='John', last_name='Smith', race='Latino',
            gender='M')
        person.save()
        # add connections to a school and a location
        person.schools.add(fifthschool)
        person.dwellings.add(sf)
        net_attrs = person.network_attributes
        included = ['label', 'first name', 'last name', 'race', 'gender']
        for f in included:
            self.assert_(f in net_attrs)
        # all editor/creator/etc flags should be false for this person
        for flag in ['editor', 'creator', 'translator', 'mentioned']:
            self.assertFalse(net_attrs[flag])
        # network edges
        self.assertTrue(person.has_network_edges)
        edges = person.network_edges
        self.assertEqual(2, len(edges),
            'person with one school and one dwelling should have 2 network edges')
        edge_targets = [t for s, t in edges]
        self.assert_(sf.network_id in edge_targets)
        self.assert_(fifthschool.network_id in edge_targets)

    def test_journal_contributor(self):
        contributors = Person.objects.journal_contributors()

        editors = Person.objects.filter(issues_edited__isnull=False)
        for ed in editors:
            self.assert_(ed in contributors,
                'editors should be included in journal contributors')

        authors = Person.objects.filter(items_created__isnull=False)
        for auth in authors:
            self.assert_(auth in contributors,
                'authors should be included in journal contributors')

        mentions = Person.objects.filter(
            Q(items_mentioned_in__isnull=False) &
            Q(issues_edited__isnull=True) &
            Q(items_created__isnull=True))
        for mensch in mentions:
            self.assert_(mensch not in contributors,
                'mentioned non-author/editor people should not contributors')

    def test_journal_contributors_with_counts(self):
        contributors = Person.objects.journal_contributors_with_counts()

        # same tests as above, did we include and exclude the right
        # people?
        editors = Person.objects.filter(issues_edited__isnull=False)
        for ed in editors:
            self.assert_(ed in contributors,
                'editors should be included in journal contributors')

        authors = Person.objects.filter(items_created__isnull=False)
        for auth in authors:
            self.assert_(auth in contributors,
                'authors should be included in journal contributors')

        mentions = Person.objects.filter(
            Q(items_mentioned_in__isnull=False) &
            Q(issues_edited__isnull=True) &
            Q(items_created__isnull=True))
        for mensch in mentions:
            self.assert_(mensch not in contributors,
                'mentioned non-author/editor people should not contributors')

        # test counts
        for contrib in contributors:
            self.assertEqual(contrib.num_created,
                             contrib.items_created.all().count())
            self.assertEqual(contrib.num_edited,
                             contrib.issues_edited.all().count())
            self.assertEqual(contrib.num_translated,
                             contrib.items_translated.all().count())


class PeopleViewsTestCase(TestCase):
    fixtures = ['test_network.json']

    def test_list_people(self):
        response = self.client.get(reverse('people:list'))
        editors = Person.objects.filter(
            Q(issues_edited__isnull=False) |
            Q(issues_contrib_edited__isnull=False))
        for ed in editors:
            self.assertContains(response, unicode(ed),
                msg_prefix='editors should be listed on person browse')

        authors = Person.objects.filter(items_created__isnull=False)
        for auth in authors:
            self.assertContains(response, unicode(auth),
                msg_prefix='authors should be listed on person browse')

        mentions = Person.objects.filter(
            Q(items_mentioned_in__isnull=False) &
            Q(issues_edited__isnull=True) &
            Q(issues_contrib_edited__isnull=True) &
            Q(items_created__isnull=True))
        for m in mentions:
            self.assertNotContains(response, unicode(m),
                msg_prefix='mentioned people should not be listed on person browse')

    def test_person_detail(self):
        # berrigan - edited one issue in test data, no items created
        berrigan = Person.objects.get(last_name='Berrigan')
        response = self.client.get(reverse('people:person',
            kwargs={'slug': berrigan.slug}))
        self.assertContains(response, berrigan.firstname_lastname,
            msg_prefix='should include Person\'s name as first name + last name')
        self.assertContains(response, 'Editor',
            msg_prefix='editor of issues should include "Editor" heading')
        ed_issue = berrigan.issues_edited.all().first()
        self.assertContains(response, unicode(ed_issue.journal),
            msg_prefix='should include journal name for edited issue')
        self.assertContains(response,
            reverse('journals:journal', kwargs={'slug': ed_issue.journal.slug}),
            msg_prefix='should link to journal for edited issue')
        self.assertContains(response, ed_issue.label,
            msg_prefix='should include label of edited issue')
        self.assertContains(response,
            reverse('journals:issue',
                kwargs={'journal_slug': ed_issue.journal.slug, 'id': ed_issue.id}),
            msg_prefix='should link to edited issue')
        self.assertNotContains(response, 'Contributing Editor',
            msg_prefix='"Contributing Editor" heading should not be displayed if no issues contrib. edited')
        self.assertNotContains(response, 'Author',
            msg_prefix='"Author" heading should not be displayed if no items authored')

        # macarthur - authored one item in test data, no issues edited
        macarthur = Person.objects.get(last_name='MacArthur')
        response = self.client.get(reverse('people:person',
            kwargs={'slug': macarthur.slug}))
        self.assertContains(response, macarthur.firstname_lastname,
            msg_prefix='should include Person\'s name as first name + last name')
        self.assertNotContains(response, '<h2>Editor</h2>', html=True,
            msg_prefix='"Editor" heading should not be displayed if no issues edited')
        self.assertNotContains(response, 'Contributing Editor',
            msg_prefix='"Contributing Editor" heading should not be displayed if no issues contrib. edited')
        self.assertContains(response, 'Author',
            msg_prefix='"Author" heading should be displayed for items authored')
        item = macarthur.items_created.all().first()
        # item display information
        self.assertContains(response, unicode(item),
            msg_prefix='should include label for authored item')
        self.assertContains(response, item.issue.label,
            msg_prefix='should include label for issue of authored item')
        self.assertContains(response,
            reverse('journals:issue',
                kwargs={'journal_slug': item.issue.journal.slug, 'id': item.issue.id}),
            msg_prefix='should link to issue for authored item')
        self.assertContains(response, unicode(item.issue.journal),
            msg_prefix='should include journal name for authored item')
        self.assertContains(response,
            reverse('journals:journal', kwargs={'slug': item.issue.journal.slug}),
            msg_prefix='should link to journal for authored item')

    def test_egograph(self):
        # main egograph page just loads json & sigma js
        # berrigan - edited one issue in test data, no items created
        berrigan = Person.objects.get(last_name='Berrigan')
        response = self.client.get(reverse('people:egograph',
            kwargs={'slug': berrigan.slug}))
        self.assertContains(response, berrigan.firstname_lastname,
            msg_prefix='egograph page should diplay person\'s name')
        self.assertContains(response,
            reverse('people:person', kwargs={'slug': berrigan.slug}),
            msg_prefix='egograph should link to main person page')
        self.assertContains(response,
            reverse('people:egograph-json', kwargs={'slug': berrigan.slug}),
            msg_prefix='egograph page should load json for egograph')

    def test_egograph_json(self):
        berrigan = Person.objects.get(last_name='Berrigan')
        response = self.client.get(reverse('people:egograph-json',
            kwargs={'slug': berrigan.slug}))
        # basic sanity checking that this is json & looks as expected
        self.assertEqual(response['content-type'], 'application/json')
        self.assert_('edges' in response.content)
        self.assert_('nodes' in response.content)

    def test_egograph_export(self):
        berrigan = Person.objects.get(last_name='Berrigan')
        # basic testing that the export formats are correct
        # and include the requested person
        # testing the generated network should happen elsewhere

        # graphml
        response = self.client.get(reverse('people:egograph-export',
            kwargs={'slug': berrigan.slug, 'fmt': 'graphml'}))
        self.assertEqual(response['content-type'], 'application/graphml+xml')
        self.assertContains(response, '<graphml')
        self.assertContains(response, berrigan.network_id)
        self.assertContains(response, berrigan.firstname_lastname)

        # gml format
        response = self.client.get(reverse('people:egograph-export',
            kwargs={'slug': berrigan.slug, 'fmt': 'gml'}))
        self.assertEqual(response['content-type'], 'text/plain')
        self.assertContains(response, 'Creator "igraph version')
        self.assertContains(response, berrigan.network_id)
        self.assertContains(response, berrigan.firstname_lastname)

    def test_csv_export(self):
        response = self.client.get(reverse('people:csv'))
        self.assertEqual(response['content-type'],
                         'text/csv; charset=utf-8')

        response_content = u''.join([
            chunk.decode('utf-8') for chunk in response.streaming_content])

        self.assert_(','.join(PeopleCSV.header_row) in response_content)

        def person_fields(p):
            return ','.join([
                ', '.join(p.race or []), p.racial_self_description, p.gender,
                ', '.join(sch.name for sch in p.schools.all()),
                p.uri,
                '; '.join([unicode(loc) for loc in p.dwellings.all()])
                # p.notes.replace('\n', ' ').replace('\r', ' ')
            ])

        editors = Person.objects.filter(
            Q(issues_edited__isnull=False) |
            Q(issues_contrib_edited__isnull=False))
        for ed in editors:
            self.assert_(
                u'%s,%s' % (ed.last_name, ed.first_name) in response_content,
                'editors should be included in person CSV export')

            self.assert_(person_fields(ed) in response_content)
            self.assert_(ed.get_absolute_url() in response_content)

        authors = Person.objects.filter(items_created__isnull=False)
        for auth in authors:
            self.assert_(
                u"%s,%s" % (auth.last_name, auth.first_name) in response_content,
                'authors should be included in person CSV export')
            self.assert_(person_fields(auth) in response_content)
            self.assert_(auth.get_absolute_url() in response_content)

        mentions = Person.objects.filter(
            Q(items_mentioned_in__isnull=False) &
            Q(issues_edited__isnull=True) &
            Q(issues_contrib_edited__isnull=True) &
            Q(items_created__isnull=True))
        for mensch in mentions:
            self.assert_(
                u'%s,%s' % (mensch.last_name, mensch.first_name) not in response_content,
                'mentioned people should not be included in CSV export')

