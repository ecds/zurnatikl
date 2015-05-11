from django.db.models import Q
from ajax_select import LookupChannel
from danowski.apps.geo.models import Location


class LocationLookup(LookupChannel):
    '''Custom :class:`~danowski.apps.geo.models.Location` lookup
    for ajax autocompletion on edit forms.  Searches on
    street address, city, state name, and country name (case-insensitive,
    partial matching).'''

    model = Location

    help_text = 'Enter text to search for and add locations.  Searches ' + \
            'on any one of street address, city, state, or country.'

    def get_query(self, q, request):
        return Location.objects.filter(
                Q(street_address__icontains=q) |
                Q(city__icontains=q) |
                Q(state__name__icontains=q) |
                Q(country__name__icontains=q))

        # not sure what would be meaningful to sort on,
        # since so many of these fields are optional
