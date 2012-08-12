from django import template

register = template.Library()

@register.filter
def lookup(lookupable, key):
    return lookupable[key]
