import decimal
import re
import unicodedata

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