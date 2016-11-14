from collections import OrderedDict
from django.db import models
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.utils.safestring import mark_safe
import itertools
import logging
import time

from igraph import Graph
from django_date_extensions import fields as ddx
from stdimage.models import StdImageField

from zurnatikl.apps.geo.models import Location
from zurnatikl.apps.people.models import Person, School


logger = logging.getLogger(__name__)


# for parsing natural key
class PlaceNameManager(models.Manager):
    def get_by_natural_key(self, name, location, item):
        return self.get(name=name)

class PlaceName(models.Model):
    '''Place name maps a specific :class:`~zurnatikl.apps.geo.models.Location`
    to a place as mentioned in an :class:`Item`.'''

    objects = PlaceNameManager()

    #: name
    name = models.CharField(max_length=200)
    #: :class:`zurnatikl.apps.geo.models.Location`
    location = models.ForeignKey(Location, blank=True, null=True)
    #: :class:`Item`
    item = models.ForeignKey('Item')

    # generate natural key
    def natural_key(self):
        return (self.name)

    def __unicode__(self):
        return self.name

class JournalQuerySet(models.QuerySet):

    def by_editor(self, person):
        '''Find all journals that a person edited issues for.'''
        return self.filter(issue__editors=person).distinct()

    def by_author(self, person):
        '''Find all journals that a person contributed to as an author.'''
        return self.filter(issue__item__creators=person).distinct()

    def by_editor_or_author(self, person):
        '''Find all journals that a person edited issues for or contributed
        content to as an author.'''
        return self.filter(
            models.Q(issue__editors=person) |
            models.Q(issue__contributing_editors=person) |
            models.Q(issue__item__creators=person)
            ).distinct()

