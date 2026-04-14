import datetime
from decimal import Decimal

import pytest
from model_bakery import baker

from sme_ptrf_apps.core.services.ata_dados_service import devolucoes_ao_tesouro_ata

pytestmark = pytest.mark.django_db


@pytest.fixture
def ata_tipo_devolucao():
    return baker.make('TipoDevolucaoAoTesouro', nome='Devolução por irregularidade')


@pytest.fixture
def ata_apresentacao(associacao, ata_periodo_2020_1):
    return baker.make(
        'Ata',
        associacao=associacao,
        periodo=ata_periodo_2020_1,
        tipo_ata='APRESENTACAO',
        prestacao_conta=None,
    )


@pytest.fixture
def ata_retificacao(associacao, ata_periodo_2020_1, ata_prestacao_conta_2020_1):
    return baker.make(
        'Ata',
        associacao=associacao,
        periodo=ata_periodo_2020_1,
        tipo_ata='RETIFICACAO',
        prestacao_conta=ata_prestacao_conta_2020_1,
    )


@pytest.fixture
def devolucao_ao_tesouro(
    ata_prestacao_conta_2020_1,
    ata_tipo_devolucao,
    ata_despesa_2020_1,
):
    return baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=ata_prestacao_conta_2020_1,
        tipo=ata_tipo_devolucao,
        data=datetime.date(2020, 5, 10),
        despesa=ata_despesa_2020_1,
        valor=200.00,
        motivo='Comprovação inválida',
    )


def test_devolucoes_ao_tesouro_ata_apresentacao_retorna_lista_vazia(
    ata_apresentacao, ata_prestacao_conta_2020_1
):
    resultado = devolucoes_ao_tesouro_ata(ata_apresentacao, ata_prestacao_conta_2020_1)
    assert resultado == []


def test_devolucoes_ao_tesouro_ata_retificacao_sem_devolucoes_retorna_lista_vazia(
    ata_retificacao, ata_prestacao_conta_2020_1
):
    resultado = devolucoes_ao_tesouro_ata(ata_retificacao, ata_prestacao_conta_2020_1)
    assert resultado == []


def test_devolucoes_ao_tesouro_ata_retificacao_com_devolucao(
    ata_retificacao, ata_prestacao_conta_2020_1, devolucao_ao_tesouro, ata_despesa_2020_1
):
    resultado = devolucoes_ao_tesouro_ata(ata_retificacao, ata_prestacao_conta_2020_1)
    assert len(resultado) == 1
    devolucao = resultado[0]
    assert devolucao['tipo'] == 'Devolução por irregularidade'
    assert devolucao['data'] == '10/05/2020'
    assert devolucao['numero_documento'] == ata_despesa_2020_1.numero_documento
    assert devolucao['valor'] == Decimal('200.00')
    assert devolucao['motivo'] == 'Comprovação inválida'


def test_devolucoes_ao_tesouro_ata_retificacao_estrutura_devolucao(
    ata_retificacao, ata_prestacao_conta_2020_1, devolucao_ao_tesouro
):
    resultado = devolucoes_ao_tesouro_ata(ata_retificacao, ata_prestacao_conta_2020_1)
    assert len(resultado) == 1
    chaves = resultado[0].keys()
    assert 'tipo' in chaves
    assert 'data' in chaves
    assert 'numero_documento' in chaves
    assert 'cpf_cnpj_fornecedor' in chaves
    assert 'valor' in chaves
    assert 'motivo' in chaves


def test_devolucoes_ao_tesouro_ata_retificacao_multiplas_devolucoes(
    ata_retificacao,
    ata_prestacao_conta_2020_1,
    ata_tipo_devolucao,
    ata_despesa_2020_1,
):
    baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=ata_prestacao_conta_2020_1,
        tipo=ata_tipo_devolucao,
        data=datetime.date(2020, 4, 1),
        despesa=ata_despesa_2020_1,
        valor=50.00,
        motivo='Motivo 1',
    )
    baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=ata_prestacao_conta_2020_1,
        tipo=ata_tipo_devolucao,
        data=datetime.date(2020, 5, 1),
        despesa=ata_despesa_2020_1,
        valor=75.00,
        motivo='Motivo 2',
    )
    resultado = devolucoes_ao_tesouro_ata(ata_retificacao, ata_prestacao_conta_2020_1)
    assert len(resultado) == 2
