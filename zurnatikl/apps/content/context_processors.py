from .models import Image

# context processor to select a random banner image for the header
def banner_image(request):
    return {
        # filter on images selected for banner use,
        # order randomly and pick the first one
        'banner_image': Image.objects.banner_images().order_by('?').first()
    }
