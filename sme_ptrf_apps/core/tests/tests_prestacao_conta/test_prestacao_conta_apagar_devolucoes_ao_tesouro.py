import pytest
from datetime import date
from model_bakery import baker

from ...models import DevolucaoAoTesouro


pytestmark = pytest.mark.django_db


@pytest.fixture
def tpcadat_despesa(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=date(2020, 3, 10),
        valor_total=100.00,
    )


@pytest.fixture
def tpcadat_tipo_devolucao_ao_tesouro():
    return baker.make('TipoDevolucaoAoTesouro', nome='Teste')

@pytest.fixture
def tpcadat_devolucao_ao_tesouro_1(prestacao_conta_2020_1_conciliada, tpcadat_tipo_devolucao_ao_tesouro, tpcadat_despesa):
    return baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        tipo=tpcadat_tipo_devolucao_ao_tesouro,
        data=date(2020, 7, 1),
        despesa=tpcadat_despesa,
        devolucao_total=True,
        valor=100.00,
        motivo='teste',
        visao_criacao='DRE'
    )

@pytest.fixture
def tpcadat_devolucao_ao_tesouro_2(prestacao_conta_2020_1_conciliada, tpcadat_tipo_devolucao_ao_tesouro, tpcadat_despesa):
    return baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        tipo=tpcadat_tipo_devolucao_ao_tesouro,
        data=date(2020, 7, 1),
        despesa=tpcadat_despesa,
        devolucao_total=True,
        valor=100.00,
        motivo='teste',
        visao_criacao='DRE'
    )


def test_apagar_devolucoes_ao_tesouro_pode_apagar_uma(
    tpcadat_devolucao_ao_tesouro_1,
    tpcadat_devolucao_ao_tesouro_2,
    prestacao_conta_2020_1_conciliada
):
    assert DevolucaoAoTesouro.objects.count() == 2
    prestacao_conta_2020_1_conciliada.apagar_devolucoes_ao_tesouro([{"uuid": tpcadat_devolucao_ao_tesouro_1.uuid}])
    assert DevolucaoAoTesouro.objects.count() == 1


def test_apagar_devolucoes_ao_tesouro_pode_apagar_varias(
    tpcadat_devolucao_ao_tesouro_1,
    tpcadat_devolucao_ao_tesouro_2,
    prestacao_conta_2020_1_conciliada
):
    assert DevolucaoAoTesouro.objects.count() == 2
    prestacao_conta_2020_1_conciliada.apagar_devolucoes_ao_tesouro([
        {"uuid": tpcadat_devolucao_ao_tesouro_1.uuid},
        {"uuid": tpcadat_devolucao_ao_tesouro_2.uuid},
    ])
    assert DevolucaoAoTesouro.objects.count() == 0

