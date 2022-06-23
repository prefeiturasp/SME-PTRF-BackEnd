

def get_recursive_attr(instance, fields):
    """
    Esse serviço existe para realizar o getattr do python recursivamente.
    Exemplo usando getattr -> getattr(instance, items, default),
    no getattr se pode passar apenas um campo, já no get_recursive_attr se pode
    passar multiplos campos.

    Exemplo: get_recursive_attr(instance, items__subitems, default).
    """
    if fields and isinstance(fields, str):
        fields = fields.split('__')

    field = getattr(instance, fields.pop(0))

    if fields and field:
        return get_recursive_attr(field, fields)

    return field
