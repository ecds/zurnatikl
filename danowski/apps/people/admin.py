from danowski.apps.admin.models import LinkedInline, get_admin_url
from danowski.apps.journals.models import Journal, Issue, IssueItem
from danowski.apps.people.forms import PersonForm, SchoolForm
from danowski.apps.people.models import School, Person, Name, PenName
from django.conf import settings
from django.contrib import admin
from django.utils.safestring import mark_safe 

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

class IssueItemInline(LinkedInline):
    model = IssueItem.persons_mentioned.through
    extra = 0
    verbose_name = 'Mentioned In Issues'
    verbose_name_plural = verbose_name
    admin_model_parent = "journals"
    admin_model_path = "issueitem"

class PersonAdmin(admin.ModelAdmin):
    class Media:
      js = (settings.STATIC_URL + 'js/admin/collapseTabularInlines.js',)
      css = { "all" : (settings.STATIC_URL +"css/admin/admin_styles.css",) }
    list_display = ['first_name', 'last_name', 'race', 'gender', 'uri']
    search_fields = ['first_name', 'last_name', 'race', 'gender', 'notes', 'uri', 'racial_self_description']
    list_display_links = ['first_name', 'last_name']
    inlines = [
        AltNamesInline,
        PenNamesInline,
        IssueItemInline,
    ]
    form = PersonForm

admin.site.register(Person, PersonAdmin)
