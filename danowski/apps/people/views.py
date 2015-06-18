import logging
import time
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.views.generic.detail import SingleObjectMixin
import networkx as nx
from networkx.readwrite import json_graph

from .models import Person
from danowski.apps.journals.models import Journal
from danowski.apps.network.base_views import JSONView, NetworkGraphExportView


logger = logging.getLogger(__name__)


class PeopleList(ListView):
    '''List all
    :class:`~danowski.apps.people.models.Person` who have edited
    at least one :class:`~danowski.apps.journals.models.Issue' or
    authored one :class:`~danowski.apps.journals.models.Item`.'''
    model = Person
    queryset = Person.objects.filter(
            Q(issues_edited__isnull=False) |
            Q(items_created__isnull=False)
        ).distinct()


class PersonDetail(DetailView):
    '''Display details for a single
    :class:`~danowski.apps.people.models.Person`'''
    model = Person
    # NOTE: could override get_object to 404 for non-editor/non-authors


class Egograph(DetailView):
    '''Display an egograph for a single
    :class:`~danowski.apps.people.models.Person`.'''
    # template for displaying / managing javascript egograph
    # actual egograph generated via json view below
    model = Person
    template_name = 'people/person_egograph.html'


class EgographBaseView(SingleObjectMixin):
    '''Base view for generating an egograph for a single person,
    for use in disseminating the graph as JSON, GEXF, or GraphML.'''
    model = Person

    def get_context_data(self, **kwargs):
        person = self.get_object()

        # get the full journal-author-editor network
        graph = Journal.author_editor_network()
        # restrict graph to an egograph around the current person
        # with a radius of 1 before export
        return nx.generators.ego.ego_graph(graph, person.network_id, 1)


class EgographJSON(JSONView, EgographBaseView):
    '''Egograph for a single :class:`~danowski.apps.people.models.Person`
    in a JSON format appropriate for use with Sigma.js'''

    def get_context_data(self, **kwargs):
        graph = super(EgographJSON, self).get_context_data(**kwargs)
        start = time.time()
        data = json_graph.node_link_data(graph,
            attrs=dict(id='id', source='source', target='target', key='id'))
        logger.debug('Generated json in %.2f sec' % \
            (time.time() - start))

        start = time.time()
        # networkx json format is not quite what sigma wants
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


class EgographExport(NetworkGraphExportView, EgographBaseView):
    '''Downloadable eggograph for a single
    :class:`~danowski.apps.people.models.Person` in GEXF or GraphML.'''

    def get_context_data(self, **kwargs):
        # set person slug as base filename
        self.filename = kwargs['slug']
        # inherit egograph generation from EgographBaseView
        return super(EgographExport, self).get_context_data(**kwargs)


