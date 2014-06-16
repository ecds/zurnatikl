from django.db import models

class GeonamesCountry(models.Model):
    '''Minimal country information, based on geonames country info download
http://download.geonames.org/export/dump/countryInfo.txt'''
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

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.code)

class GeonamesContinent(models.Model):
    '''Continent names and codes from GeoNames, as listed at
http://download.geonames.org/export/dump/'''
    #: continent name
    name = models.CharField(max_length=255)
    #: two-letter continent code
    code = models.CharField(max_length=2, unique=True)
    #: geonames id
    geonames_id = models.IntegerField()

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.code)

class StateCode(models.Model):
    'U.S. State abbreviation and FIPS codes, for generating maps'
    #: state name
    name = models.CharField(max_length=255)
    #: two-letter state abbrevation
    code = models.CharField(max_length=2, unique=True)
    #: numeric FIPS code
    fips = models.IntegerField()

    class Meta:
        verbose_name_plural = 'geonames statecode'

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.code)
