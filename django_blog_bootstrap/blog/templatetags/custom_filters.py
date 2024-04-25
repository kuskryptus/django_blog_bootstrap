from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import strip_tags

register = template.Library()


@register.filter(name='plain_text')
def plain_text(value):
    return strip_tags(value)

