from django import template

import logging

register = template.Library()

LOGGER = logging.getLogger(__name__)


@register.filter
def retorna_quantidade_rowspan(tamanho_lista):
    return str(tamanho_lista * 8)
