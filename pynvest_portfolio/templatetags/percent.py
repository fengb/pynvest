from django import template

register = template.Library()

@register.filter
def percent(num):
    return template.defaultfilters.floatformat(num * 100, 2) + '%'
