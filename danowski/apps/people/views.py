import logging
import json
import time
from django.db.models import Q
from django.views.generic import ListView, DetailView, View
from django.views.generic.detail import SingleObjectMixin
import networkx as nx
from networkx.readwrite import json_graph

from .models import Person
from danowski.apps.journals.models import Journal
from danowski.apps.network.base_views import JSONView


logger = logging.getLogger(__name__)


class PeopleList(ListView):
    'List editors and authors'
    model = Person
    queryset = Person.objects.filter(
            Q(issues_edited__isnull=False) |
            Q(issues_contrib_edited__isnull=False) |
            Q(items_created__isnull=False)
        ).distinct()


class PersonDetail(DetailView):
    'Display details for a single person'
    model = Person
    # NOTE: could override get_object to 404 for non-editor/non-authors


class PersonEgographJSON(JSONView, SingleObjectMixin):
    model = Person
    def get_context_data(self, **kwargs):
        person = self.get_object()

        # get the full journal-author-editor network
        graph = Journal.author_editor_network()
        # restrict graph to an egograph around the current person
        # with a radius of 1 before export
        graph = nx.generators.ego.ego_graph(graph, person.network_id, 1)

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


class PersonEgograph(DetailView):
    'Display an egograph for a single person'
    model = Person
    template_name = 'people/person_egograph.html'