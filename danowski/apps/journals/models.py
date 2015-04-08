from django.db import models
from danowski.apps.geo.models import Location
from danowski.apps.people.models import Person, School
from django_date_extensions import fields as ddx

# for parsing natural key
class PlaceNameManager(models.Manager):
    def get_by_natural_key(self, name, location, issueItem):
        return self.get(name=name)

class PlaceName(models.Model):
    '''Place name maps a specific :class:`~danowski.apps.geo.models.Location`
    to a place as mentioned in an :class:`IssueItem`.'''

    objects = PlaceNameManager()

    #: name
    name = models.CharField(max_length=200)
    #: :class:`danowski.apps.geo.models.Location`
    location = models.ForeignKey(Location, blank=True, null=True)
    #: :class:`IssueItem`
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
    'A Journal or Magazine'

    objects = JournalManager()

    #: title
    title = models.CharField(max_length=255)
    #: uri
    uri = models.URLField(blank=True)
    #: publisher
    publisher = models.CharField(max_length=100, blank=True)
    #: issn
    issn = models.CharField(max_length=50, blank=True)
    #: associated schools;
    #: many-to-many to :class:`danowski.apps.people.models.School`
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
    'Single issue in a :class:`Journal`'

    objects = IssueManager()

    SEASON_CHOICES = (
        ('Fall', 'Fall'),
        ('Spring', 'Spring'),
        ('Summer', 'Summer'),
        ('Winter', 'Winter'),

    )

    #: :class:`Journal`
    journal = models.ForeignKey('Journal')
    #: volume number
    volume = models.CharField(max_length=255, blank=True)
    #: issue number
    issue = models.CharField(max_length=255, blank=True)
    #: publication date
    publication_date = ddx.ApproximateDateField(help_text='YYYY , MM/YYYY, DD/MM/YYYY')
    #: season of publication
    season = models.CharField(max_length=10, blank=True, choices=SEASON_CHOICES)
    #: editors, many-to-many to :class:`~danowski.apps.people.models.Person`
    editors = models.ManyToManyField(Person)
    #: contributing editors, many-to-many to :class:`~danowski.apps.people.models.Person`
    contributing_editors = models.ManyToManyField(Person, related_name='contributing_editors', blank=True, null=True)
    #: publication address :class:`~danowski.apps.geo.models.Location'
    publication_address = models.ForeignKey(Location, help_text="address of publication", related_name='publication_address', blank=True, null=True)
    #: print address :class:`~danowski.apps.geo.models.Location'
    print_address = models.ForeignKey(Location, blank=True, help_text="address where issue was printed", related_name='print_address', null=True)
    #: mailing addresses, many-to-many relation to :class:`~danowski.apps.geo.models.Location'
    mailing_addresses  = models.ManyToManyField(Location, blank=True, help_text="addresses where issue was mailed", related_name='mailing_addresses', null=True)
    #: physical description
    physical_description = models.CharField(max_length=255, blank=True)
    #: boolean indicating if pages are numbered
    numbered_pages = models.BooleanField(default=False)
    #: price
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    #: text notes
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
    'Genre'

    objects = GenreManager()

    #: name
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
    'Item in a :class:`Issue`'

    objects = IssueItemManager()

    #: :class:`Issue` the item is included in
    issue = models.ForeignKey('Issue')
    #: title
    title = models.CharField(max_length=255)
    #: creators, many-to-many to :class:`~danowski.apps.people.models.Person`,
    #: related via :class:`~danowski.apps.people.models.CreatorName`,
    creators = models.ManyToManyField(Person, through='CreatorName', related_name='creators_name', null=True, blank=True)
    #: anonymous
    anonymous = models.BooleanField(help_text='check if labeled as by Anonymous',
        default=False)
    #: no creator listed
    no_creator = models.BooleanField(help_text='check if no author is listed [including Anonymous]',
        default=False)
    #: translator, :class:`~danowski.apps.people.models.Person`,
    translator = models.ManyToManyField(Person, related_name='translator_name', blank=True, null=True)
    #: start page
    start_page = models.IntegerField(max_length=6)
    #: end page
    end_page = models.IntegerField(max_length=6)
    #: :class:`Genre`
    genre = models.ManyToManyField('Genre')
    #: includes abbreviated text
    abbreviated_text = models.BooleanField(help_text='check if the text contains abbreviations such as wd, yr, etc',
        default=False)
    #: mentioned people, many-to-many to :class:`~danowski.apps.people.models.Person`
    persons_mentioned= models.ManyToManyField(Person, related_name='persons_mentioned', blank=True, null=True)
    #: addressse, many-to-many to :class:`danowski.apps.geo.models.Location`
    addresses = models.ManyToManyField(Location, blank=True, null=True)
    #: indicates if it is a literary advertisement
    literary_advertisement = models.BooleanField(default=False)
    #: notes

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
        return unicode(self.person)
