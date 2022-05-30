import decimal

from django import template

import logging

register = template.Library()

LOGGER = logging.getLogger(__name__)


@register.simple_tag
def divide_lista_por_numero_de_corte(lista, numero_de_corte):
    print(f"XXXXXXXXXXXXX Numero de corte {numero_de_corte}")
    print(f"XXXXXXXXXXXXX Tamanho Lista {len(lista)}")
    return lista
