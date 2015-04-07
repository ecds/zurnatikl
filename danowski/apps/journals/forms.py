from django import forms
from danowski.apps.journals.models import Journal, Issue, IssueItem



class JournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = '__all__'
        widgets = {
            'schools': forms.SelectMultiple(attrs={'style': "width:482px",
                                                    'width' : '482px'})
        }


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = '__all__'
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
        fields = '__all__'
        widgets = {
            'addresses': forms.SelectMultiple(attrs={'style': "width:482px",
                                                    'width' : '482px'}),
        }