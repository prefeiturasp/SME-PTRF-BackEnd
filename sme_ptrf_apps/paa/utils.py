from datetime import date
from calendar import monthrange
from typing import List

def ajustar_data_inicial_e_final(data_inicial: date, data_final: date)-> List[date]:
    """
    Ajusta a data inicial e final de um período para o primeiro e último dia do mês, respectivamente.

    :param data_inicial: Data inicial do período.
    :param data_final: Data final do período.
    :return: Lista contendo a data inicial ajustada e a data final ajustada.
    """
    # Ajusta a data inicial para o primeiro dia do mês
    data_inicial_ajustada = date(data_inicial.year, data_inicial.month, 1)

    # Ajusta a data final para o último dia do mês
    ultimo_dia_do_mes = monthrange(data_final.year, data_final.month)[1]
    data_final_ajustada = date(data_final.year, data_final.month, ultimo_dia_do_mes)

    return [data_inicial_ajustada, data_final_ajustada]


def validar_data_final(data_inicial: date, data_final: date) -> bool:
    """
    Valida se a data final é maior ou igual à data inicial.

    :param data_inicial: Data inicial do período.
    :param data_final: Data final do período.
    :return: True se a data final for maior ou igual à data inicial, False caso contrário.
    """
    if data_inicial.month == data_final.month and data_inicial.year == data_final.year:
        return False, "Data final não pode ter o mesmo mês que a data inicial"
    
    return data_final >= data_inicial, "Data final deve ser maior que a data inicial"
