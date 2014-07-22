from django.contrib import admin
from danowski.apps.people.models import School, Person, Name, PenName
from danowski.apps.people.forms import PersonForm, SchoolForm

class SchoolAdmin(admin.ModelAdmin):
    form = SchoolForm
    list_display = ['name', 'categorizer', 'location']
    search_fields = ['name', 'categorizer', 'notes']
admin.site.register(School, SchoolAdmin)


class AltNamesInline(admin.TabularInline):
    model = Name
    verbose_name_plural = 'Alternate Names'
    extra = 1

class PenNamesInline(admin.TabularInline):
    model = PenName
    verbose_name_plural = 'Pen Names'
    extra = 1

class PersonAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'race', 'gender', 'uri']
    search_fields = ['first_name', 'last_name', 'race', 'gender', 'notes', 'uri', 'racial_self_description']
    list_display_links = ['first_name', 'last_name']
    inlines = [
        AltNamesInline,
        PenNamesInline
    ]
    form = PersonForm
admin.site.register(Person, PersonAdmin)
