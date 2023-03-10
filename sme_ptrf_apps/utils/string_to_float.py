def string_to_float(string):
    """
    Recebe uma string númerica e retorna um número float.

    Exemplos: 
        string_to_float('12,34') -> 12.34
        string_to_float('1.234,56') -> 1234.56
    """
    return float(string.replace('.', '').replace(',','.'))