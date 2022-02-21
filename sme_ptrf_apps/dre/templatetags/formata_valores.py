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


@register.filter(name='formata_valor_vazio')
def formata_valor_vazio(valor):
    # O metodo formata_valor, é usado em diversos PDFs, então para evitar a quebra de alguma regra
    # Este metodo formata_valor_vazio, foi criado

    if int(valor) == 0 or valor == "":
        return "-"
    else:
        if valor:
            try:
                from babel.numbers import format_currency
                sinal, valor_formatado = format_currency(valor, 'BRL', locale='pt_BR').split('\xa0')
                sinal = '-' if '-' in sinal else ''
                return f'{sinal}{valor_formatado}'
            except decimal.InvalidOperation as err:
                LOGGER.error(f'Erro ao converter o valor: {valor} -  {err}')
    return "-"


@register.filter(name='formata_valor_rendimento')
def formata_valor_rendimento(valor):
    if valor:
        try:
            from babel.numbers import format_currency
            sinal, valor_formatado = format_currency(valor, 'BRL', locale='pt_BR').split('\xa0')
            sinal = '-' if '-' in sinal else ''
            return f'{sinal}{valor_formatado}'
        except decimal.InvalidOperation as err:
            LOGGER.error(f'Erro ao converter o valor: {valor} -  {err}')

    return "-"


@register.simple_tag(name='label_status_pc')
def label_status_pc(status_pc):
    _label_status_pc = ""
    if status_pc == "APROVADA":
        _label_status_pc = "Aprovada"
    elif status_pc == "APROVADA_RESSALVA":
        _label_status_pc = "Aprovada com ressalvas"
    elif status_pc == "REPROVADA":
        _label_status_pc = "Rejeitada"

    return _label_status_pc
