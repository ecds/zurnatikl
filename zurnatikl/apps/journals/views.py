import re

from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from django.views.generic import View, ListView, DetailView, TemplateView


from zurnatikl.apps.network.base_views import NetworkGraphExportView, \
    SigmajsJSONView
from .models import Journal, Issue, Item
from .forms import SearchForm


class JournalList(ListView):
    'List all Journals'
    model = Journal


class JournalDetail(DetailView):
    'Display details for a single journal'
    model = Journal


class IssueDetail(DetailView):
    'Display details for a single issue of a journal'
    model = Issue

    def get_object(self, queryset=None):
        # override default get object to lookup issue by
        # journal slug + item id
        if queryset is None:
            queryset = self.get_queryset()

        try:
            return queryset.get(journal__slug=self.kwargs['journal_slug'],
                                pk=self.kwargs['id'])
        except Issue.DoesNotExist:
            raise Http404

class SearchView(View):
    'Search items by title or creator name'
    form_class = SearchForm
    template_name = 'journals/search_results.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.GET)
        ctx = {'form': form}
        # currently keyword is the only field and is required
        if form.is_valid():
            # search for items by author or title
            kw = form.cleaned_data.get('keyword')
            # split the query into words on spaces or comma space
            # and match any field on any word
            words = re.split(',? +', kw)
            items = Item.objects.all().distinct()
            # distinct required in case a term matches multiple fields
            for w in words:
                items = items.filter(
                    Q(title__icontains=w) |
                    Q(creators__last_name__icontains=w) |
                    Q(creators__first_name__icontains=w) |
                    Q(creators__name__first_name__icontains=w) |
                    Q(creators__name__last_name__icontains=w) |
                    Q(creators__penname__name__icontains=w))

            ctx['items'] = items

        return render(request, self.template_name, ctx)


class ContributorNetwork(TemplateView):
    template_name = 'journals/contributor_network.html'


class ContributorNetworkBaseView(TemplateView):
    '''Base view to generate full journal contributor network
    for use in disseminating the graph as JSON, GEXF, or GraphML.'''

    def get_context_data(self, **kwargs):
        # full journal-contributor network
        return Journal.contributor_network()


class ContributorNetworkJSON(SigmajsJSONView, ContributorNetworkBaseView):
    '''Journal contributor network in a JSON format appropriate for use
    with Sigma.js'''

    community_detection = True
    # full network graph layout takes ~4s to calculate, so cache it
    cache_layout = True
    # FIXME: how do we make sure the cached graph layout stays in sync
    # with the cached graph?


class ContributorNetworkExport(NetworkGraphExportView, ContributorNetworkBaseView):
    '''Downloadable eggograph for
    :class:`~zurnatikl.apps.journals.models.Journal` and
    :class:`~zurnatikl.apps.people.models.Person`
    contributors (authors, editors, and translators) as GEXF or GraphML.'''

    filename = 'journals-contributors'
