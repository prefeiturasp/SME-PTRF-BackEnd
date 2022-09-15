from django import template

import logging

register = template.Library()

LOGGER = logging.getLogger(__name__)


@register.filter
def retorna_type(value):
    """ It returns variable type as a pure string name """
    return type(value).__name__
