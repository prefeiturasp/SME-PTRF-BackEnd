def remove_digitos(string):
    """
    Recebe uma steing e retorna a mesma string sem qualquer dígito.

    Exemplo: remove_digitos('teste 123') -> 'teste '
    """
    return ''.join([i for i in string if not i.isdigit()])
