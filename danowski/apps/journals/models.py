from django.db import models
from danowski.apps.geo.models import Location
from danowski.apps.people.models import Person, School
from django_date_extensions import fields as ddx

# for parsing natural key
class PlaceNameManager(models.Manager):
    def get_by_natural_key(self, name, location, issueItem):
        return self.get(name=name)

class PlaceName(models.Model):

    objects = PlaceNameManager()

    name = models.CharField(max_length=200)
    location = models.ForeignKey(Location, blank=True, null=True)
    issueItem = models.ForeignKey('IssueItem')

    # generate natural key
    def natural_key(self):
        return (self.name)

    def __unicode__(self):
        return self.name


# for parsing natural key
class JournalManager(models.Manager):
    def get_by_natural_key(self, title):
        return self.get(title=title)

class Journal(models.Model):

    objects = JournalManager()

    title = models.CharField(max_length=255)
    uri = models.URLField(blank=True)
    publisher = models.CharField(max_length=100, blank=True)
    issn = models.CharField(max_length=50, blank=True)
    schools = models.ManyToManyField(School, blank=True)
    notes = models.TextField(blank=True)


    # generate natural key
    def natural_key(self):
        return (self.title,)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']


class IssueManager(models.Manager):
    def get_by_natural_key(self, volume, issue, season, journal):
        j = Journal.objects.get(title=journal)
        return self.get(volume=volume, issue=issue, season=season, journal=j)

class Issue(models.Model):

    objects = IssueManager()

    SEASON_CHOICES = (
        ('Fall', 'Fall'),
        ('Spring', 'Spring'),
        ('Summer', 'Summer'),
        ('Winter', 'Winter'),

    )

    journal = models.ForeignKey('Journal')
    volume = models.CharField(max_length=255, blank=True)
    issue = models.CharField(max_length=255, blank=True)
    publication_date = ddx.ApproximateDateField(help_text='YYYY , MM/YYYY, DD/MM/YYYY')
    season = models.CharField(max_length=10, blank=True, choices=SEASON_CHOICES)
    editors = models.ManyToManyField(Person)
    contributing_editors = models.ManyToManyField(Person, related_name='contributing_editors', blank=True, null=True)
    publication_address = models.ForeignKey(Location, help_text="address of publication", related_name='publication_address', blank=True, null=True)
    print_address = models.ForeignKey(Location, blank=True, help_text="address where issue was printed", related_name='print_address', null=True)
    mailing_addresses  = models.ManyToManyField(Location, blank=True, help_text="addresses where issue was mailed", related_name='mailing_addresses', null=True)
    physical_description = models.CharField(max_length=255, blank=True)
    numbered_pages = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True)


    # generate natural key
    def natural_key(self):
        return (self.volume, self.issue, self.season, self.journal.title)

    def __unicode__(self):
        return '%s vol. %s issue %s' % (self.journal.title, self.volume, self.issue)

    class Meta:
        ordering = ['journal', 'volume', 'issue']

class GenreManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Genre(models.Model):

    objects = GenreManager()

    name = models.CharField(max_length=50)

    # generate natural key
    def natural_key(self):
        return (self.name,)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


class IssueItemManager(models.Manager):
    def get_by_natural_key(self, title):
        return self.get(title=title)

class IssueItem(models.Model):

    objects = IssueItemManager()

    issue = models.ForeignKey('Issue')
    title = models.CharField(max_length=255)
    creators = models.ManyToManyField(Person, through='CreatorName', related_name='creators_name', null=True, blank=True)
    anonymous = models.BooleanField(help_text='check if labeled as by Anonymous',
        default=False)
    no_creator = models.BooleanField(help_text='check if no author is listed [including Anonymous]',
        default=False)
    translator = models.ManyToManyField(Person, related_name='translator_name', blank=True, null=True)
    start_page = models.IntegerField(max_length=6)
    end_page = models.IntegerField(max_length=6)
    genre = models.ManyToManyField('Genre')
    abbreviated_text = models.BooleanField(help_text='check if the text contains abbreviations such as wd, yr, etc',
        default=False)
    persons_mentioned= models.ManyToManyField(Person, related_name='persons_mentioned', blank=True, null=True)
    addresses = models.ManyToManyField(Location, blank=True, null=True)
    literary_advertisement = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    # generate natural key
    def natural_key(self):
        return (self.title)

    def __unicode__(self):
        return self.title


class CreatorNameManager(models.Manager):
    def get_by_natural_key(self, name_used):
        return self.get(name_used=name_used)

class CreatorName(models.Model):

    objects = CreatorNameManager()

    issue_item = models.ForeignKey("IssueItem")
    person = models.ForeignKey(Person)
    name_used = models.CharField(max_length=200, blank=True)

    def natural_key(self):
        return (self.name_used,)

    def __unicode__(self):
        return self.person
