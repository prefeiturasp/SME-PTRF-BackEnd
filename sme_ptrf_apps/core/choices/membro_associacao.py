"""
Choices para o modelo MembroAssociacao
"""

from enum import Enum

class RepresentacaoCargo(Enum):
    SERVIDOR = 'Servidor'
    PAI_RESPONSAVEL = 'Pai_ou_responsável'
    ESTUDANTE = 'Estudante'

    @classmethod
    def choices(cls):
        return [(key.name, key.value) for key in cls]


class MembroEnum(Enum):
    PRESIDENTE_DIRETORIA_EXECUTIVA = 'Presidente da diretoria executiva'
    VICE_PRESIDENTE_DIRETORIA_EXECUTIVA = 'Vice-Presidente da diretoria executiva'
    SECRETARIO = 'Secretario'
    TESOUREIRO = 'Tesoureiro'
    VOGAL_1 = 'Vogal 1'
    VOGAL_2 = 'Vogal 2'
    VOGAL_3 = 'Vogal 3'
    VOGAL_4 = 'Vogal 4'
    VOGAL_5 = 'Vogal 5'
    PRESIDENTE_CONSELHO_FISCAL = 'Presidente do conselho fiscal'
    CONSELHEIRO_1 = 'Conselheiro 1'
    CONSELHEIRO_2 = 'Conselheiro 2'
    CONSELHEIRO_3 = 'Conselheiro 3'
    CONSELHEIRO_4 = 'Conselheiro 4'

    @classmethod
    def choices(cls):
        return [(key.name, key.value) for key in cls]
