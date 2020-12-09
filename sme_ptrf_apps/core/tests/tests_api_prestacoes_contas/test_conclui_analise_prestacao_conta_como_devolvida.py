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
def test_api_conclui_analise_prestacao_conta_devolvida(jwt_authenticated_client_a, prestacao_conta_em_analise,
                                                       conta_associacao, despesa, tipo_devolucao_ao_tesouro):
    payload = {
        'devolucao_tesouro': True,
        'analises_de_conta_da_prestacao': [
            {
                'conta_associacao': f'{conta_associacao.uuid}',
                'data_extrato': '2020-07-01',
                'saldo_extrato': 100.00,
            },
        ],
        'resultado_analise': PrestacaoConta.STATUS_DEVOLVIDA,
        'data_limite_ue': '2020-07-21',
        'devolucoes_ao_tesouro_da_prestacao': [
            {
                'data': '2020-07-01',
                'devolucao_total': True,
                'motivo': 'teste',
                'valor': 100.00,
                'tipo': f'{tipo_devolucao_ao_tesouro.uuid}',
                'despesa': f'{despesa.uuid}',
                'visao_criacao': 'UE',
            }
        ]
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_em_analise.uuid}/concluir-analise/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_em_analise.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_DEVOLVIDA, 'Status deveria ter passado para APROVADA_RESSALVA.'
    assert prestacao_atualizada.devolucoes_da_prestacao.exists(), 'Não gravou o registro de devolução da PC.'
    assert prestacao_atualizada.devolucoes_da_prestacao.first().data_limite_ue == date(2020, 7,
                                                                                       21), 'Não gravou a data limite.'
    assert prestacao_atualizada.devolucoes_ao_tesouro_da_prestacao.exists(), 'Não gravou as devoluções ao tesouro'

def test_api_conclui_analise_prestacao_conta_aprovada_ressalva_exige_data_limite(jwt_authenticated_client_a,
                                                                                 prestacao_conta_em_analise,
                                                                                 conta_associacao):
    payload = {
        'devolucao_tesouro': True,
        'analises_de_conta_da_prestacao': [
            {
                'conta_associacao': f'{conta_associacao.uuid}',
                'data_extrato': '2020-07-01',
                'saldo_extrato': 100.00,
            },
        ],
        'resultado_analise': PrestacaoConta.STATUS_DEVOLVIDA,
    }
    url = f'/api/prestacoes-contas/{prestacao_conta_em_analise.uuid}/concluir-analise/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_em_analise.uuid}',
        'erro': 'falta_de_informacoes',
        'operacao': 'concluir-analise',
        'mensagem': 'Para concluir como DEVOLVIDA é necessário informar o campo data_limite_ue.'
    }

    assert result == result_esperado, "Deveria ter retornado erro falta_de_informacoes."
