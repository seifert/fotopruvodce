from html import parser

import html2text
import markdown
from django.utils.safestring import mark_safe


class HTMLParser(parser.HTMLParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tags = set()

    def handle_startendtag(self, tag, attrs):
        self.tags.add(tag)


def is_html(text):
    parser = HTMLParser()
    parser.feed(text)
    return bool(parser.tags)


def raw_text_to_html(raw_text):
    if is_html(raw_text):
        text = html2text.html2text(raw_text)
    else:
        text = raw_text
    return mark_safe(markdown.markdown(text))
