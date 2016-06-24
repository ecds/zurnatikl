from django.shortcuts import render
from django.views.generic import TemplateView
from djqscsv import render_to_csv_response
from .models import Image
from zurnatikl.apps.people.models import Person
from zurnatikl.apps.journals.models import Journal, Item, Issue, Genre

def people_csv(request):
    '''Export person data in CSV'''
    qs = Person.objects.all().values('last_name', 'first_name', 'schools__name', 'items_created__title')
    return render_to_csv_response(qs)

def journal_csv(request):
    '''Export journal data in CSV'''
    return True

def genre_csv(request):
    '''Export genre data in CSV'''
    qs = Genre.objects.all().values('name')
    return render_to_csv_response(qs)

def item_csv(request):
    '''Export item data in CSV'''
    return True

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
