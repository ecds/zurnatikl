from collections import defaultdict
import itertools
import logging
import time

from django.views.generic import ListView
from igraph import Graph

from zurnatikl.apps.geo.models import Location
from zurnatikl.apps.journals.models import Journal, Issue, Item
from zurnatikl.apps.people.models import Person, School
from .utils import add_nodes_to_graph, add_edges_to_graph, to_ascii, \
    encode_unicode
from .base_views import NetworkGraphExportView, SigmajsJSONView


logger = logging.getLogger(__name__)


def generate_network_graph(use_ascii=False):
    '''Generate a :class:`networkx.MultiGraph` from the connections among
    schools, people, locations, journals, issues, and items.
    Optionally convert unicode to ascii, if needed by the export tool.
    '''
    start = time.time()
    # generate a graph for serialization
    # TODO: probably need to add caching on this graph
    graph = Graph()
    # igraph requires numerical id; zurnatikl uses network id to
    # differentiate content types & database ids

    # TODO: make node type an object attribute

    def attr(attributes):
        # force content to ascii if requested
        if use_ascii:
            return to_ascii(attributes)
        else:
            # explicitly encode unicode, as a workaround for
            # igraph/ascii errors
            # see https://github.com/igraph/python-igraph/issues/5
            return encode_unicode(attributes)

    schools = School.objects.all()
    edges = []
    for school in schools:
        graph.add_vertex(school.network_id, type='School',
                         **attr(school.network_attributes))
        # edges can't be added until both source and target nodes exist
        if school.has_network_edges:
            edges.extend(school.network_edges)

    people = Person.objects.all().prefetch_related('schools', 'dwellings')
    for person in people:
        graph.add_vertex(person.network_id, type='Person',
                         **attr(person.network_attributes))
        if person.has_network_edges:
            edges.extend(person.network_edges)

    locations = Location.objects.all().prefetch_related('placename_set')
    for loc in locations:
        graph.add_vertex(loc.network_id, type='Location',
                         **attr(loc.network_attributes))
        if loc.has_network_edges:
            edges.extend(loc.network_edges)

    journals = Journal.objects.all()
    for journal in journals:
        graph.add_vertex(journal.network_id, type='Journal',
                         **attr(journal.network_attributes))
        if journal.has_network_edges:
            edges.extend(journal.network_edges)

    issues = Issue.objects.all().prefetch_related('editors',
        'contributing_editors', 'publication_address', 'print_address',
        'mailing_addresses')
    for issue in issues:
        graph.add_vertex(issue.network_id, type='Issue',
                         **attr(issue.network_attributes))
        if issue.has_network_edges:
            edges.extend(issue.network_edges)
    items = Item.objects.all().prefetch_related('issue', 'creators',
        'translators', 'persons_mentioned', 'addresses', 'genre')
    for item in items:
        graph.add_vertex(item.network_id, type='Item',
                         **attr(item.network_attributes))
        if item.has_network_edges:
            edges.extend(item.network_edges)

    # some edges have edge attributes, others do not
    # edges without attributes can be added en masse
    simple_edges = [edge for edge in edges if len(edge) == 2]
    graph.add_edges(simple_edges)
    edge_attrs = [edge for edge in edges if len(edge) > 2]
    for source, target, attributes in edge_attrs:
        graph.add_edge(source, target, **attributes)

    logger.debug('Generated full graph in %.2f sec' % (time.time() - start))
    return graph

class FullNetworkExport(NetworkGraphExportView):
    filename = 'network_data'

    def get_context_data(self, **kwargs):
        use_ascii = (self.export_format == 'gml')
        return generate_network_graph(use_ascii=use_ascii)


class SchoolsNetwork(ListView):
    model = School
    template_name = 'network/schools.html'

    def get_queryset(self):
        # url slug is for school categorizer
        return School.objects.filter(categorizer=self.kwargs['slug'])


class SchoolsNetworkBaseView(SchoolsNetwork):
    '''Base view for generating a network graph for a set of schools,
    for use in disseminating the graph as JSON, GEXF, or GraphML.'''

    def get_context_data(self, **kwargs):
        return School.schools_network(self.get_queryset())


class SchoolsNetworkJSON(SigmajsJSONView, SchoolsNetworkBaseView):
    '''Network graph based on a number of :class:`~zurnatikl.apps.people.models.School`
    objects in a JSON format appropriate for use with Sigma.js'''


class SchoolsNetworkExport(NetworkGraphExportView, SchoolsNetworkBaseView):
    '''Downloadable eggograph for a
    :class:`~zurnatikl.apps.people.models.School` group in GEXF or GraphML.'''

    def get_context_data(self, **kwargs):
        # set filename based on categorizer slug
        self.filename = '%s-schools' % kwargs['slug']
        # inherit graph generation logic
        return super(SchoolsNetworkExport, self).get_context_data(**kwargs)




