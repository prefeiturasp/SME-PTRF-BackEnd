from enum import Enum


class RecursoOpcoesEnum(Enum):
    PTRF = "PTRF"
    PDDE = "PDDE"
    RECURSO_PROPRIO = "Recursos Próprios"

    @classmethod
    def choices(cls):
        return [(key.name, key.value) for key in cls]

    @classmethod
    def to_dict(cls):
        return [dict(key=key.name, value=key.value) for key in cls]


class TipoAplicacaoOpcoesEnum(Enum):
    CUSTEIO = "Custeio"
    CAPITAL = "Capital"

    @classmethod
    def choices(cls):
        return [(key.name, key.value) for key in cls]

    @classmethod
    def to_dict(cls):
        return [dict(key=key.name, value=key.value) for key in cls]
