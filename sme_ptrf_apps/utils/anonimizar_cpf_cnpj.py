"""
Utilitário para anonimização de CPF/CNPJ do fornecedor nas extrações de dados.

Padrão: exibir apenas os 3 primeiros e os 2 últimos dígitos, ocultando os demais.
Exemplo CPF: 12345678901 -> 123XXXXXX45
Exemplo CNPJ: 12345678000199 -> 123XXXXXXXXX99
"""


def anonimizar_cpf_cnpj_fornecedor(valor):
    """
    Anonimiza CPF ou CNPJ para exibição nas extrações de dados.

    - CPF (11 dígitos): 3 primeiros + XXXXXX + 2 últimos (ex: 123XXXXXX45)
    - CNPJ (14 dígitos): 3 primeiros + 9 X + 2 últimos (ex: 123XXXXXXXXX99)
    - Valores vazios ou com quantidade de dígitos diferente de 11 ou 14: retorna o valor original.

    :param valor: string com CPF ou CNPJ (pode conter formatação . - /)
    :return: string anonimizada ou valor original se não for CPF/CNPJ válido
    """
    if valor is None or not isinstance(valor, str):
        return valor if valor is not None else ""

    apenas_digitos = "".join(c for c in valor if c.isdigit())

    if len(apenas_digitos) == 11:
        # CPF: 3 primeiros + 6 ocultos + 2 últimos
        return f"{apenas_digitos[:3]}XXXXXX{apenas_digitos[-2:]}"
    if len(apenas_digitos) == 14:
        # CNPJ: 3 primeiros + 9 ocultos + 2 últimos
        return f"{apenas_digitos[:3]}{'X' * 9}{apenas_digitos[-2:]}"

    return valor
