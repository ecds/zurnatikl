from collections import defaultdict
from django.db import models
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.utils.safestring import mark_safe
import itertools
import logging
import time

from igraph import Graph
from djago_date_extensions import fields as ddx
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


    @classmethod
    def contributor_network(self):
        'Network graph of authors, editors, translators, and journals'

        # NOTE: this is probably a bit slow to be generating on the fly.
        # For now, cache the network after it's generated, but that
        # will need to be refined
        graph = cache.get('journal_auth_ed_network')
        if graph:
            return graph

        graph = Graph()
        graph.to_directed()   # we want a directed graph
        full_start = time.time()
        # gather edges in a set to avoid generating duplicate edges;
        # will be added as a tuple of source & target nodes, edge label:
        #   ((source, target), label)
        edges = set()
        # track sizes for repeated edges
        edge_size = defaultdict(int)

        start = time.time()
        # prefetch journal contributors all at once, for efficiency
        journals = list(Journal.objects.all().prefetch_related(
            'issue_set__editors', 'issue_set__item_set__creators',
            'issue_set__item_set__translators'))
        logger.debug('Retrieved journal contributor data from db in %.2f sec',
                     time.time() - start)
        for j in journals:
            start = time.time()
            # starting count, to easily calculate number of nodes & edges added
            vtx_count = len(graph.vs())
            edge_count = len(edges)
            graph.add_vertex(j.network_id, label=unicode(j),
                             type=j.network_type)

            # journal editors are at the issue level
            for issue in j.issue_set.all():
                editors = issue.editors.all()
                for ed in editors:
                    # only add if not already present
                    if ed.network_id not in graph.vs['name']:
                        graph.add_vertex(ed.network_id, type=ed.network_type,
                                         label=ed.firstname_lastname)
                    edge = ((ed.network_id, j.network_id), 'editor')
                    edges.add(edge)
                    edge_size[edge] += 1

                # if an issue has more than one editor, relate them
                # as co-editors
                if editors.count() > 1:
                    for i, editor in enumerate(editors):
                        # each editor is a co-editor with all other editors
                        for co_editor in editors[i+1:]:
                            edge = ((editor.network_id, co_editor.network_id),
                                    'co-editor')
                            edges.add(edge)
                            edge_size[edge] += 1

                # authors and translators are at the item level
                for item in issue.item_set.all():
                    authors = item.creators.all()
                    for author in authors:
                        # only add person if not already present in the graph
                        if author.network_id not in graph.vs['name']:
                            graph.add_vertex(author.network_id,
                                             label=author.firstname_lastname,
                                             type=author.network_type)
                        # author is a journal contributor
                        edge = ((author.network_id, j.network_id), 'contributor')
                        edges.add(edge)
                        edge_size[edge] += 1

                        # each author is connected to the issue editors who
                        # edited their work
                        for editor in editors:
                            edge = ((editor.network_id, author.network_id),
                                    'edited')
                            edges.add(edge)
                            edge_size[edge] += 1

                    # if an item has more than one author, relate them
                    # as co-authors
                    if authors.count() > 1:
                        for i, editor in enumerate(authors):
                            # each author is a co-author with all other authors
                            for co_author in authors[i+1:]:
                                edge = ((author.network_id, co_author.network_id),
                                        'co-author')
                                edges.add(edge)
                                edge_size[edge] += 1

                    for translator in item.translators.all():
                        # only add person if not already present in the graph
                        if translator.network_id not in graph.vs['name']:
                            graph.add_vertex(translator.network_id,
                                             label=translator.firstname_lastname,
                                             type=translator.network_type)

                        # translators are connected to the journal they contributed to
                        edge = ((translator.network_id, j.network_id), 'translator')
                        edges.add(edge)
                        edge_size[edge] += 1
                        # and to the author whose work they translated
                        for author in authors:
                            edge = ((translator.network_id, author.network_id),
                                    'translated')
                            edges.add(edge)
                            edge_size[edge] += 1

            logger.debug('Added %d nodes and %d edges for %s in %.2f sec',
                         len(graph.vs()) - vtx_count, len(edges) - edge_count,
                         j, time.time() - start)

        start = time.time()
        # split edge information into source/target tuple and edge label
        edge_src_target, edge_labels = zip(*edges)
        # add the edges to the graph
        graph.add_edges(edge_src_target)
        # set the edge labels
        graph.es['label'] = edge_labels
        # set default edge size as 1
        graph.es['size'] = 1

        # update edge sizes for size > 1
        for edge_info, size in edge_size.iteritems():
            # if size is one, nothing needs to be done
            if size == 1:
                next

            # edge info is a tuple of (source, target), edge label
            # vertex can be found by name, but edges must be found
            # by vertex index
            source = graph.vs.find(edge_info[0][0]).index
            target = graph.vs.find(edge_info[0][1]).index
            label = edge_info[1]

            # NOTE: search must include label filter, since the same edge
            # could exist with different labels
            edge = graph.es.find(_source=source, _target=target, label=label)
            edge['size'] = size

        logger.debug('Added edges and edge sizes in %.2f sec',
                     time.time() - start)

        logger.debug('Complete journal contributor graph (%d nodes, %d edges) generated in %.2f sec',
                     len(graph.vs()), len(graph.es()), time.time() - full_start)

        # store the generated graph in the cache for next time
        cache.set('journal_auth_ed_network', graph)
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
    mailing_addresses  = models.ManyToManyField(Location, blank=True,
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
