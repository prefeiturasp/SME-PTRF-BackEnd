from enum import Enum


class StatusTag(Enum):
    ATIVO = 'Ativo'
    INATIVO = 'Inativo'

    @classmethod
    def choices(cls):
        return [(key.name, key.value) for key in cls]
