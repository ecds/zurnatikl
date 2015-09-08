import re

from django.db.models import Q
from django.http import Http404
from django.views.generic import View, ListView, DetailView
from django.shortcuts import render

from zurnatikl.apps.network.base_views import NetworkGraphExportView
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


class AuthorEditorNetworkExport(NetworkGraphExportView):
    '''Downloadable eggograph for journals, authors, and editors
    :class:`~zurnatikl.apps.people.models.Person` in GEXF or GraphML.'''
    filename = 'journals-authors-editors'

    def get_context_data(self, **kwargs):
        # full journal-author-editor network
        return Journal.author_editor_network()
        # set person slug as base filename
