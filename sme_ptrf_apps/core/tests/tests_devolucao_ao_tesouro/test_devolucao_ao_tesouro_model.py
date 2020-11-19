import pytest
from datetime import date
from django.contrib import admin
from model_bakery import baker

from ...models import PrestacaoConta, DevolucaoAoTesouro, TipoDevolucaoAoTesouro
from ....despesas.models import Despesa

pytestmark = pytest.mark.django_db

@pytest.fixture
def despesa(associacao, tipo_documento, tipo_transacao):
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
def tipo_devolucao_ao_tesouro():
    return baker.make('TipoDevolucaoAoTesouro', nome='Teste')


@pytest.fixture
def devolucao_ao_tesouro(prestacao_conta_2020_1_conciliada, tipo_devolucao_ao_tesouro, despesa):
    return baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        tipo=tipo_devolucao_ao_tesouro,
        data=date(2020, 7, 1),
        despesa=despesa,
        devolucao_total=True,
        valor=100.00,
        motivo='teste',
        visao_criacao='DRE'
    )


def test_instance_model(devolucao_ao_tesouro):
    model = devolucao_ao_tesouro
    assert isinstance(model, DevolucaoAoTesouro)
    assert isinstance(model.prestacao_conta, PrestacaoConta)
    assert isinstance(model.tipo, TipoDevolucaoAoTesouro)
    assert isinstance(model.despesa, Despesa)
    assert model.data
    assert model.devolucao_total
    assert model.valor
    assert model.motivo
    assert model.visao_criacao


def test_srt_model(devolucao_ao_tesouro):
    assert devolucao_ao_tesouro.__str__() == '2020-07-01 - Teste'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[DevolucaoAoTesouro]
