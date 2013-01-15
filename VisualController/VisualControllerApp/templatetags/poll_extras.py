import numpy

__author__ = 'pita'

from django import template

register = template.Library()

@register.filter
def mean(value):
    return numpy.mean(value)

@register.filter
def std(value):
    return numpy.std(value)