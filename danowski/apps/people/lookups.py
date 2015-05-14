import re
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.html import escape
from django.template.defaultfilters import pluralize
from ajax_select import LookupChannel
from danowski.apps.people.models import Person


class PersonLookup(LookupChannel):
    '''Custom :class:`~danowski.apps.people.models.Person` lookup
    for ajax autocompletion on edit forms.  Searches on
    street address, city, state name, and country name (case-insensitive,
    partial matching).'''

    model = Person

    help_text = 'Enter text to search for and add people.  Searches ' + \
            'on any one of last or first name, last or first alternate name,' + \
            ' or pen name.'

    def get_query(self, q, request):
        # NOTE: could configure mysql full-text indexing to allow using
        # a search filter

        # split the query into words (on spaces or comma space)
        # and match any field on any word
        words = re.split(',? +', q)
        people = Person.objects.all().order_by('last_name').distinct()
        # distinct required in case a term matches multiple names

        for w in words:
            people = people.filter(
                Q(first_name__icontains=w) |
                Q(last_name__icontains=w) |
                Q(name__first_name__icontains=w) |
                Q(name__last_name__icontains=w) |
                Q(penname__name__icontains=w))

        return people


    def name_info(self, obj):
        # formatted name info for display in match & item display
        names = {
            # main name
            'name': escape(unicode(obj)),  # lastname, first or just lastname
            # alternate names
            'alt_names': '; '.join(escape(unicode(n)) for n in obj.name_set.all()),
            # pen names
            'pennames': '; '.join(escape(unicode(n)) for n in obj.penname_set.all()),
        }
        return names

    def format_match(self, obj):
        """HTML formatted item for display in the dropdown """
        name_info = self.name_info(obj)
        name_info['break'] = name_info['btw'] = ''
        if name_info['alt_names'] or name_info['pennames']:
            name_info['break'] = '<br/>'
        if name_info['alt_names'] and name_info['pennames']:
            name_info['btw'] = '; '
        # NOTE: using bold to help differentiate name from alternate names
        return u'''<div>
           <b>%(name)s</b> %(break)s
           <span class="small">%(alt_names)s%(btw)s%(pennames)s</span>
           </div>''' % name_info


    def format_item_display(self, obj):
        """HTML formatted item for display in the selected area"""
        names = self.name_info(obj)
        formatted_names = {
            'name': names['name'],
            'alt_names': '<i>Alternate names:</i> %(alt_names)s' % names
                          if names['alt_names'] else '',
            'pennames': '<i>Pen names:</i> %(pennames)s' % names
                         if names['pennames'] else '',
            'url': reverse('admin:people_person_change', args=[obj.pk])
        }
        formatted_names['break'] = formatted_names['btw'] = ''
        if formatted_names['alt_names'] or formatted_names['pennames']:
            formatted_names['break'] = '<br/>'
        if formatted_names['alt_names'] and formatted_names['pennames']:
            formatted_names['btw'] = '; '

        return u'''<div>
           <b>%(name)s</b>
           <a href="%(url)s"><span class="glyphicon glyphicon-edit"></span></a>
           %(break)s<span class="small">%(alt_names)s%(btw)s%(pennames)s</span>
           </div>''' % formatted_names
