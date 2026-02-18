"""
Utilitário para anonimização de CPF nas extrações de dados.

Padrão CPF: exibir os 3 primeiros e os 2 últimos caracteres, ocultando os demais.
Aceita formato numérico ou alfanumérico.
Exemplo CPF: 12345678901 -> 123XXXXXX45
Exemplo CNPJ: 12345678000199 -> retornado sem alteração
"""


def anonimizar_cpf(valor):
    """
    Anonimiza apenas CPF para exibição nas extrações de dados. CNPJ é retornado sem alteração.

    - CPF (11 caracteres): anonimiza com 3 primeiros + XXXXXX + 2 últimos (ex: 123XXXXXX45)
    - CNPJ (14 caracteres): retorna o valor original (não anonimiza)
    - Aceita formato numérico ou alfanumérico (apenas dígitos e letras são considerados).
    - Valores vazios ou com quantidade de caracteres diferente de 11 ou 14: retorna o valor original.

    :param valor: string com CPF ou CNPJ (pode conter formatação . - / e caracteres alfanuméricos)
    :return: string anonimizada (só para CPF) ou valor original
    """
    if valor is None or not isinstance(valor, str):
        return valor if valor is not None else ""

    # Aceita dígitos e letras (formato alfanumérico)
    caracteres = "".join(c for c in valor if c.isalnum())

    if len(caracteres) == 11:
        # CPF: anonimizar com 3 primeiros + 6 ocultos + 2 últimos
        return f"{caracteres[:3]}XXXXXX{caracteres[-2:]}"
    if len(caracteres) == 14:
        # CNPJ: não anonimizar
        return valor

    return valor
