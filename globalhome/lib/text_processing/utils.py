# -*- coding: utf-8 -*-
# $Id $

def cut(text, length, end_with=None):
    if len(text) <= length: return text
    text = text.strip()
    text = text[0:length]
    text = [i for i in text] 
    text.reverse()
    for i in range(0,len(text)):
        if text[i] in [' ', '\n', '\t', '\r', '\f', '\v']:
            break;
    text = text[i:len(text)]
    text.reverse()
    text = ''.join(text)
    if end_with:
        text = "%s %s" % (text.strip(), end_with)           
    return text
            