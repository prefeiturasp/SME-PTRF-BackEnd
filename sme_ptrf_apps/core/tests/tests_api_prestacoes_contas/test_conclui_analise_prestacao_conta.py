import json
import pytest

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


def test_api_conclui_analise_prestacao_conta_exige_resultado_analise(jwt_authenticated_client_a,
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
        ]
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_em_analise.uuid}/concluir-analise/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_em_analise.uuid}',
        'erro': 'falta_de_informacoes',
        'operacao': 'concluir-analise',
        'mensagem': 'Faltou informar o campo resultado_analise.'
    }

    assert result == result_esperado, "Deveria ter retornado erro falta_de_informacoes."


def test_api_conclui_analise_prestacao_conta_exige_analises_de_conta_da_prestacao(jwt_authenticated_client_a,
                                                                                  prestacao_conta_em_analise):
    payload = {
        'devolucao_tesouro': True,
        'resultado_analise': PrestacaoConta.STATUS_APROVADA
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_em_analise.uuid}/concluir-analise/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_em_analise.uuid}',
        'erro': 'falta_de_informacoes',
        'operacao': 'concluir-analise',
        'mensagem': 'Faltou informar o campo analises_de_conta_da_prestacao.'
    }

    assert result == result_esperado, "Deveria ter retornado erro falta_de_informacoes."


@pytest.fixture
def prestacao_conta_recebida(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        status=PrestacaoConta.STATUS_RECEBIDA
    )


def test_api_conclui_analise_prestacao_conta_status_diferente_de_nao_recebida(jwt_authenticated_client_a,
                                                                              prestacao_conta_recebida,
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
        'resultado_analise': PrestacaoConta.STATUS_APROVADA
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_recebida.uuid}/concluir-analise/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_recebida.uuid}',
        'erro': 'status_nao_permite_operacao',
        'status': PrestacaoConta.STATUS_RECEBIDA,
        'operacao': 'concluir-analise',
        'mensagem': 'Você não pode concluir análise de uma prestação de contas com status diferente de EM_ANALISE.'
    }

    assert result == result_esperado, "Deveria ter retornado erro status_nao_permite_operacao."


def test_api_conclui_analise_prestacao_conta_valida_resultado_aanalise(jwt_authenticated_client_a,
                                                                       prestacao_conta_recebida,
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
        'resultado_analise': 'XXX'
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_recebida.uuid}/concluir-analise/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_recebida.uuid}',
        'erro': 'resultado_analise_invalido',
        'status': 'XXX',
        'operacao': 'concluir-analise',
        'mensagem': 'Resultado inválido. Resultados possíveis: APROVADA, APROVADA_RESSALVA, REPROVADA, DEVOLVIDA.'
    }

    assert result == result_esperado, "Deveria ter retornado erro resultado_analise_invalido."
