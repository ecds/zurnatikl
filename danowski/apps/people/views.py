from django.db.models import Q
from django.views.generic import ListView

from .models import Person


class PeopleList(ListView):
    'List editors and authors'
    model = Person
    queryset = Person.objects.filter(
            Q(issues_edited__isnull=False) |
            Q(issues_contrib_edited__isnull=False) |
            Q(items_created__isnull=False)
        ).distinct()
