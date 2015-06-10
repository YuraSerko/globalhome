from html_parser import HtmlParser

def full_clean(text):
    parser = HtmlParser(text)
    parser.clean()
    text = parser.get_text()
    del parser
    return text

def clean(text):
    from django.conf import settings
    parser = HtmlParser(text)
    parser.config(allowed_tags=settings.ALLOWED_HTML_TAGS, allowed_attrs=settings.ALLOWED_HTML_ATTRS)
    parser.clean()
    text = parser.get_text()
    del parser
    return text