from django import template

import logging

register = template.Library()

LOGGER = logging.getLogger(__name__)


@register.filter(name='capitaliza_string')
def capitaliza_string(string):
    if string:
        return string.capitalize()
    return ""

