import logging
import networkx as nx
from networkx.readwrite import json_graph
import time

from django.views.generic import ListView

from zurnatikl.apps.geo.models import Location
from zurnatikl.apps.journals.models import Journal, Issue, Item
from zurnatikl.apps.people.models import Person, School
from .utils import add_nodes_to_graph, add_edges_to_graph
from .base_views import NetworkGraphExportView, JSONView, NetworkGraphExportView

logger = logging.getLogger(__name__)


def generate_network_graph(use_ascii=False):
    '''Generate a :class:`networkx.MultiGraph` from the connections among
    schools, people, locations, journals, issues, and items.
    Optionally convert unicode to ascii, if needed by the export tool.
    '''

    # generate a networkx graph for serialization
    # TODO: probably need to add caching on this graph
    graph = nx.MultiGraph()
    start = time.time()

    # add all the high-level objects to the network as nodes
    schools = School.objects.all()
    add_nodes_to_graph(schools, graph, 'School', use_ascii)
    people = Person.objects.all().prefetch_related('schools', 'dwellings')
    add_nodes_to_graph(people, graph, 'Person', use_ascii)
    locations = Location.objects.all().prefetch_related('placename_set')
    add_nodes_to_graph(locations, graph, 'Location', use_ascii)
    journals = Journal.objects.all()
    add_nodes_to_graph(journals, graph, 'Journal', use_ascii)
    issues = Issue.objects.all().prefetch_related('editors',
        'contributing_editors', 'publication_address', 'print_address',
        'mailing_addresses')
    add_nodes_to_graph(issues, graph, 'Issue', use_ascii)
    items = Item.objects.all().prefetch_related('issue', 'creators',
        'translators', 'persons_mentioned', 'addresses', 'genre')
    add_nodes_to_graph(items, graph, 'Item', use_ascii)

    # then add edges to connect everything

    add_edges_to_graph(schools, graph, 'School')
    add_edges_to_graph(people, graph, 'Person')
    # locations do not have any outbound edges
    add_edges_to_graph(journals, graph, 'Journal')
    add_edges_to_graph(issues, graph, 'Issue')
    add_edges_to_graph(items, graph, 'Item')

    logger.debug('Generated full graph in %.2f sec' % (time.time() - start))

    return graph


class FullNetworkExport(NetworkGraphExportView):
    filename = 'network_data'

    def get_context_data(self, **kwargs):
        use_ascii = (self.export_format == 'gexf')
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
        schools = self.get_queryset()

        # generate the graph
        graph = nx.Graph()  # multi? directional?
        start = time.time()
        graph.add_nodes_from(
            # node id, node attributes
            [(s.network_id, {'label': unicode(s)}) for s in schools],
            type='School')

        # add people, places, & journals associated with each school
        for s in schools:
            # a school may have one or more locations
            graph.add_nodes_from(
                [(loc.network_id, {'label': loc.short_label})
                for loc in s.locations.all()],
                type='Place')
            graph.add_edges_from([(s.network_id, loc.network_id)
                                  for loc in s.locations.all()])

            # people can be associated with one or more schools
            graph.add_nodes_from(
                [(p.network_id, {'label': p.firstname_lastname})
                  for p in s.person_set.all()],
                type='Person')
            graph.add_edges_from([(s.network_id, p.network_id)
                                  for p in s.person_set.all()])

            # a journal can also be associated with a school
            graph.add_nodes_from(
                [(j.network_id, {'label': unicode(j)})
                for j in s.journal_set.all()],
                type='Journal')
            graph.add_edges_from([(s.network_id, j.network_id)
                                  for j in s.journal_set.all()])

            logger.debug('Added %d locations, %s people, and %d journals for %s in %.2f sec' % \
                (s.locations.all().count(), s.person_set.all().count(),
                 s.journal_set.all().count(), s, time.time() - start))

        return graph


class SchoolsNetworkJSON(JSONView, SchoolsNetworkBaseView):
    '''Network graph based on a number of :class:`~zurnatikl.apps.people.models.School`
    objects in a JSON format appropriate for use with Sigma.js'''

    def get_context_data(self, **kwargs):
        graph = super(SchoolsNetworkJSON, self).get_context_data(**kwargs)
        start = time.time()
        data = json_graph.node_link_data(graph,
            attrs=dict(id='id', source='source', target='target', key='id'))
        logger.debug('Generated json in %.2f sec' % \
            (time.time() - start))

        start = time.time()
        # networkx json format is not quite what sigma wants
        # TODO: refactor into common location for reusability
        # rename links -> edges
        data['edges'] = data.pop('links')
        i = 0
        for edge in data['edges']:
            # output doesn't include edge ids, but sigma wants them
            edge['id'] = i
            # output references source/target by index, not id
            edge['source'] = data['nodes'][edge['source']]['id']
            edge['target'] = data['nodes'][edge['target']]['id']
            i += 1
        logger.debug('Converted json for sigma.js in %.2f sec' % \
            (time.time() - start))
        return data


class SchoolsNetworkExport(NetworkGraphExportView, SchoolsNetworkBaseView):
    '''Downloadable eggograph for a
    :class:`~zurnatikl.apps.people.models.School` group in GEXF or GraphML.'''

    def get_context_data(self, **kwargs):
        # set filename based on categorizer slug
        self.filename = '%s-schools' % kwargs['slug']
        # inherit graph generation logic
        return super(SchoolsNetworkExport, self).get_context_data(**kwargs)




