from django.test import TestCase

from danowski.apps.geo.models import Location, GeonamesCountry, StateCode
from danowski.apps.journals.models import PlaceName, IssueItem

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
        pn.issueItem = IssueItem.objects.first()
        self.maz.placename_set.add(pn)
        net_attrs = self.maz.network_attributes
        self.assertEqual(pn.name, net_attrs['placenames'])
        self.assertTrue(net_attrs['mentioned'])

        # has network edges - always false for locations
        self.assertFalse(self.maz.has_network_edges)
        self.assertFalse(self.bannam.has_network_edges)