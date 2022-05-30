from django import template

import logging

register = template.Library()

LOGGER = logging.getLogger(__name__)


@register.simple_tag
def divide_lista_por_numero_de_corte(conta, numero_de_corte):
    contador = 0

    # Split a Python List into Chunks using For Loops
    our_list = conta['info']
    chunked_list = list()
    chunk_size = numero_de_corte

    # Acescentado ordem a todos os itens
    for index, item in enumerate(our_list):
        contador = contador + 1
        item['ordem'] = contador

    # Separando lista pelo numero de corte
    for i in range(0, len(our_list), chunk_size):
        chunked_list.append(our_list[i:i + chunk_size])

    return chunked_list
