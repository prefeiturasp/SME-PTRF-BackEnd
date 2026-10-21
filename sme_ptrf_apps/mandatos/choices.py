from django.db import models


class CargoComposicaoVacanciaChoices(models.TextChoices):
    CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA = 'PRESIDENTE_DIRETORIA_EXECUTIVA', 'Presidente da diretoria executiva'  # noqa
    CARGO_ASSOCIACAO_VICE_PRESIDENTE_DIRETORIA_EXECUTIVA = 'VICE_PRESIDENTE_DIRETORIA_EXECUTIVA', 'Vice-Presidente da diretoria executiva'  # noqa
    CARGO_ASSOCIACAO_SECRETARIO = 'SECRETARIO', 'Secretário'
    CARGO_ASSOCIACAO_TESOUREIRO = 'TESOUREIRO', 'Tesoureiro'
    CARGO_ASSOCIACAO_VOGAL_1 = 'VOGAL_1', 'Vogal 1'
    CARGO_ASSOCIACAO_VOGAL_2 = 'VOGAL_2', 'Vogal 2'
    CARGO_ASSOCIACAO_VOGAL_3 = 'VOGAL_3', 'Vogal 3'
    CARGO_ASSOCIACAO_VOGAL_4 = 'VOGAL_4', 'Vogal 4'
    CARGO_ASSOCIACAO_VOGAL_5 = 'VOGAL_5', 'Vogal 5'
    CARGO_ASSOCIACAO_PRESIDENTE_CONSELHO_FISCAL = 'PRESIDENTE_CONSELHO_FISCAL', 'Presidente do conselho fiscal'
    CARGO_ASSOCIACAO_CONSELHEIRO_1 = 'CONSELHEIRO_1', 'Conselheiro 1'
    CARGO_ASSOCIACAO_CONSELHEIRO_2 = 'CONSELHEIRO_2', 'Conselheiro 2'
    CARGO_ASSOCIACAO_CONSELHEIRO_3 = 'CONSELHEIRO_3', 'Conselheiro 3'
    CARGO_ASSOCIACAO_CONSELHEIRO_4 = 'CONSELHEIRO_4', 'Conselheiro 4'

    # Obter o label
    # CargoComposicaoVacanciaChoices(cargo_associacao).label

    # obter como dict
    # dict(CargoComposicaoVacanciaChoices.choices)

    # Obter como tuplas
    # CargoComposicaoVacanciaChoices.choices

    # obtem somente valores
    # CargoComposicaoVacanciaChoices.values

    # Obtem somente labels
    # CargoComposicaoVacanciaChoices.labels

    # Obtem somente nomes
    # CargoComposicaoVacanciaChoices.names
