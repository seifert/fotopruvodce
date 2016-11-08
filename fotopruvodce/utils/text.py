
import html2text
import markdown2

from pygments.lexers import guess_lexer, ClassNotFound

from django.utils.html import escape, strip_tags
from django.utils.safestring import mark_safe


def raw_text_to_html(raw_text):
    try:
        lexer = guess_lexer(raw_text)
    except ClassNotFound:
        lexer_name = ''
    else:
        lexer_name = lexer.name

    if lexer_name in ('XML', 'HTML'):
        text = html2text.html2text(raw_text)
    else:
        text = escape(strip_tags(raw_text))

    return mark_safe(markdown2.markdown(text))
