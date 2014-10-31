from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()

@register.filter
@stringfilter
def splitOutLink(s):
    str = s.split('"')
    if len(str) == 3
      return s.split('"')[1];
    return s
