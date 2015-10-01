import logging
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.views.generic.detail import SingleObjectMixin
import networkx as nx

from .models import Person
from zurnatikl.apps.journals.models import Journal
from zurnatikl.apps.network.base_views import SigmajsJSONView, \
   NetworkGraphExportView


logger = logging.getLogger(__name__)


class PeopleList(ListView):
    '''List all
    :class:`~zurnatikl.apps.people.models.Person` who have edited
    at least one :class:`~zurnatikl.apps.journals.models.Issue',
    authored one :class:`~zurnatikl.apps.journals.models.Item`,
    or translated one :class:`~zurnatikl.apps.journals.models.Item`.
    '''
    model = Person

    queryset = Person.objects.filter(
            Q(issues_edited__isnull=False) |
            Q(items_created__isnull=False) |
            Q(items_translated__isnull=False)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super(PeopleList, self).get_context_data(**kwargs)
        authors = Person.objects.filter(Q(items_created__isnull=False)).distinct()
        context['authors_ids'] = [author.id for author in authors]
        editors = Person.objects.filter(Q(issues_edited__isnull=False) | Q(issues_contrib_edited__isnull=False)).distinct()
        context['editors_ids'] = [editor.id for editor in editors]
        translators = Person.objects.filter(Q(items_translated__isnull=False)).distinct()
        context['translators_ids'] = [translator.id for translator in translators]
        return context


class PersonDetail(DetailView):
    '''Display details for a single
    :class:`~zurnatikl.apps.people.models.Person`'''
    model = Person
    # NOTE: could override get_object to 404 for non-editor/non-authors


class Egograph(DetailView):
    '''Display an egograph for a single
    :class:`~zurnatikl.apps.people.models.Person`.'''
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
        graph = Journal.contributor_network()
        # restrict graph to an egograph around the current person
        # with a radius of 1 before export
        return nx.generators.ego.ego_graph(graph, person.network_id, 1)


class EgographJSON(SigmajsJSONView, EgographBaseView):
    '''Egograph for a single :class:`~zurnatikl.apps.people.models.Person`
    in a JSON format appropriate for use with Sigma.js'''
    pass


class EgographExport(NetworkGraphExportView, EgographBaseView):
    '''Downloadable eggograph for a single
    :class:`~zurnatikl.apps.people.models.Person` in GEXF or GraphML.'''

    def get_context_data(self, **kwargs):
        # set person slug as base filename
        self.filename = kwargs['slug']
        # inherit egograph generation from EgographBaseView
        return super(EgographExport, self).get_context_data(**kwargs)


