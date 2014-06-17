from django.db import models
from danowski.apps.geo.models import GeonamesCountry, StateCode
class Location(models.Model):
    """
    Locations or Addresses
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

    class Meta:
        unique_together = ('street_address', 'city', 'state', 'zipcode', 'country')


class School(models.Model):
    '''School of Writing'''

    CATEGORIZER_CHOICES =(
        ('Donald Allen', 'Donald Allen'),
    )

    name = models.CharField(max_length=255)
    ''' Name of school'''
    categorizer = models.CharField(max_length=100, blank=True, choices=CATEGORIZER_CHOICES)
    '''Name of categorizer'''
    location = models.ForeignKey(Location, blank=True, null=True)
    '''Location / Address of school'''
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'categorizer', 'location')
