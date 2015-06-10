from django.contrib import admin
from ajax_select.admin import AjaxSelectAdmin
from ajax_select import make_ajax_form
from ajax_select.fields import autoselect_fields_check_can_add
from django_admin_bootstrapped.admin.models import SortableInline


from danowski.apps.journals.models import Journal, Issue, Item, \
   CreatorName, Genre, PlaceName
from danowski.apps.journals.forms import JournalForm, IssueForm, \
   ItemForm, PlaceNameForm, CreatorNameForm


class PlaceNamesInline(admin.TabularInline):
    model = PlaceName
    verbose_name_plural = 'Places Mentioned'
    extra = 1
    form = PlaceNameForm

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(PlaceNamesInline, self).get_formset(request, obj, **kwargs)
        # required to force ajax_select to check if user can add ajax
        # fields and add the link to the autocomplete widget
        autoselect_fields_check_can_add(formset.form, self.model, request.user)
        return formset


class IssueInline(admin.StackedInline, SortableInline):
    model = Issue
    extra = 0
    fields = ['sort_order']
    # sortable options
    start_collapsed = True
    sortable_field_name = 'sort_order'

    # disallow delete from Journal form
    def has_delete_permission(self, request, obj=None):
        return False

    # disallow adding issues from Journal form
    def has_add_permission(self, request):
        return False


class JournalAdmin(admin.ModelAdmin):
    list_display = ['title', 'uri', 'publisher', 'issn']
    search_fields = list_display = ['title', 'uri', 'publisher', 'issn',
       'notes']
    filter_horizontal = ('schools', )
    inlines = [IssueInline, ]
    form = JournalForm
admin.site.register(Journal, JournalAdmin)


class IssueAdmin(AjaxSelectAdmin):
    list_display = ['journal', 'volume', 'issue', 'publication_date',
        'season', 'physical_description', 'numbered_pages']
    list_display = ['journal', 'volume', 'issue',
        'physical_description', 'notes']
    search_fields = ['journal__title', 'journal__publisher',
        'volume', 'issue', 'physical_description', 'notes']
    list_filter = ['journal']
    filter_horizontal = ('editors', 'contributing_editors',
        'mailing_addresses')
    # don't allow editing sort order on single issue page
    exclude = ['sort_order']
    form = IssueForm
admin.site.register(Issue, IssueAdmin)

class CreatorNameInline(admin.TabularInline):
    model = CreatorName
    extra = 1
    form = CreatorNameForm

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(CreatorNameInline, self).get_formset(request, obj, **kwargs)
        # required to force ajax_select to check if user can add ajax
        # fields and add the link to the autocomplete widget
        autoselect_fields_check_can_add(formset.form, self.model, request.user)
        return formset


admin.site.register(Genre)


class ItemAdmin(AjaxSelectAdmin):
    class Media:
        js = ('js/admin/collapseTabularInlines.js',)
        css = { 'all' : ('css/admin/admin_styles.css',) }
    form = ItemForm
    list_display = ['title', 'issue', 'start_page', 'end_page']
    search_fields = ['title', 'notes']
    list_filter = ['issue__journal']
    filter_horizontal = ('creators', 'translators', 'genre')
    inlines = [
        CreatorNameInline,
        PlaceNamesInline
    ]
admin.site.register(Item, ItemAdmin)
