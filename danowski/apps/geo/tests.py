from django.test import TestCase

from danowski.apps.geo.models import Location, GeonamesCountry, StateCode

class LocationTestCase(TestCase):

    def test_unicode(self):
        mx = GeonamesCountry.objects.filter(name='Mexico').first()
        # location with only a few fields should not include None
        # or extra spaces in unicode output
        maz = Location(city='Mazatlan', country=mx)
        self.assertEqual("Mazatlan Mexico (MX)", unicode(maz),
            'unicode for location without all fields should not include None or extra spaces')

        # location with all values should work too
        us = GeonamesCountry.objects.filter(name='United States').first()
        ca = StateCode.objects.filter(code='CA').first()
        bannam = Location(street_address='14 Bannam Alley',
            city='San Francisco', state=ca, country=us, zipcode='94133')
        print unicode(bannam)
        expected_value = '%(st)s %(city)s %(state)s %(zip)s %(country)s' % \
            {'st': bannam.street_address, 'city': bannam.city,
             'state': ca, 'zip': bannam.zipcode, 'country': us}
        self.assertEqual(expected_value, unicode(bannam),
            'unicode for location with all fields should include them in order')
