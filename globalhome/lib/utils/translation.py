# -*- coding=utf-8 -*-
# $Id$
# $D$
import os
from pytils.translit import slugify

def filename(s):
    path, fname = os.path.split(s)
    name, ext = os.path.splitext(fname)
    name = slugify(name)
    return os.path.join(path, '%s%s' % (name, ext))