# for parsing natural key
class JournalManager(models.Manager):
    def get_queryset(self):
        return JournalQuerySet(self.model, using=self._db)

    def get_by_natural_key(self, title):
        return self.get(title=title)

    def by_editor_or_author(self, person):
        return self.get_queryset().by_editor_or_author(person)

    def by_editor(self, person):
        return self.get_queryset().by_editor(person)

    def by_author(self, person):
        return self.get_queryset().by_author(person)


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
    #: many-to-many to :class:`zurnatikl.apps.people.models.School`
    schools = models.ManyToManyField(School, blank=True)
    #: any additional notes
    notes = models.TextField(blank=True)
    #: slug for use in urls
    slug = models.SlugField(unique=True, blank=True,
        help_text='Short name for use in URLs. ' +
        'Leave blank to have a slug automatically generated. ' +
        'Change carefully, since editing this field this changes the site URL.')

    image = StdImageField(blank=True,
        variations={
            # sizes needed for site design use
            'thumbnail': {'width': 150, 'height': 50, 'crop': True},
            # FIXME: this size doesn't seem to be right
            'large': {'width': 425, 'height': 150, 'crop': True},
    })

    # generate natural key
    def natural_key(self):
        return (self.title,)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        # generate a slug if we don't have one set
        if self.slug is None or len(self.slug) == 0:
            max_length = Journal._meta.get_field('slug').max_length
            self.slug = orig = slugify(self.title)[:max_length]
            for x in itertools.count(1):
                if not Journal.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                    break
                # Truncate the original slug dynamically. Minus 1 for the hyphen.
                self.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        super(Journal, self).save(force_insert, force_update, *args, **kwargs)


    def get_absolute_url(self):
        return reverse('journals:journal', kwargs={'slug': self.slug})

    def admin_thumbnail(self):
        if self.image:
            return mark_safe('<img src="%s"/>' % self.image.thumbnail.url)

    admin_thumbnail.short_description = 'thumbnail'

    #: node type to be used in generated networks
    network_type = 'Journal'

    @property
    def network_id(self):
        #: node identifier when generating a network
        return 'journal:%s' % self.id

    @property
    def network_attributes(self):
        #: data to be included as node attributes when generating a network
        attrs = {'type': self.network_type, 'label': unicode(self)}
        if self.publisher:
            attrs['publisher'] = self.publisher
        return attrs

    @property
    def has_network_edges(self):
        return self.schools.exists()

    @property
    def network_edges(self):
        #: list of tuples for edges in the network
        return [(self.network_id, school.network_id) for school in self.schools.all()]

    contributor_network_cache_key = 'journal-contributor-network'

    @classmethod
    def contributor_network(cls):
        'Network graph of authors, editors, translators, and journals'

        # NOTE: this is a bit slow to be generating on the fly.
        # For now, cache the network after it's generated, but that
        # should probably be refined
        graph = cache.get(cls.contributor_network_cache_key)
        if graph:
            logger.debug('Using cached journal contributor network graph')
            return graph

        graph = Graph()
        graph.to_directed()   # we want a directed graph
        full_start = time.time()
        # gather edges in an ordered dict to avoid generating duplicate
        # edges, and so edge weights can be added efficiently
        # - key is a tuple of source & target nodes, edge label, i.e.
        #   ((source, target), label)
        # - value is the count or weight of that edge
        edges = OrderedDict()

        # helper method to add edges:
        # set count to 1 if not already present; increase count if present
        def add_edge(edge):
            if edge not in edges:
                edges[edge] = 1
            else:
                edges[edge] += 1

        # start = time.time()
        # prefetch journal contributors all at once, for efficiency
        journals = Journal.objects.all().prefetch_related(
            'schools', 'issue_set__editors', 'issue_set__item_set__creators',
            'issue_set__item_set__translators')
        # NOTE: this query is currently the slowest step in generating the
        # graph, nearly ~4s in dev.  It can only be timed here if it is
        # forced to evaluate via list or similar, but it is slightly more
        # efficient not to evaluate it that way
        # logger.debug('Retrieved journal contributor data from db in %.2f sec',
                    # time.time() - start)

        for j in journals:
            start = time.time()
            # starting count, to easily calculate number of nodes & edges added
            vtx_count = len(graph.vs())
            edge_count = len(edges)
            graph.add_vertex(j.network_id, label=unicode(j),
                             type=j.network_type,
                             schools=[s.name for s in j.schools.all()])

            # journal editors are at the issue level
            for issue in j.issue_set.all():
                editors = issue.editors.all()
                for i, editor in enumerate(editors):
                    # only add if not already present
                    if editor.network_id not in graph.vs['name']:
                        graph.add_vertex(editor.network_id,
                                         type=editor.network_type,
                                         label=editor.firstname_lastname)
                    add_edge(((editor.network_id, j.network_id), 'editor'))

                    # add a co-editor rel to any other editors on this issue
                    for co_editor in editors[i+1:]:
                        add_edge(((editor.network_id, co_editor.network_id),
                                 'co-editor'))

                # authors and translators are at the item level
                for item in issue.item_set.all():
                    authors = item.creators.all()
                    for i, author in enumerate(authors):
                        # only add person if not already present in the graph
                        if author.network_id not in graph.vs['name']:
                            graph.add_vertex(author.network_id,
                                             label=author.firstname_lastname,
                                             type=author.network_type)
                        # author is a journal contributor
                        add_edge(((author.network_id, j.network_id),
                                 'contributor'))

                        # each author is connected to the issue editors who
                        # edited their work
                        for editor in editors:
                            add_edge(((editor.network_id, author.network_id),
                                     'edited'))

                        # add a co-author to any other authors on this item
                        for co_author in authors[i+1:]:
                            add_edge(((author.network_id, co_author.network_id),
                                     'co-author'))

                    for translator in item.translators.all():
                        # only add person if not already present in the graph
                        if translator.network_id not in graph.vs['name']:
                            graph.add_vertex(translator.network_id,
                                             label=translator.firstname_lastname,
                                             type=translator.network_type)

                        # translators are connected to the journal they contributed to
                        add_edge(((translator.network_id, j.network_id),
                                 'translator'))
                        # and to the author whose work they translated
                        for author in authors:
                            add_edge(((translator.network_id, author.network_id),
                                     'translated'))

            logger.debug('Added %d nodes and %d edges for %s in %.2f sec',
                         len(graph.vs()) - vtx_count, len(edges) - edge_count,
                         j, time.time() - start)

        # add person-school associations
        # - only a fairly small number of people are associated with
        # schools, so it should be most efficient to handle separately
        start = time.time()
        schooled_people = Person.objects.filter(schools__isnull=False) \
                                .prefetch_related('schools')
        for person in schooled_people:
            try:
                graph.vs.find(name=person.network_id)['schools'] = \
                    [s.name for s in person.schools.all()]

            except ValueError:
                # it's possible we have people associated with schools
                # who are not contributors to our journals, so this is
                # not an error, but providea  warning.
                logger.warn('School-associated person %s not found in contributor network graph',
                            person)
        logger.debug('Added school associations for %d people in %.2f sec',
                     schooled_people.count(), time.time() - start)

        start = time.time()
        # split edge information into source/target tuple and edge label
        edge_src_target, edge_labels = zip(*edges.keys())
        # add the edges to the graph
        graph.add_edges(edge_src_target)
        # set the edge labels
        graph.es['label'] = edge_labels
        # set edge weight based on number of occurrences
        graph.es['weight'] = edges.values()

        logger.debug('Added edges and edge sizes in %.2f sec',
                     time.time() - start)

        logger.debug('Complete journal contributor graph (%d nodes, %d edges) generated in %.2f sec',
                     len(graph.vs()), len(graph.es()), time.time() - full_start)

        # store the generated graph in the cache for the next time
        # for now, set cached graph to never time out
        cache.set(cls.contributor_network_cache_key, graph, None)
        return graph


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
    #: editors, many-to-many to :class:`~zurnatikl.apps.people.models.Person`
    editors = models.ManyToManyField(Person, related_name='issues_edited')
    #: contributing editors, many-to-many to :class:`~zurnatikl.apps.people.models.Person`
    contributing_editors = models.ManyToManyField(Person,
        related_name='issues_contrib_edited', blank=True)
    #: publication address :class:`~zurnatikl.apps.geo.models.Location`
    publication_address = models.ForeignKey(Location,
        help_text="address of publication",
        related_name='issues_published_at', blank=True, null=True)
    #: print address :class:`~zurnatikl.apps.geo.models.Location`
    print_address = models.ForeignKey(Location, blank=True,
        help_text="address where issue was printed",
        related_name='issues_printed_at', null=True)
    #: mailing addresses, many-to-many relation to :class:`~zurnatikl.apps.geo.models.Location`
    mailing_addresses = models.ManyToManyField(Location, blank=True,
        help_text="addresses where issue was mailed",
        related_name='issues_mailed_to')
    #: physical description
    physical_description = models.CharField(max_length=255, blank=True)
    #: boolean indicating if pages are numbered
    numbered_pages = models.BooleanField(default=False)
    #: price
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    #: text notes
    notes = models.TextField(blank=True)
    #: issue sort order, since volume/issue/date are unreliable
    sort_order = models.PositiveSmallIntegerField("Sort order",
        blank=True, null=True,
        help_text='Sort order for display within a journal')

    class Meta:
        ordering = ['journal', 'sort_order', 'volume', 'issue']

    # generate natural key
    def natural_key(self):
        return (self.volume, self.issue, self.season, self.journal.title)

    def __unicode__(self):
        return '%s %s' % (self.journal.title, self.label)

    @property
    def label(self):
        'Issue display label without journal title'
        # format should be Volume #, Issue # (season date)
        parts = [
            'Volume %s' % self.volume if self.volume else None,
            'Issue %s' % self.issue if self.issue else 'Issue'
        ]
        return ', '.join(p for p in parts if p)

    @property
    def date(self):
        'Date for display: including publication date and season, if any'
        return ' '.join(d for d in [self.season, unicode(self.publication_date)] if d)

    def get_absolute_url(self):
        return reverse('journals:issue',
            kwargs={'journal_slug': self.journal.slug, 'id': self.id})

    @property
    def next_issue(self):
        'Next issue in order, if there is one (requires sort_order to be set)'
        if self.sort_order is not None:
            next_issues = self.journal.issue_set.all().filter(sort_order__gt=self.sort_order)
            if next_issues.exists():
                return next_issues.first()

    @property
    def previous_issue(self):
        'Previous issue in order, if there is one (requires sort_order to be set)'
        if self.sort_order is not None:
            prev_issues = self.journal.issue_set.all().filter(sort_order__lt=self.sort_order)
            if prev_issues.exists():
                return prev_issues.last()

    #: node type to be used in generated networks
    network_type = 'Issue'

    @property
    def network_id(self):
        #: node identifier when generating a network
        return 'issue:%s' % self.id

    @property
    def network_attributes(self):
        #: data to be included as node attributes when generating a network
        attrs = {'type': self.network_type, 'label': unicode(self)}
        if self.volume:
            attrs['volume'] = self.volume
        if self.issue:
            attrs['issue'] = self.issue
        if self.publication_date:
            attrs['publication date'] = unicode(self.publication_date)
        return attrs

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


