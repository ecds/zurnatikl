from django.http import Http404
from django.views.generic import ListView, DetailView
from danowski.apps.journals.models import Journal, Issue

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
            return queryset.get(journal__slug=self.kwargs['slug'],
                                pk=self.kwargs['id'])
        except Issue.DoesNotExist:
            raise Http404
