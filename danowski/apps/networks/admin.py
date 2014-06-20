from django.contrib import admin
from danowski.apps.networks.models import Location, School, Person, AltName, PenName, Journal, Issue
from danowski.apps.networks.forms import PersonForm, JournalForm, IssueForm


class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'street_address', 'city', 'state', 'zipcode', 'country']
    search_fields = ['street_address', 'city', 'state', 'zipcode', 'country']
    list_display_linksf = ['id']
admin.site.register(Location, LocationAdmin)


class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'categorizer', 'location', 'notes']
    search_fields = ['name', 'categorizer', 'notes']
admin.site.register(School, SchoolAdmin)


class AltNamesInline(admin.TabularInline):
    model = AltName
    verbose_name_plural = 'Alternate Names'
    extra = 1

class PenNamesInline(admin.TabularInline):
    model = PenName
    verbose_name_plural = 'Pen Names'
    extra = 1



class PersonAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'race', 'gender', 'uri']
    search_fields = ['first_name', 'last_name', 'race', 'gender', 'notes', 'uri', 'racial_self_description']
    inlines = [
        AltNamesInline,
        PenNamesInline
    ]
    form = PersonForm
admin.site.register(Person, PersonAdmin)


class JournalAdmin(admin.ModelAdmin):
    list_display = ['title', 'uri', 'publisher', 'issn']
    search_fields = list_display = ['title', 'uri', 'publisher', 'issn', 'notes']
    form = JournalForm
admin.site.register(Journal, JournalAdmin)


class IssueAdmin(admin.ModelAdmin):
     list_display = ['journal', 'volume', 'issue', 'publication_date', 'season', 'physical_description', 'numbered_pages']
     search_fields = list_display = ['journal', 'volume', 'issue', 'physical_description', 'notes']
     form = IssueForm
admin.site.register(Issue, IssueAdmin)