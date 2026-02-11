from enum import Enum


class TipoCargaPaaEnum(Enum):
    MODELO_PLANO_ANUAL = "Modelo Plano Anual"

    @classmethod
    def choices(cls):
        return [(key.name, key.value) for key in cls]

    @classmethod
    def to_dict(cls):
        return [dict(key=key.name, value=key.value) for key in cls]


class RecursoOpcoesEnum(Enum):
    PTRF = "PTRF"
    PDDE = "PDDE"
    RECURSO_PROPRIO = "Recursos Próprios"
    OUTRO_RECURSO = "Outros Recursos"

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


class TipoAtividadeEstatutariaEnum(Enum):
    ORDINARIA = "Reuniões Ordinárias"
    EXTRAORDINARIA = "Reuniões Extraordinárias"

    @classmethod
    def choices(cls):
        return [(key.name, key.value) for key in cls]

    @classmethod
    def to_dict(cls):
        return [dict(key=key.name, value=key.value) for key in cls]


class PaaStatusEnum(Enum):
    NAO_INICIADO = "Não iniciado"
    EM_ELABORACAO = "Em elaboração"
    GERADO = "Gerado"
    EM_RETIFICACAO = "Em retificação"

    @classmethod
    def choices(cls):
        return [(key.name, key.value) for key in cls]

    @classmethod
    def to_dict(cls):
        return [dict(key=key.name, value=key.value) for key in cls]
