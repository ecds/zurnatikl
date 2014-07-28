from django.db import models
from danowski.apps.geo.models import Location


#Schools
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
        ordering = ['name']


# Person and person parts
class Person(models.Model):

    GENDER_CHOICES = (
        ('F', 'Female'),
        ('M', 'Male')
    )

    RACE_CHOICES = (
        ('American Indian or Alaska Native', 'American Indian or Alaska Native'),
        ('Asian', 'Asian'),
        ('Black or African American', 'Black or African American'),
        ('Hispanic', 'Hispanic'),
        ('Latino', 'Latino'),
        ('Native Hawaiian or Other Pacific Islander', 'Native Hawaiian or Other Pacific Islander'),
        ('White', 'White'),
    )

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    race = models.CharField(max_length=50, blank=True, choices=RACE_CHOICES)
    racial_self_description = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1, blank=True, choices=GENDER_CHOICES)
    schools = models.ManyToManyField('School', blank=True)
    uri = models.URLField(blank=True)
    dwelling = models.ManyToManyField(Location, blank=True)
    notes = models.TextField(blank=True)

    def __unicode__(self):
        if not self.first_name:
            return self.last_name
        else:
            return '%s, %s' % (self.last_name, self.first_name)

    class Meta:
        verbose_name_plural = 'People'
        unique_together = ('first_name', 'last_name')
        ordering = ['last_name', 'first_name']


class Name(models.Model):
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    person = models.ForeignKey('Person')

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)



class PenName(models.Model):
    name = models.CharField(max_length=200)
    person = models.ForeignKey('Person')

    def __unicode__(self):
        return self.name