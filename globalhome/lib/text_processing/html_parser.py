# -*- coding: utf-8 -*-
# $Id $

import re
from textwrap import fill

from BeautifulSoup import BeautifulSoup, Comment, Tag, NavigableString

class HtmlParser(object):
    """
    Clean incoming text from html tags and tag attributes.
    """

    def __init__(self, text, **kwargs):
        if not isinstance(text, basestring):
            text = u''
        self.text = text.strip()
        self.soup = BeautifulSoup(self.text)
        self.allowed_tags = []
        self.allowed_attrs = []
        self.max_word_length = 20

    def config(self, **kwargs):
        if 'allowed_tags' in kwargs: self.allowed_tags = kwargs.get('allowed_tags')
        if 'allowed_attrs' in kwargs: self.allowed_attrs = kwargs.get('allowed_attrs')
        if 'max_word_length' in kwargs: self.max_word_length = kwargs.get('max_word_length', None)
        return self

    def clean_tags(self):
        to_delete = []

        for tag in self.soup.contents:
            self._clean_tag(tag, to_delete)

        for tag in to_delete:
            tag.extract()

        for tag in self.soup.findAll(True):
            if hasattr(tag, 'attrs'):
                tag.attrs = [attr for attr in tag.attrs if attr[0] in self.allowed_attrs]

        self.text = self.soup.__unicode__()

    def _clean_tag(self, tag, to_delete):
        operation = self._check_tag(tag)
        if not operation == 'delete':
            for _tag in tag.contents:
                self._clean_tag(_tag, to_delete)
            if operation == 'delete_safe':
                to_append = []
                for _tag in tag.contents:
                    to_append.append(_tag)
                for _tag in to_append:
                    tag.parent.insert(self._find_position(tag),_tag)
                del to_append
        if operation in ('delete', 'delete_safe'):
            to_delete.append(tag)

    def _find_position(self, tag):
        for i,j in enumerate(tag.parent.contents):
            if j == tag:
                return i
        return 0

    def _check_tag(self, tag):
        if not hasattr(tag, 'contents'):
            tag.contents = []
        if isinstance(tag, Comment):
            return 'delete'
        if isinstance(tag, Tag) and not tag.name in self.allowed_tags:
            return 'delete_safe'
        return 'leave'

    def clean_trash(self):
        self.text = re.sub(r'^(<br type="_moz" />|&#160;|<br />|&nbsp;|\s)*', '', self.text)
        self.text = re.sub(r'&#160;', ' ', self.text)

    def clean_spaces(self):
        reg = re.compile(u'\s{2,}', re.UNICODE)
        self.text = reg.sub('', self.text)

    def clean_max_word_length(self):
        self.text = fill(self.text, self.max_word_length)

    def transform_urls(self):
        """
        Finds all URLs like http://domain/adress/?params
        and replaces it with
        <a href="http://domain/adress/?params">http://domain/adress/?params</a>
        """

        def replace(text):
            """
            Replace URLS
            """
            r1 = r"(\b(http|https)://([-A-Za-z0-9+&@#/%?=~_()|!:,.;]*[-A-Za-z0-9+&@#/%=~_()|]))"
            #r2 = r"((^|\b)www\.([-A-Za-z0-9+&@#/%?=~_()|!:,.;]*[-A-Za-z0-9+&@#/%=~_()|]))"
            #return re.sub(r2,r'<a rel="nofollow" target="_blank" href="http://\1">\1</a>', \
            #    text)
            return re.sub(r1,r'<a rel="nofollow" target="_blank" href="\1">\1</a>',text)

        for tag in self.soup.findAll(text=True):
            if len(tag.findParents(name='a')) == 0:
                tag.replaceWith(NavigableString(replace(unicode(tag))))
        return self.soup.__unicode__()



# TODO: complete this function.
#    def cut(self, *args):
#        """
#        Html-safe cutting the text (get a part of text of defined length, where length of html tags is not included).
#        """
#        length = 0
#        to_delete = []
#        for tag in self.soup.findAll(True):
#            if isinstance(tag, NavigableString):
#                if length + len(tag.__unicode__()) > self.max_word_length:
#                    next = tag.next
#                    while next:
#                        to_delete.append(next)
#                        next = next.next
#
#
#        #start, length = len(args) == 2 and (args[0], args[1]) or (0, args[0])
#        #self.text = self.text[start: start+length]
#        return self

    def get_text(self):
        return self.text

    def clean(self):
        #self.clean_trash()
#        self.clean_max_word_length()
        self.clean_tags()
        self.clean_spaces()
        return self

    def __unicode__(self):
        return unicode(self.text)

    def __str__(self):
        return self.__unicode__()

