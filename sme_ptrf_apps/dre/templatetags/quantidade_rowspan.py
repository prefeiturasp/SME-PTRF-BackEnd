from django import template

import logging

register = template.Library()

LOGGER = logging.getLogger(__name__)


@register.filter
def retorna_quantidade_rowspan(tamanho_lista):
    return str(tamanho_lista * 8)

@register.filter
def retorna_quantidade_rowspan_retira_sem_valores(lista):
    tamanho_lista = len([i for i in lista if i['exibe_valores']])
    return str(tamanho_lista * 8)
