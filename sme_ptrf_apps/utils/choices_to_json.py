from typing import List, Dict, Any


def choices_to_json(choices: List[Any]) -> List[Dict[str, Any]]:
    result = []
    for choice in choices:
        choice_dict = {"id": choice[0], "nome": choice[1]}
        result.append(choice_dict)
    return result
