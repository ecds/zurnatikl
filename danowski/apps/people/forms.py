from django import forms
from danowski.apps.people.models import Person, School

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = '__all__'
        widgets = {
            'dwelling': forms.SelectMultiple(attrs={'style': "width:482px",
                                                    'width' : '482px'}),
            'schools': forms.SelectMultiple(attrs={'style': "width:482px",
                                                    'width' : '482px'})
        }

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = '__all__'
        widgets = {
            'location': forms.Select(attrs={'style': "width:482px",
                                                    'width' : '482px'}),
        }