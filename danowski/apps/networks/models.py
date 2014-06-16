from django.db import models
from danowski.apps.geo.models import GeonamesCountry, StateCode
class Location(models.Model):
    """
    Locations or Addresses within the network
    """

    COUNTRY_CHOICES = tuple((c.code, '%s (%s)' % (c.name, c.code)) for c in GeonamesCountry.objects.all())
    STATE_CHOICES = tuple((s.code, '%s (%s)' % (s.name, s.code),) for s in StateCode.objects.all())

    street_address = models.CharField(max_length=255, blank=True, help_text='Street name and number')
    '''Street name and number'''
    city = models.CharField(max_length=255, help_text='City name')
    '''City name'''
    state = models.CharField(max_length=2, blank=True, help_text='State name', choices=STATE_CHOICES)
    '''State name'''
    zipcode = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=2, help_text='Country name', choices=COUNTRY_CHOICES)
    ''' Country name'''

    def __unicode__(self):
        return '%s %s %s %s %s' \
               % (self.street_address, self.city, self.state, self.zipcode, self.country)
