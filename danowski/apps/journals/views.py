from django.views.generic import ListView, DetailView
from danowski.apps.journals.models import Journal

class JournalList(ListView):
    'List all Journals'
    model = Journal


class Journal(DetailView):
    'Display details for a single journal'
    model = Journal
