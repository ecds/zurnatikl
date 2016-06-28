from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Image
from zurnatikl.apps.people.models import Person
from zurnatikl.apps.journals.models import Journal, Item, Issue, Genre
from zurnatikl.apps.network.base_views import CsvView


class PeopleCSV(CsvView):
    '''Export person data as CSV'''
    filename = 'people'
    header_row = ['Last Name', 'First Name', 'Associated Schools']

    def get_context_data(self, **kwargs):
        # todo: filter on journal contributors only?
        # additional fields?
        for person in Person.objects.all():
            yield [person.last_name, person.first_name,
                   ', '.join(sch.name for sch in person.schools.all())]


class JournalIssuesCSV(CsvView):
    '''Export journal issue data as CSV'''
    filename = 'journal_issues'
    header_row = ['Journal', 'Volume', 'Issue', 'Publication Date',
                  'Editors', 'Contributing Editors', 'Publication Address',
                  'Print Address', 'Mailing Addresses']

    def get_context_data(self, **kwargs):
        for issue in Issue.objects.all():
            yield [
                issue.journal.title, issue.volume, issue.issue,
                issue.publication_date,
                u', '.join(unicode(ed) for ed in issue.editors.all()),
                u', '.join(unicode(ed) for ed in issue.contributing_editors.all()),
                issue.publication_address, issue.print_address,
                u'; '.join(unicode(loc) for loc in issue.mailing_addresses.all())
            ]


class JournalItemsCSV(CsvView):
    '''Export journal issue item data as CSV'''
    filename = 'journal_items'
    header_row = ['Journal', 'Volume', 'Issue', 'Title', 'No Creator Listed',
                  'Genre', 'Creator Names', 'Persons Mentioned']

    def get_context_data(self, **kwargs):
        for item in Item.objects.all():
            yield [
                item.issue.journal.title, item.issue.volume, item.issue.issue,
                item.title,
                item.no_creator,
                u', '.join(g.name for g in item.genre.all()),
                u', '.join(unicode(p) for p in item.creators.all()),
                u', '.join(unicode(p) for p in item.persons_mentioned.all()),
            ]


class SiteIndex(TemplateView):
    # TODO: move template under content app
    template_name = "site_index.html"

    def get_context_data(self):
        # select 5 random home page images
        images = list(Image.objects.homepage_images().order_by('?')[:4])
        # NOTE: using list to harden the selection to avoid getting a
        # different random set part way through, with possibility of repeating
        return {
            'images': images,
            # provide an alternate banner image to ensure we don't
            # get a repeat with an image on the homepage
            # (overrides the one set by context processor)
            'banner_image': Image.objects.banner_images() \
                                 .exclude(id__in=[img.id for img in images]) \
                                 .order_by('?').first()
        }
