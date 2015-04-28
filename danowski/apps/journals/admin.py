from django.contrib import admin
from danowski.apps.journals.models import Journal, Issue, IssueItem, \
  CreatorName, Genre, PlaceName
from danowski.apps.journals.forms import JournalForm, IssueForm, IssueItemForm


class PlaceNamesInline(admin.TabularInline):
    model = PlaceName
    verbose_name_plural = 'Places Mentioned'
    extra = 1


class JournalAdmin(admin.ModelAdmin):
    list_display = ['title', 'uri', 'publisher', 'issn']
    search_fields = list_display = ['title', 'uri', 'publisher', 'issn',
       'notes']
    filter_horizontal = ('schools', )
    form = JournalForm
admin.site.register(Journal, JournalAdmin)


class IssueAdmin(admin.ModelAdmin):
    list_display = ['journal', 'volume', 'issue', 'publication_date',
        'season', 'physical_description', 'numbered_pages']
    search_fields = list_display = ['journal', 'volume', 'issue',
        'physical_description', 'notes']
    list_filter = ['journal']
    filter_horizontal = ('editors', 'contributing_editors',
        'mailing_addresses')
    form = IssueForm
admin.site.register(Issue, IssueAdmin)

class CreatorNameInline(admin.TabularInline):
    model = CreatorName
    extra = 1

admin.site.register(Genre)


class IssueItemAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/admin/collapseTabularInlines.js',)
        css = { 'all' : ('css/admin/admin_styles.css',) }
    form = IssueItemForm
    list_display = ['title', 'issue', 'start_page', 'end_page']
    search_fields = ['title', 'notes']
    list_filter = ['issue__journal']
    filter_horizontal = ('creators', 'translator', 'genre',
        'persons_mentioned', 'addresses',)
    inlines = [
        CreatorNameInline,
        PlaceNamesInline
    ]
admin.site.register(IssueItem, IssueItemAdmin)
