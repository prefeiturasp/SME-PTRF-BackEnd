import datetime

import pytest
from model_bakery import baker

from sme_ptrf_apps.core.services.ata_dados_service import presentes_ata

pytestmark = pytest.mark.django_db


@pytest.fixture
def ata_para_presentes(associacao, ata_periodo_2020_1):
    return baker.make(
        'Ata',
        associacao=associacao,
        periodo=ata_periodo_2020_1,
        tipo_ata='APRESENTACAO',
        prestacao_conta=None,
        data_reuniao=datetime.date(2020, 7, 10),
        hora_reuniao=datetime.time(10, 0),
    )


@pytest.fixture
def participante_membro(ata_para_presentes):
    return baker.make(
        'Participante',
        ata=ata_para_presentes,
        nome='João Presidente',
        cargo='Presidente',
        membro=True,
        conselho_fiscal=False,
    )


@pytest.fixture
def participante_nao_membro(ata_para_presentes):
    return baker.make(
        'Participante',
        ata=ata_para_presentes,
        nome='Maria Visitante',
        cargo='',
        membro=False,
        conselho_fiscal=False,
    )


def test_presentes_ata_estrutura(ata_para_presentes):
    resultado = presentes_ata(ata_para_presentes)
    assert 'presentes_ata_membros' in resultado
    assert 'presentes_ata_nao_membros' in resultado
    assert 'presentes_ata_conselho_fiscal' in resultado


def test_presentes_ata_sem_participantes(ata_para_presentes):
    resultado = presentes_ata(ata_para_presentes)
    assert list(resultado['presentes_ata_membros']) == []
    assert list(resultado['presentes_ata_nao_membros']) == []


def test_presentes_ata_membro_listado(ata_para_presentes, participante_membro):
    resultado = presentes_ata(ata_para_presentes)
    membros = list(resultado['presentes_ata_membros'])
    nomes = [p['nome'] for p in membros]
    assert 'João Presidente' in nomes


def test_presentes_ata_nao_membro_listado(ata_para_presentes, participante_nao_membro):
    resultado = presentes_ata(ata_para_presentes)
    nao_membros = list(resultado['presentes_ata_nao_membros'])
    nomes = [p['nome'] for p in nao_membros]
    assert 'Maria Visitante' in nomes


def test_presentes_ata_membro_nao_aparece_em_nao_membros(
    ata_para_presentes, participante_membro
):
    resultado = presentes_ata(ata_para_presentes)
    nao_membros = list(resultado['presentes_ata_nao_membros'])
    nomes = [p['nome'] for p in nao_membros]
    assert 'João Presidente' not in nomes


def test_presentes_ata_conselho_fiscal_nao_aparece_em_nao_membros(ata_para_presentes):
    baker.make(
        'Participante',
        ata=ata_para_presentes,
        nome='Pedro Conselheiro',
        cargo='Conselheiro',
        membro=False,
        conselho_fiscal=True,
    )
    resultado = presentes_ata(ata_para_presentes)
    nao_membros = list(resultado['presentes_ata_nao_membros'])
    nomes = [p['nome'] for p in nao_membros]
    assert 'Pedro Conselheiro' not in nomes
