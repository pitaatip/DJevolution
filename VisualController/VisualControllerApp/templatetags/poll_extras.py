import numpy

__author__ = 'pita'

from django import template

register = template.Library()

@register.filter
def mean(value):
    return numpy.mean(value)


@register.filter
def sort_comp(value):
    return sorted(value, key=lambda x: x.created_on, reverse=True)

@register.filter
def std(value):
    return numpy.std(value)