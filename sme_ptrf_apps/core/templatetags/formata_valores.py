import decimal

from django import template

import logging

register = template.Library()

LOGGER = logging.getLogger(__name__)


@register.filter(name='formata_valor')
def formata_valor(valor):
    if valor:
        try:
            from babel.numbers import format_currency
            sinal, valor_formatado = format_currency(valor, 'BRL', locale='pt_BR').split('\xa0')
            sinal = '-' if '-' in sinal else ''
            return f'{sinal}{valor_formatado}'
        except decimal.InvalidOperation as err:
            LOGGER.error(f'Erro ao converter o valor: {valor} -  {err}')

    return "0,00"
