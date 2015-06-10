from django import template

register = template.Library()

@register.filter
def mysafe(value):
    print " ========= mysafe: ================ "
    print value
    print "===================================="
    return value
mysafe.is_safe = True

@register.filter
def mytype(value):
    print " ========= mytype: ================ "
    print value
    print "===================================="
    return type(value)
mysafe.is_safe = False

@register.filter
def mystr(value):
    return str(value)
mysafe.is_safe = True

@register.filter
def mydir(value):
    #return "{0}\n{1}".format(type(value), dir(value))
    return "%s\n%s" % (type(value), dir(value))
mysafe.is_safe = True


