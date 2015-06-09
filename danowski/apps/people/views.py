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


def add_person_connections(graph, person):

    if person.coeditors.exists():
        start = time.time()
        graph.add_nodes_from(
            [(p.network_id, {'label': unicode(p)}) for p in person.coeditors],
            type='Person')
        edges = [(person.network_id, p.network_id) for p in person.coeditors]
        graph.add_edges_from(edges, label='co-editor')
        # TODO: edges between people and other people/journals
        logger.debug('Added %d co-editors in %.2f sec' % \
            (len(person.coeditors), time.time() - start))

    if person.coauthors.exists():
        start = time.time()
        graph.add_nodes_from(
            [(p.network_id, {'label': unicode(p)}) for p in person.coauthors],
            type='Person')
        edges = [(person.network_id, p.network_id) for p in person.coauthors]
        graph.add_edges_from(edges, label='co-author')
        # TODO: edges between people and other people/journals
        logger.debug('Added %d co-authors in %.2f sec' % \
            (len(person.coauthors), time.time() - start))

    if person.editors.exists():
        start = time.time()
        graph.add_nodes_from(
            [(p.network_id, {'label': unicode(p)}) for p in person.editors],
            type='Person')
        edges = [(person.network_id, p.network_id) for p in person.editors]
        graph.add_edges_from(edges, label='editor')
        # TODO: edges between people and other people/journals
        logger.debug('Added %d editors in %.2f sec' % \
            (len(person.editors), time.time() - start))

    # if person.edited_by.exists():
    #     start = time.time()
    #     graph.add_nodes_from(
    #         [(p.network_id, {'label': unicode(p)}) for p in person.edited_by],
    #         type='Person')
    #     edges = [(person.network_id, p.network_id) for p in person.edited_by]
    #     graph.add_edges_from(edges, label='edited by')
    #         # TODO: edges between people and other people/journals
    #     logger.debug('Added %d edited by in %.2f sec' % \
    #         (len(person.edited_by), time.time() - start))

    return graph


class PersonEgographJSON(JSONView, SingleObjectMixin):
    model = Person
    def get_context_data(self, **kwargs):
        person = self.get_object()

        connected_people = set()
        if person.coeditors.exists():
            connected_people.update(set(person.coeditors))
        if person.coauthors.exists():
            connected_people.update(set(person.coauthors))
        if person.editors.exists():
            connected_people.update(set(person.editors))
        if person.edited_by.exists():
            connected_people.update(set(person.edited_by))

        graph = nx.MultiGraph()

        # add current person to the graph
        graph.add_node(person.network_id, {'label': unicode(person), 'type': 'Person'})

        # connected people
        graph = add_person_connections(graph, person)
        # FIXME: there must be a more efficient way to generate these connections
        # connections between connected people
        # how to do this without taking too long?
        # start = time.time()
        # for person in connected_people:
        #     graph = add_person_connections(graph, person)
        # logger.debug('Added intra-personal connections for %d people in %.2f sec' % \
        #     (len(connected_people), time.time() - start))

        # connected journals
        start = time.time()
        journals_edited = Journal.objects.by_editor(person)
        graph.add_nodes_from(
            # node id, node attributes
            [(j.network_id, {'label': unicode(j)}) for j in journals_edited],
            type='Journal')
        graph.add_edges_from([(person.network_id, j.network_id) for j in journals_edited],
            type='editor')
        logger.debug('Added %d journals edited in %.2f sec' % \
            (len(journals_edited), time.time() - start))


        journals_contributor = Journal.objects.by_author(person)
        graph.add_nodes_from(
            # node id, node attributes
            [(j.network_id, {'label': unicode(j)}) for j in journals_contributor],
            type='Journal')
        # NOTE: currently not differentiating edge types (editor/author)
        graph.add_edges_from([(person.network_id, j.network_id) for j in journals_contributor])
        logger.debug('Added %d connected journals in %.2f sec' % \
            (len(journals_contributor), time.time() - start))

        start = time.time()
        count = 0

        # FIXME: need to distinguish journals person edited vs journals
        # where person authored items

        for j in journals_edited:
            # TODO: add rels between all co-authors, co-editors, and editors/authors
            # *here* instead of using connected people

            editors = Person.objects.filter(issues_edited__journal=j).distinct()
            # this is redundant currently
            graph.add_nodes_from(
                [(p.network_id, {'label': unicode(p)}) for p in editors],
                type='Person')
            graph.add_edges_from([(p.network_id, j.network_id) for p in editors],
                label='editor')
            graph.add_edges_from([(person.network_id, p.network_id) for p in editors],
                label='co-editor')
            count += editors.count()

            # TODO: relate all co-editors to each other

            authors = Person.objects.filter(items_created__issue__journal=j).distinct()
            graph.add_nodes_from(
                [(p.network_id, {'label': unicode(p)}) for p in authors],
                type='Person')
            graph.add_edges_from([(person.network_id, p.network_id) for p in authors],
                label='edited by')
            count += authors.count()
            graph.add_edges_from([(p.network_id, j.network_id) for p in authors],
                label='contributor')
        logger.debug('Added %d journal edges for editors/authors by via journal in %.2f sec' % \
            (count, time.time() - start))


        for j in journals_contributor:
            # TODO: add rels between all co-authors, co-editors, and editors/authors
            # *here* instead of using connected people

            editors = Person.objects.filter(issues_edited__journal=j).distinct()
            # this may be redundant...
            graph.add_nodes_from(
                [(p.network_id, {'label': unicode(p)}) for p in editors],
                type='Person')
            graph.add_edges_from([(p.network_id, j.network_id) for p in editors],
                label='editor')
            graph.add_edges_from([(person.network_id, p.network_id) for p in editors],
                label='editor')
            count += editors.count()

            # TODO: relate all co-editors to each other

            # for now, we don't care about other authors
        logger.debug('Added %d journal edges for editors via journals contributed to in %.2f sec' % \
            (count, time.time() - start))



        # restrict graph to an egograph around the current person
        # with a radius of 1 before export
        # (remove extra connections that have been added)
        graph = nx.generators.ego.ego_graph(graph, person.network_id, 1)

        # arg, this json format is not what sigma wants
        # rename links -> edges
        start = time.time()
        data = json_graph.node_link_data(graph,
            attrs=dict(id='id', source='source', target='target', key='id'))
        logger.debug('Generated json in %.2f sec' % \
            (time.time() - start))

        start = time.time()
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