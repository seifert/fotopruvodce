
from django import template

from fotopruvodce.utils.text import raw_text_to_html

register = template.Library()

register.filter('raw_text_to_html', raw_text_to_html)


@register.filter
def startswith(s, prefix):
    return s.startswith(prefix)
