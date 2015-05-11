from django.views.generic import ListView
from danowski.apps.journals.models import Journal

class JournalList(ListView):
    model = Journal
