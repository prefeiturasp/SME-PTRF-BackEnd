import json
import pytest

from datetime import date

from model_bakery import baker
from rest_framework import status
from unittest import mock

from ...models import PrestacaoConta, DevolucaoPrestacaoConta, AnalisePrestacaoConta

pytestmark = pytest.mark.django_db


@pytest.fixture
def prestacao_conta_em_analise(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        status=PrestacaoConta.STATUS_EM_ANALISE,
    )

@pytest.fixture
def devolucao_prestacao(prestacao_conta_em_analise):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_conta_em_analise,
        data=date(2020, 7, 1),
        data_limite_ue=date(2020, 8, 1),
        data_retorno_ue=None
    )

@pytest.fixture
def analise_prestacao_conta_2020_1(prestacao_conta_em_analise, devolucao_prestacao):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_em_analise,
        devolucao_prestacao_conta=devolucao_prestacao
    )


def test_api_conclui_analise_prestacao_conta_exige_resultado_analise(jwt_authenticated_client_a,
                                                                     prestacao_conta_em_analise,
                                                                     conta_associacao):
    payload = {
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

@pytest.mark.django_db
def test_concluir_analise_rollback_quando_devolver_falha_em_devolver(jwt_authenticated_client_a,
                                                         prestacao_conta_em_analise,
                                                         conta_associacao,
                                                         devolucao_prestacao,
                                                         analise_prestacao_conta_2020_1):
    payload = {
        'analises_de_conta_da_prestacao': [],
        'resultado_analise': PrestacaoConta.STATUS_DEVOLVIDA,
        'data_limite_ue': '2025-12-31',
        'motivos_reprovacao': [],
        'outros_motivos_reprovacao': '',
        'motivos_aprovacao_ressalva': [],
        'outros_motivos_aprovacao_ressalva': '',
        'recomendacoes': ''
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_em_analise.uuid}/concluir-analise/'

    status_inicial = prestacao_conta_em_analise.status

    with mock.patch.object(PrestacaoConta, 'devolver', side_effect=Exception("Erro simulado no devolver")):
        with pytest.raises(Exception, match="Erro simulado no devolver"):
            jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    prestacao_conta_em_analise.refresh_from_db()

    assert prestacao_conta_em_analise.status == status_inicial, "Status deveria ter sido revertido ao valor inicial"

@pytest.mark.django_db
def test_concluir_analise_rollback_quando_devolver_falha_em_salvar_analise(jwt_authenticated_client_a,
                                                         prestacao_conta_em_analise,
                                                         conta_associacao,
                                                         devolucao_prestacao,
                                                         analise_prestacao_conta_2020_1):
    payload = {
        'analises_de_conta_da_prestacao': [],
        'resultado_analise': PrestacaoConta.STATUS_DEVOLVIDA,
        'data_limite_ue': '2025-12-31',
        'motivos_reprovacao': [],
        'outros_motivos_reprovacao': '',
        'motivos_aprovacao_ressalva': [],
        'outros_motivos_aprovacao_ressalva': '',
        'recomendacoes': ''
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_em_analise.uuid}/concluir-analise/'

    status_inicial = prestacao_conta_em_analise.status

    with mock.patch.object(PrestacaoConta, 'salvar_analise', side_effect=Exception("Erro simulado no salvar_analise")):
        with pytest.raises(Exception, match="Erro simulado no salvar_analise"):
            jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    prestacao_conta_em_analise.refresh_from_db()

    assert prestacao_conta_em_analise.status == status_inicial, "Status deveria ter sido revertido ao valor inicial"

