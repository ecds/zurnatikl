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

    @property
    def network_id(self):
        #: node identifier when generating a network
        return 'journal:%s' % self.id

    @property
    def network_attributes(self):
        #: data to be included as node attributes when generating a network
        return {
            'label': unicode(self),
            'title': self.title,
            'uri': self.uri,
            'publisher': self.publisher,
            'issn': self.issn
        }

    @property
    def has_network_edges(self):
        return self.schools.exists()

    @property
    def network_edges(self):
        #: list of tuples for edges in the network
        return [(self.network_id, school.network_id) for school in self.schools.all()]


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
    numbered_pages = models.BooleanField()
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

    @property
    def network_id(self):
        #: node identifier when generating a network
        return 'issue:%s' % self.id

    @property
    def network_attributes(self):
        #: data to be included as node attributes when generating a network
        return {
            'label': unicode(self),
            'volume': self.volume,
            'issue': self.issue,
            'publication_date': unicode(self.publication_date),
            'season': self.season,
            'numbered_pages': self.numbered_pages,
            'price': unicode(self.price) or ''
        }

    @property
    def has_network_edges(self):
        return any([self.journal, self.editors.exists(), self.contributing_editors.exists(),
                    self.publication_address, self.print_address, self.mailing_addresses.exists()])

    @property
    def network_edges(self):
        #: list of tuples for edges in the network
        edges = []
        if self.journal:
            edges.append((self.network_id, self.journal.network_id))
        if self.publication_address:
            edges.append((self.network_id, self.publication_address.network_id, {'label': 'publication address'}))
        if self.print_address:
            edges.append((self.network_id, self.print_address.network_id, {'label': 'print address'}))

        edges.extend([(self.network_id, ed.network_id, {'label': 'editor'})
            for ed in self.editors.all()])
        edges.extend([(self.network_id, c_ed.network_id, {'label': 'contributing editor'})
             for c_ed in self.contributing_editors.all()])
        edges.extend([(self.network_id, loc.network_id, {'label': 'mailing address'})
             for loc in self.mailing_addresses.all()])

        return edges


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
    anonymous = models.BooleanField(help_text='check if labeled as by Anonymous')
    #: no creator listed
    no_creator = models.BooleanField(help_text='check if no author is listed [including Anonymous')
    #: translator, :class:`~danowski.apps.people.models.Person`,
    translator = models.ManyToManyField(Person, related_name='translator_name', blank=True, null=True)
    #: start page
    start_page = models.IntegerField(max_length=6)
    #: end page
    end_page = models.IntegerField(max_length=6)
    #: :class:`Genre`
    genre = models.ManyToManyField('Genre')
    #: includes abbreviated text
    abbreviated_text = models.BooleanField(help_text='check if the text contains abbreviations such as wd, yr, etc')
    #: mentioned people, many-to-many to :class:`~danowski.apps.people.models.Person`
    persons_mentioned= models.ManyToManyField(Person, related_name='persons_mentioned', blank=True, null=True)
    #: addressse, many-to-many to :class:`danowski.apps.geo.models.Location`
    addresses = models.ManyToManyField(Location, blank=True, null=True)
    #: indicates if it is a literary advertisement
    literary_advertisement = models.BooleanField()
    #: notes
    notes = models.TextField(blank=True)

    # generate natural key
    def natural_key(self):
        return (self.title)

    def __unicode__(self):
        return self.title

    @property
    def network_id(self):
        #: node identifier when generating a network
        return 'issueitem:%s' % self.id

    @property
    def network_attributes(self):
        #: data to be included as node attributes when generating a network
        return {
            'label': unicode(self),
            'anonymous': self.anonymous,
            'no_creator': self.no_creator,
            'start_page': self.start_page,
            'end_page': self.end_page,
            'genre': ', '.join([g.name for g in self.genre.all()]),
            'abbreviated_text': self.abbreviated_text,
            'literary_advertisement': self.literary_advertisement
        }

    @property
    def has_network_edges(self):
        return any([self.issue, self.creators.exists(), self.translator.exists(),
                    self.persons_mentioned.exists(), self.addresses.exists()])

    @property
    def network_edges(self):
        #: list of tuples for edges in the network
        edges = []
        if self.issue:
            edges.append((self.network_id, self.issue.network_id))
        edges.extend([(self.network_id, c.network_id, {'label': 'creator'})
            for c in self.creators.all()])
        edges.extend([(self.network_id, trans.network_id, {'label': 'translator'})
             for trans in self.translator.all()])
        edges.extend([(self.network_id, person.network_id, {'label': 'mentioned'})
             for person in self.persons_mentioned.all()])
        edges.extend([(self.network_id, loc.network_id)
             for loc in self.addresses.all()])

        return edges


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
