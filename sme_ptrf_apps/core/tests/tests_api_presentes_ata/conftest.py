import pytest
from datetime import date

from model_bakery import baker


@pytest.fixture
def ata_2020_1_teste(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'Ata',
        arquivo_pdf=None,
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        periodo=prestacao_conta_2020_1_conciliada.periodo,
        associacao=prestacao_conta_2020_1_conciliada.associacao,
        tipo_ata='APRESENTACAO',
        tipo_reuniao='ORDINARIA',
        convocacao='PRIMEIRA',
        status_geracao_pdf='NAO_GERADO',
        data_reuniao=date(2020, 7, 1),
        local_reuniao='Escola Teste',
        presidente_reuniao='José',
        cargo_presidente_reuniao='Presidente',
        secretario_reuniao='Ana',
        cargo_secretaria_reuniao='Secretária',
        comentarios='Teste',
        parecer_conselho='APROVADA',
    )


@pytest.fixture
def presente_ata_membro_arnaldo(ata_2020_1_teste):
    return baker.make(
        'PresenteAta',
        ata=ata_2020_1_teste,
        identificacao="0001",
        nome="Arnaldo",
        cargo="Presidente",
        membro=True,
        conselho_fiscal=False
    )


@pytest.fixture
def presente_ata_membro_e_conselho_fiscal_benedito(ata_2020_1_teste):
    return baker.make(
        'PresenteAta',
        ata=ata_2020_1_teste,
        identificacao="0002",
        nome="Benedito",
        cargo="Secretario",
        membro=True,
        conselho_fiscal=True
    )

@pytest.fixture
def presente_ata_nao_membro_carlos(ata_2020_1_teste):
    return baker.make(
        'PresenteAta',
        ata=ata_2020_1_teste,
        identificacao="0003",
        nome="Carlos",
        cargo="Auxiliar",
        membro=False,
        conselho_fiscal=False
    )

