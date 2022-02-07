import unicodedata
from django import template

import logging

register = template.Library()

LOGGER = logging.getLogger(__name__)


@register.simple_tag(name='replace_string_normalizada')
def replace_string_normalizada(string, string_a_ser_removido):

    string = unicodedata.normalize('NFD', string)
    string = string.encode('ascii', 'ignore').decode('utf8').casefold()

    string_a_ser_removido = unicodedata.normalize('NFD', string_a_ser_removido)
    string_a_ser_removido = string_a_ser_removido.encode('ascii', 'ignore').decode('utf8').casefold()

    if string_a_ser_removido in string:
        return string.replace(string_a_ser_removido, '').upper()
    else:
        return string.upper()
