from django import template

register = template.Library()


@register.filter(name='formata_valor')
def formata_valor(valor):
    if valor:
        from babel.numbers import format_currency
        sinal, valor_formatado = format_currency(valor, 'BRL', locale='pt_BR').split('\xa0')
        sinal = '-' if '-' in sinal else ''
        return f'{sinal}{valor_formatado}'
    return "0,00"
