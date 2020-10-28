import json
import pytest

from freezegun import freeze_time
from datetime import date

from model_bakery import baker
from rest_framework import status

from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db


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


@freeze_time('2020-09-01')
def test_api_salva_devolucoes_ao_tesouro(jwt_authenticated_client, prestacao_conta_em_analise, conta_associacao,
                                           tipo_devolucao_ao_tesouro, despesa):
    payload = {
        'devolucoes_ao_tesouro_da_prestacao': [
            {
                'data': '2020-07-01',
                'devolucao_total': True,
                'motivo': 'teste',
                'valor': 100.00,
                'tipo': f'{tipo_devolucao_ao_tesouro.uuid}',
                'despesa': f'{despesa.uuid}'
            }
        ]
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_em_analise.uuid}/salvar-devolucoes-ao-tesouro/'

    response = jwt_authenticated_client.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_em_analise.uuid)
    assert prestacao_atualizada.devolucoes_ao_tesouro_da_prestacao.exists(), 'Não gravou as devoluções ao tesouro'

def test_api_salvar_devolucoes_ao_tesouro_exige_devolucao_tesouro(jwt_authenticated_client, prestacao_conta_em_analise):
    url = f'/api/prestacoes-contas/{prestacao_conta_em_analise.uuid}/salvar-devolucoes-ao-tesouro/'

    response = jwt_authenticated_client.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_em_analise.uuid}',
        'erro': 'falta_de_informacoes',
        'operacao': 'salvar-devolucoes-ao-tesouro',
        'mensagem': 'Faltou informar o campo devolucoes_ao_tesouro_da_prestacao.'
    }

    assert result == result_esperado, "Deveria ter retornado erro falta_de_informacoes."
