from django import forms
from danowski.apps.networks.models import Person, Journal, Issue, IssueItem, School

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person

        widgets = {
            'dwelling': forms.SelectMultiple(attrs={'style': "width:482px",
                                                    'width' : '482px'}),
            'schools': forms.SelectMultiple(attrs={'style': "width:482px",
                                                    'width' : '482px'})
        }

class JournalForm(forms.ModelForm):
    class Meta:
        model = Journal

        widgets = {
            'schools': forms.SelectMultiple(attrs={'style': "width:482px",
                                                    'width' : '482px'})
        }


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue

        widgets = {
            'print_address': forms.Select(attrs={'style': "width:482px",
                                                    'width' : '482px'}),
            'mailing_addresses': forms.SelectMultiple(attrs={'style': "width:482px",
                                                    'width' : '482px'}),
            'publication_address': forms.Select(attrs={'style': "width:482px",
                                                    'width' : '482px'})
        }


class IssueItemForm(forms.ModelForm):
    class Meta:
        model = IssueItem

        widgets = {
            'addresses': forms.Select(attrs={'style': "width:482px",
                                                    'width' : '482px'}),
        }

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School

        widgets = {
            'location': forms.Select(attrs={'style': "width:482px",
                                                    'width' : '482px'}),
        }