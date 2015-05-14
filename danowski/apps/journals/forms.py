from django import forms
from ajax_select import make_ajax_field

from danowski.apps.geo.lookups import LocationLookup
from danowski.apps.journals.models import Journal, Issue, Item
from danowski.apps.people.lookups import PersonLookup


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
    # ajax autocomplete for person fields
    editors = make_ajax_field(Issue, 'editors', 'person',
        help_text=PersonLookup.help_text)
    contributing_editors = make_ajax_field(Issue, 'contributing_editors', 'person',
        help_text=PersonLookup.help_text)


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = '__all__'

    # ajax autocomplete for locations
    addresses = make_ajax_field(Item, 'addresses', 'location',
        help_text=LocationLookup.help_text)
    # ajax autocomplete for person fields
    translators= make_ajax_field(Item, 'translators', 'person',
        help_text=PersonLookup.help_text)
    persons_mentioned = make_ajax_field(Item, 'persons_mentioned', 'person',
        help_text=PersonLookup.help_text)
