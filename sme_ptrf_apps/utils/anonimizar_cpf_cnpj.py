"""
Utilitário para anonimização de CPF/CNPJ do fornecedor nas extrações de dados.

Padrão: exibir apenas os 3 primeiros e os 2 últimos caracteres, ocultando os demais.
Aceita formato numérico ou alfanumérico (novo formato).
Exemplo CPF: 12345678901 -> 123XXXXXX45
Exemplo CNPJ: 12345678000199 -> 123XXXXXXXXX99
Exemplo alfanumérico (11): ABC12345678 -> ABCXXXXXX78
"""


def anonimizar_cpf_cnpj_fornecedor(valor):
    """
    Anonimiza CPF ou CNPJ para exibição nas extrações de dados.

    - CPF (11 caracteres): 3 primeiros + XXXXXX + 2 últimos (ex: 123XXXXXX45)
    - CNPJ (14 caracteres): 3 primeiros + 9 X + 2 últimos (ex: 123XXXXXXXXX99)
    - Aceita formato numérico ou alfanumérico (apenas dígitos e letras são considerados).
    - Valores vazios ou com quantidade de caracteres diferente de 11 ou 14: retorna o valor original.

    :param valor: string com CPF ou CNPJ (pode conter formatação . - / e caracteres alfanuméricos)
    :return: string anonimizada ou valor original se não for CPF/CNPJ válido
    """
    if valor is None or not isinstance(valor, str):
        return valor if valor is not None else ""

    # Aceita dígitos e letras (formato alfanumérico)
    caracteres = "".join(c for c in valor if c.isalnum())

    if len(caracteres) == 11:
        # CPF: 3 primeiros + 6 ocultos + 2 últimos
        return f"{caracteres[:3]}XXXXXX{caracteres[-2:]}"
    if len(caracteres) == 14:
        # CNPJ: 3 primeiros + 9 ocultos + 2 últimos
        return f"{caracteres[:3]}{'X' * 9}{caracteres[-2:]}"

    return valor