class ItemManager(models.Manager):
    def get_by_natural_key(self, title):
        return self.get(title=title)

class Item(models.Model):
    'Item in a :class:`Issue`'

    objects = ItemManager()

    #: :class:`Issue` the item is included in
    issue = models.ForeignKey('Issue')
    #: title
    title = models.CharField(max_length=255)
    #: creators, many-to-many to :class:`~zurnatikl.apps.people.models.Person`,
    #: related via :class:`~zurnatikl.apps.people.models.CreatorName`,
    creators = models.ManyToManyField(Person, through='CreatorName',
        related_name='items_created', blank=True)
    #: anonymous
    anonymous = models.BooleanField(help_text='check if labeled as by Anonymous',
        default=False)
    #: no creator listed
    no_creator = models.BooleanField(help_text='check if no author is listed [including Anonymous]',
        default=False)
    #: translators, :class:`~zurnatikl.apps.people.models.Person`,
    translators = models.ManyToManyField(Person,
        related_name='items_translated', blank=True)
    #: start page
    start_page = models.IntegerField()
    #: end page
    end_page = models.IntegerField()
    #: :class:`Genre`
    genre = models.ManyToManyField('Genre')
    #: includes abbreviated text
    abbreviated_text = models.BooleanField(help_text='check if the text contains abbreviations such as wd, yr, etc',
        default=False)
    #: mentioned people, many-to-many to :class:`~zurnatikl.apps.people.models.Person`
    persons_mentioned = models.ManyToManyField(Person,
        related_name='items_mentioned_in', blank=True)
    #: addressses, many-to-many to :class:`zurnatikl.apps.geo.models.Location`
    addresses = models.ManyToManyField(Location, blank=True)
    #: indicates if it is a literary advertisement
    literary_advertisement = models.BooleanField(default=False)
    #: notes
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['issue', 'start_page', 'end_page', 'title']

    # generate natural key
    def natural_key(self):
        return (self.title)

    def __unicode__(self):
        return self.title

    @property
    def edit_url(self):
        # generate a link to admin edit form for current issue item;
        # for use in various inlines, to link back to item
        return reverse('admin:%s_%s_change' % (self._meta.app_label,
                                              self._meta.model_name),
                       args=(self.id,))

    #: node type to be used in generated networks
    network_type = 'Item'

    @property
    def network_id(self):
        #: node identifier when generating a network
        return 'item:%s' % self.id

    @property
    def network_attributes(self):
        #: data to be included as node attributes when generating a network
        attrs = {
            'type': self.network_type,
            'label': self.title,
            'anonymous': self.anonymous,
            'no creator': self.no_creator,
            'issue': unicode(self.issue)
        }
        if self.genre.exists():
            attrs['genre'] = ', '.join([g.name for g in self.genre.all()])
        return attrs

    @property
    def has_network_edges(self):
        return any([self.issue, self.creators.exists(), self.translators.exists(),
                    self.persons_mentioned.exists(), self.addresses.exists(),
                    self.placename_set.exists()])

    @property
    def network_edges(self):
        #: list of tuples for edges in the network
        edges = []
        if self.issue:
            edges.append((self.network_id, self.issue.network_id))
        edges.extend([(self.network_id, c.network_id, {'label': 'creator'})
            for c in self.creators.all()])
        edges.extend([(self.network_id, trans.network_id, {'label': 'translator'})
             for trans in self.translators.all()])
        edges.extend([(self.network_id, person.network_id, {'label': 'mentioned'})
             for person in self.persons_mentioned.all()])
        edges.extend([(self.network_id, loc.network_id)
             for loc in self.addresses.all()])
        # location is not required in placenames, but only placenames with a location
        # can contribute a network edge
        edges.extend([(self.network_id, placename.location.network_id, {'label': 'mentioned'})
             for placename in self.placename_set.filter(location__isnull=False).all()
             if placename.location is not None])

        return edges



class CreatorNameManager(models.Manager):
    def get_by_natural_key(self, name_used):
        return self.get(name_used=name_used)

class CreatorName(models.Model):
    # join model for item creator,
    # with a field for capturing name as displayed on the publication

    objects = CreatorNameManager()

    item = models.ForeignKey(Item)
    person = models.ForeignKey(Person)
    name_used = models.CharField(max_length=200, blank=True)

    def natural_key(self):
        return (self.name_used,)

    def __unicode__(self):
        return unicode(self.person)
