from django.db import models

# for parsing natural key
class CountryManager(models.Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)

class GeonamesCountry(models.Model):
    '''Minimal country information, based on geonames country info download
http://download.geonames.org/export/dump/countryInfo.txt'''

    objects = CountryManager()
    #: country name
    name = models.CharField(max_length=255)
    #: two-letter ISO country code
    code = models.CharField(max_length=2, unique=True)
    #: ISO-numeric code
    numeric_code = models.IntegerField()
    #: two-letter continent code
    continent = models.CharField(max_length=2)
    #: numeric geonames id
    geonames_id = models.IntegerField()

    class Meta:
        verbose_name_plural = 'geonames countries'

    # generate natural key
    def natural_key(self):
        return (self.code,)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.code)

class ContinentManager(models.Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)

class GeonamesContinent(models.Model):
    '''Continent names and codes from GeoNames, as listed at
http://download.geonames.org/export/dump/'''

    objects = ContinentManager()

    #: continent name
    name = models.CharField(max_length=255)
    #: two-letter continent code
    code = models.CharField(max_length=2, unique=True)
    #: geonames id
    geonames_id = models.IntegerField()

    # generate natural key
    def natural_key(self):
        return (self.code,)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.code)


class StateManager(models.Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)

class StateCode(models.Model):
    'U.S. State abbreviation and FIPS codes, for generating maps'

    objects = StateManager()

    #: state name
    name = models.CharField(max_length=255)
    #: two-letter state abbrevation
    code = models.CharField(max_length=2, unique=True)
    #: numeric FIPS code
    fips = models.IntegerField()

    class Meta:
        verbose_name_plural = 'geonames statecode'

    # generate natural key
    def natural_key(self):
        return (self.code,)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.code)


class LocationManager(models.Manager):
    def get_by_natural_key(self, street_address, city, zipcode):
        return self.get(street_address=street_address, city=city, zipcode=zipcode)


class Location(models.Model):
    """
    Locations or Addresses
    """

    objects = LocationManager()

    #: Street name and number
    street_address = models.CharField(max_length=255, blank=True, help_text='Street name and number')
    #: City name
    city = models.CharField(max_length=255, help_text='City name')
    #: state - :class:`StateCode`
    state = models.ForeignKey(StateCode, blank=True, null=True, help_text='State name')
    #: zipcode
    zipcode = models.CharField(max_length=10, blank=True)
    #: country - :class:`GeonamesCountry`
    country = models.ForeignKey(GeonamesCountry, help_text='Country name')
    ''' Country name'''

    # available reverse relationship names:
    # - people
    # - issues_published_at, issues_printed_at, issues_mailed_to
    # - item_set

    # generate natural key
    def natural_key(self):
        return (self.street_address, self.city, self.zipcode)

    def __unicode__(self):
        # only include fields that are not empty
        fields = [self.street_address, self.city, self.state, self.zipcode, self.country]
        return ' '.join([unicode(f) for f in fields if f])

    @property
    def display_label(self):
        # variant display - drop zipcode, only show state/country names and not codes
        # state names are stored as all caps, so title-case them
        fields = [
            self.street_address,
            self.city,
            self.state.name.title() if self.state else None,
            self.country.name
        ]
        # only include fields that are not empty
        return ', '.join([f for f in fields if f])

    @property
    def short_label(self):
        # even shorter display label variant
        if self.country.code == 'US':
            fields = [self.street_address, self.city, self.state.code]
        else:
            fields = [self.street_address, self.city, self.country.name]
        return ', '.join([f for f in fields if f])

    class Meta:
        unique_together = ('street_address', 'city', 'state', 'zipcode', 'country')
        ordering = ['street_address', 'city', 'state', 'zipcode', 'country']

    @property
    def network_id(self):
        #: node identifier when generating a network
        return 'location:%s' % self.id

    @property
    def network_attributes(self):
        #: data to be included as node attributes when generating a network
        attrs = {
            'label': unicode(self),
            'city': self.city,
            # boolean flag to allow filtering out mentioned places in output
            'mentioned': self.placename_set.exists()
        }
        if self.street_address:
            attrs['street address'] = self.street_address
        if self.zipcode:
            attrs['zipcode'] = self.zipcode
        if self.placename_set.count():
            attrs['placenames'] = '; '.join(set(unicode(pn) for pn in self.placename_set.all()))
        if self.state:
            attrs.update({
                'state': self.state.name,
                'state code': self.state.code,
            })
        if self.country:
            attrs.update({
                'country': self.country.name,
                'country code': self.country.code
            })
        return attrs

    @property
    def has_network_edges(self):
        # no edges originate from location, they are all *to* locations
        return False
