# custom template filters for displaying
# journal contents

from django import template

register = template.Library()

@register.filter
def readable_list(terms, attr=None):
    '''Generate a human-readable list separating items with commas and using
    "and" for the last term.  Returns unicode of terms or attribute if
    specified.'''
    def display_term(term):
        if attr:
            return getattr(term, attr)
        else:
            return unicode(term)

    try:
        # empty list - return empty string
        if len(terms) < 1:
            return ''
        # one item: return or unicode requested attribute
        if len(terms) == 1:
            return display_term(terms[0])
        # two exactly: a and b
        if len(terms) == 2:
            return ' and '.join(display_term(t) for t in terms)
        # more than two: a, b, and c
        # comma separate all, with an "and" before the last term
        last_term = terms[len(terms) - 1]
        # find last term by length because querysets don't support negadive indexing
        return ', '.join(['and %s' % display_term(t) if t == last_term else display_term(t)
                         for t in terms])
    except TypeError:
        # if terms is not a list, fail silently
        pass

@register.filter
def all_except(terms, exception):
    'Filter a list, returning all items but the one specified.'
    try:
        return [t for t in terms if t != exception]
    except TypeError:
        pass