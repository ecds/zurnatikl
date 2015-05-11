from django.test import TestCase

from danowski.apps.geo.models import Location
from danowski.apps.people.models import Person, School

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


class PeopleTestCase(TestCase):
    fixtures = ['test_network.json']

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

        # network edges - no location
        self.assertFalse(berrigan.has_network_edges,
            'person with no location should have no network edges')
        self.assertEqual([], berrigan.network_edges)

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

