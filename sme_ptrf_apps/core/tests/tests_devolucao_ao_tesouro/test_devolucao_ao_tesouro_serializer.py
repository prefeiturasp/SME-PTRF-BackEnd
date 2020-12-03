import pytest
from datetime import date
from model_bakery import baker

from ...api.serializers.devolucao_ao_tesouro_serializer import DevolucaoAoTesouroRetrieveSerializer

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


def test_devolucao_ao_tesouro_retrieve_serializer(devolucao_ao_tesouro):
    serializer = DevolucaoAoTesouroRetrieveSerializer(devolucao_ao_tesouro)
    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['prestacao_conta']
    assert serializer.data['tipo']
    assert serializer.data['data']
    assert serializer.data['despesa']
    assert serializer.data['devolucao_total']
    assert serializer.data['valor']
    assert serializer.data['motivo']
    assert serializer.data['visao_criacao']
