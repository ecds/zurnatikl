from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase

from danowski.apps.geo.models import Location, GeonamesCountry, StateCode
from danowski.apps.journals.models import PlaceName, Issue, Item
from danowski.apps.people.models import Person

class LocationTestCase(TestCase):
    fixtures = ['test_network.json']

    def setUp(self):
        # test location with only a few fields
        self.mx = GeonamesCountry.objects.filter(name='Mexico').first()
        self.maz = Location(city='Mazatlan', country=self.mx)
        self.maz.save()

        # test location with all fields
        self.us = GeonamesCountry.objects.filter(name='United States').first()
        self.ca = StateCode.objects.filter(code='CA').first()
        self.bannam = Location(street_address='14 Bannam Alley',
            city='San Francisco', state=self.ca, country=self.us, zipcode='94133')
        self.bannam.save()

    def test_unicode(self):
        # location with only a few fields should not include None
        # or extra spaces in unicode output
        self.assertEqual("Mazatlan Mexico (MX)", unicode(self.maz),
            'unicode for location without all fields should not include None or extra spaces')

        # location with all values should work too
        expected_value = '%(st)s %(city)s %(state)s %(zip)s %(country)s' % \
            {'st': self.bannam.street_address, 'city': self.bannam.city,
             'state': self.ca, 'zip': self.bannam.zipcode, 'country': self.us}
        self.assertEqual(expected_value, unicode(self.bannam),
            'unicode for location with all fields should include them in order')

    def test_network_properties(self):
        # network id
        for loc in [self.maz, self.bannam]:
            self.assertEqual('location:%d' % loc.id, loc.network_id)

        # network attributes - only present when set
        included = ['label', 'city', 'country', 'country code']
        not_included = ['street address', 'zipcode', 'placenames',
            'state', 'state code']
        net_attrs = self.maz.network_attributes
        for f in included:
            self.assert_(f in net_attrs,
                '%s should be included in network attributes' % f)
        for f in not_included:
            self.assert_(f not in net_attrs,
                '%s should not be included in network attributes' % f)
        self.assertFalse(net_attrs['mentioned'])

        # bannam location should include everything except a placename
        included = ['label', 'city', 'country', 'country code',
           'street address', 'zipcode', 'state', 'state code']
        not_included = ['placenames']
        net_attrs = self.bannam.network_attributes
        for f in included:
            self.assert_(f in net_attrs,
                '%s should be included in network attributes' % f)
        for f in not_included:
            self.assert_(f not in net_attrs,
                '%s should not be included in network attributes' % f)

        # test placename inclusion
        pn = PlaceName(name='somewhere out there')
        pn.item = Item.objects.first()
        self.maz.placename_set.add(pn)
        net_attrs = self.maz.network_attributes
        self.assertEqual(pn.name, net_attrs['placenames'])
        self.assertTrue(net_attrs['mentioned'])

        # has network edges - always false for locations
        self.assertFalse(self.maz.has_network_edges)
        self.assertFalse(self.bannam.has_network_edges)


class LocationAdminViewsTestCase(TestCase):
    fixtures = ['test_network.json']

    def test_change_form(self):
        # login as admin user for testing admin views
        user_info = {'username': 'testsuper', 'password': 'sshd0ntt3ll'}
        self.client.login(**user_info)

        # location with a school (and only a school)
        loc = Location.objects.filter(schools__isnull=False,
            item__isnull=True).first()
        url = reverse('admin:geo_location_change', args=[loc.pk])
        resp = self.client.get(url)
        self.assertTemplateUsed(resp, 'geo/admin/location_change_form.html')
        self.assertContains(resp, 'Schools')
        self.assertContains(resp, loc.schools.first().name)
        self.assertContains(resp, reverse('admin:people_school_change', args=[loc.schools.first().pk]))
        self.assertNotContains(resp, 'People')
        self.assertNotContains(resp, 'Issues')
        self.assertNotContains(resp, 'Items')

        # for convenience, add other associations to this location
        loc.schools.all().delete()
        loc.people.add(Person.objects.first())
        items = Item.objects.all()
        loc.item_set.add(items[0])
        loc.item_set.add(items[1])
        # currently only three issues in the test fixture
        issues = Issue.objects.all()
        # - issues_published_at, issues_printed_at, issues_mailed_to
        loc.issues_published_at.add(issues[0])
        loc.issues_published_at.add(issues[1])
        loc.issues_printed_at.add(issues[0])
        loc.issues_mailed_to.add(issues[0])
        loc.issues_mailed_to.add(issues[2])
        loc.save()

        resp = self.client.get(url)
        self.assertNotContains(resp, 'Schools')
        self.assertContains(resp, 'People')
        for p in loc.people.all():
            self.assertContains(resp, unicode(p))
            self.assertContains(resp, reverse('admin:people_person_change', args=[p.pk]))
        self.assertContains(resp, 'Issues')
        self.assertContains(resp, 'Publication address for')
        for i in loc.issues_published_at.all():
            self.assertContains(resp, unicode(i))
            self.assertContains(resp, reverse('admin:journals_issue_change', args=[i.pk]))
        self.assertContains(resp, 'Print address for')
        for i in loc.issues_printed_at.all():
            self.assertContains(resp, unicode(i))
            self.assertContains(resp, reverse('admin:journals_issue_change', args=[i.pk]))
        self.assertContains(resp, 'Mailing address for')
        for i in loc.issues_mailed_to.all():
            self.assertContains(resp, unicode(i))
            self.assertContains(resp, reverse('admin:journals_issue_change', args=[i.pk]))
        # issues[0] should display 3 times; confirm repeated
        self.assertContains(resp, issues[0], 3)
        self.assertContains(resp, 'Items')
        for i in loc.item_set.all():
            self.assertContains(resp, unicode(i))
            self.assertContains(resp, reverse('admin:journals_item_change', args=[i.pk]))

