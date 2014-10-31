from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()

@register.filter
@stringfilter
def splitOutLink(s):
    return s.split('"')[1];
