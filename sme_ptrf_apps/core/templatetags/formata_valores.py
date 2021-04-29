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


@register.simple_tag(name='soma_valores')
def soma_todos_numeros_args(*args):
    soma = sum(args)
    return formata_valor(soma)


@register.simple_tag(name='parecer_conselho')
def parecer_conselho(parecer_conselho):
    texto_parecer = ""

    if parecer_conselho == "APROVADA":
        texto_parecer = "Os membros do Conselho Fiscal, à vista dos registros contábeis e verificando nos documentos apresentados a exatidão das despesas realizadas, julgaram exata a presente prestação de contas considerando-a em condições de ser aprovada e emitindo parecer favorável à sua aprovação."
    elif parecer_conselho == "REJEITADA":
        texto_parecer = "Os membros do Conselho Fiscal, à vista dos registros contábeis e verificando nos documentos apresentados, não consideram a presente prestação de contas em condições de ser aprovada emitindo parecer contrário à sua aprovação."

    return texto_parecer
