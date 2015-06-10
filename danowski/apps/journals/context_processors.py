from .forms import SearchForm

# context processor to search form to template context
def search(request):
    return {'search_form': SearchForm()}