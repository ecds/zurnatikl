import logging
import networkx as nx
import time

from django.views.generic import ListView

from zurnatikl.apps.geo.models import Location
from zurnatikl.apps.journals.models import Journal, Issue, Item
from zurnatikl.apps.people.models import Person, School
from .utils import add_nodes_to_graph, add_edges_to_graph
from .base_views import NetworkGraphExportView, SigmajsJSONView


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




