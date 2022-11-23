import json
import pytest

from datetime import date
from model_bakery import baker

from sme_ptrf_apps.core.models import PrestacaoConta

from rest_framework import status

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
def prestacao_conta_em_analise(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        status=PrestacaoConta.STATUS_EM_ANALISE
    )


@pytest.fixture
def tipo_devolucao_ao_tesouro():
    return baker.make('TipoDevolucaoAoTesouro', nome='Teste')


@pytest.fixture
def devolucao_ao_tesouro(prestacao_conta_em_analise, tipo_devolucao_ao_tesouro, despesa):
    return baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=prestacao_conta_em_analise,
        tipo=tipo_devolucao_ao_tesouro,
        data=date(2020, 7, 1),
        despesa=despesa,
        devolucao_total=True,
        valor=100.00,
        motivo='teste',
    )


def test_api_apaga_devolucoes_ao_tesouro(
    jwt_authenticated_client_a,
    prestacao_conta_em_analise,
    conta_associacao,
    devolucao_ao_tesouro
):
    payload = {
        'devolucoes_ao_tesouro_a_apagar': [
            {
                'uuid': f"{devolucao_ao_tesouro.uuid}",
            }
        ]
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_em_analise.uuid}/apagar-devolucoes-ao-tesouro/'

    response = jwt_authenticated_client_a.delete(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
