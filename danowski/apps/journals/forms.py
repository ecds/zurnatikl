from django import forms
from ajax_select import make_ajax_field
from ajax_select.fields import AutoCompleteSelectMultipleField, \
    AutoCompleteSelectField, AutoCompleteSelectWidget, \
    AutoCompleteSelectMultipleWidget


from danowski.apps.geo.lookups import LocationLookup
from danowski.apps.journals.models import Journal, Issue, Item, \
   PlaceName, CreatorName
from danowski.apps.people.lookups import PersonLookup


# common arguments for initializing select widgets, for consistency

# NOTE: currently AutoCompleteSelectMultipleField does *NOT*
# allow for overriding the widget, so these cannot be used on
# many-to-many fields for the moment.
# Disabling placeholder text for now, so that autocomplete
# fields will be consistent.

location_widget_attrs = {
    'channel': 'location',
    'help_text': LocationLookup.help_text,
    'show_help_text': True,
    'attrs': {
        # 'placeholder': 'Start typing to search...',
        'size': 50
    }
}

person_widget_attrs = {
    'channel': 'person',
    'help_text': PersonLookup.help_text,
    'show_help_text': True,
    'attrs': {
        # 'placeholder': 'Start typing to search...',
        'size': 50
    }
}

class JournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = '__all__'
        # NOTE: horizontal filter configured for schools in admin


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = '__all__'

    # ajax autocomplete for locations
    print_address = make_ajax_field(Issue, 'print_address', 'location',
        help_text=LocationLookup.help_text)
    publication_address = make_ajax_field(Issue, 'publication_address', 'location',
        help_text=LocationLookup.help_text)
    mailing_addresses = make_ajax_field(Issue, 'mailing_addresses', 'location',
        help_text=LocationLookup.help_text)
    # publication_address = AutoCompleteSelectField('location', label='Print Address',
    #     widget=AutoCompleteSelectWidget(**location_widget_attrs))
    # publication_address = AutoCompleteSelectField('location', label='Publication Address',
    #     widget=AutoCompleteSelectWidget(**location_widget_attrs))
    # mailing_addresses = AutoCompleteSelectMultipleField('location', label='Mailing Addresses',
    #     widget=AutoCompleteSelectMultipleWidget(**location_widget_attrs))

    # ajax autocomplete for person fields
    editors = make_ajax_field(Issue, 'editors', 'person',
        help_text=PersonLookup.help_text)
    contributing_editors = make_ajax_field(Issue, 'contributing_editors', 'person',
        help_text=PersonLookup.help_text)
    # editors = AutoCompleteSelectMultipleField('person', label='Editors',
    #     widget=AutoCompleteSelectMultipleWidget(**person_widget_attrs))
    # contributing_editors = AutoCompleteSelectMultipleField('person',
    #     label='Contributing Editors',
    #     widget=AutoCompleteSelectMultipleWidget(**person_widget_attrs))


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = '__all__'

    # ajax autocomplete for locations
    addresses = make_ajax_field(Item, 'addresses', 'location',
        help_text=LocationLookup.help_text)
    # addresses = AutoCompleteSelectMultipleField('location', label='Addresses',
    #     widget=AutoCompleteSelectMultipleWidget(**location_widget_attrs))

    # ajax autocomplete for person fields
    translators= make_ajax_field(Item, 'translators', 'person',
        help_text=PersonLookup.help_text)
    persons_mentioned = make_ajax_field(Item, 'persons_mentioned', 'person',
        help_text=PersonLookup.help_text)
    # translators = AutoCompleteSelectMultipleField('person', label='Translators',
    #     widget=AutoCompleteSelectMultipleWidget(**person_widget_attrs))
    # persons_mentioned = AutoCompleteSelectMultipleField('person',
    #     label='Persons Mentioned',
    #     widget=AutoCompleteSelectMultipleWidget(**person_widget_attrs))


class CreatorNameForm(forms.ModelForm):
    class Meta:
        model = CreatorName
        fields = '__all__'

    person = AutoCompleteSelectField('person', label='Person',
        widget=AutoCompleteSelectWidget(**person_widget_attrs))


class PlaceNameForm(forms.ModelForm):
    class Meta:
        model = PlaceName
        fields = ['location', 'name']

    location = AutoCompleteSelectField('location', label='Location',
        widget=AutoCompleteSelectWidget(**location_widget_attrs))


class SearchForm(forms.Form):
    keyword = forms.CharField(label='Search terms',
        help_text='Search by keyword in author name or title',
        required=True,
        error_messages={'required': 'Please enter one or more search terms'})



