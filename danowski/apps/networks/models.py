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
    zipcode = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=2, help_text='Country name', choices=COUNTRY_CHOICES)
    ''' Country name'''

    def __unicode__(self):
        return '%s %s %s %s %s' \
               % (self.street_address, self.city, self.state, self.zipcode, self.country)

    class Meta:
        unique_together = ('street_address', 'city', 'state', 'zipcode', 'country')


class School(models.Model):
    '''School of poetry'''

    CATEGORIZER_CHOICES =(
        ('Donald Allen', 'Donald Allen'),
    )

    name = models.CharField(max_length=255)
    ''' Name of school of poetry'''
    categorizer = models.CharField(max_length=100, blank=True, choices=CATEGORIZER_CHOICES)
    '''Name of categorizer'''
    location = models.ForeignKey(Location, blank=True, null=True)
    ''':class:`Location` of school of poetry'''
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'categorizer', 'location')


class AltName(models.Model):
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    person = models.ForeignKey('Person')

class PenName(models.Model):
    name = models.CharField(max_length=200)
    person = models.ForeignKey('Person')

class Person(models.Model):

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )

    RACE_CHOICES = (
        ('White', 'White'),
        ('Black or African American', 'Black or African American'),
        ('American Indian or Alaska Native', 'American Indian or Alaska Native'),
        ('Asian', 'Asian'),
        ('Native Hawaiian or Other Pacific Islander', 'Native Hawaiian or Other Pacific Islander'),
        ('Hispanic', 'Hispanic'),
        ('Latino', 'Latino'),
    )

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    race = models.CharField(max_length=50, blank=True, choices=RACE_CHOICES)
    racial_self_description = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1, blank=True, choices=GENDER_CHOICES)
    schools = models.ManyToManyField('School', blank=True)
    uri = models.URLField(blank=True)
    dwelling = models.ManyToManyField('Location', blank=True)
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)

    class Meta:
        verbose_name_plural = 'People'
        unique_together = ('first_name', 'last_name')

class Journal(models.Model):
    title = models.CharField(max_length=255)
    uri = models.URLField(blank=True)
    publisher = models.CharField(max_length=100)
    issn = models.CharField(max_length=50, blank=True)
    schools = models.ManyToManyField('School', blank=True)
    notes = models.TextField(blank=True)