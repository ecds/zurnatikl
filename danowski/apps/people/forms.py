from django import forms
from ajax_select import make_ajax_field

from danowski.apps.geo.lookups import LocationLookup
from danowski.apps.people.models import Person, School


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = '__all__'
        # NOTE: schools configured to use horizontal filter in admin

    # ajax autocomplete for locations
    dwelling  = make_ajax_field(Person, 'dwelling', 'location',
        help_text=LocationLookup.help_text)

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = '__all__'

    locations  = make_ajax_field(School, 'locations', 'location',
        help_text=LocationLookup.help_text)