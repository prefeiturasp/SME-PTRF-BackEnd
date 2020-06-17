def choices_to_json(choices):
    result = []
    for choice in choices:
        choice = {
            'id': choice[0],
            'nome': choice[1]
        }
        result.append(choice)
    return result
