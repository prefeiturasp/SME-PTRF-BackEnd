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


@freeze_time('2020-09-01')
def test_api_salva_analise_prestacao_conta(client, prestacao_conta_em_analise, conta_associacao):
    payload = {
        'devolucao_tesouro': True,
        'analises_de_conta_da_prestacao': [
            {
                'conta_associacao': f'{conta_associacao.uuid}',
                'data_extrato': '2020-07-01',
                'saldo_extrato': 100.00,
            },
        ],
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_em_analise.uuid}/salvar-analise/'

    response = client.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_em_analise.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_EM_ANALISE, 'Status deveria ter sido mantido.'
    assert prestacao_atualizada.data_ultima_analise == date(2020, 9, 1), 'Data de última análise não atualizada.'
    assert prestacao_atualizada.devolucao_tesouro, 'Devolução ao tesouro não atualizado.'
    assert prestacao_atualizada.analises_de_conta_da_prestacao.exists(), 'Não gravou a análise de conta'
    assert prestacao_atualizada.analises_de_conta_da_prestacao.first().data_extrato == date(2020, 7,
                                                                                            1), 'Não atualizou a data do extrato.'
    assert prestacao_atualizada.analises_de_conta_da_prestacao.first().saldo_extrato == 100.00, 'Não atualizou a saldo do extrato.'


def test_api_salvar_prestacao_conta_exige_devolucao_tesouro(client, prestacao_conta_em_analise):
    url = f'/api/prestacoes-contas/{prestacao_conta_em_analise.uuid}/salvar-analise/'

    response = client.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_em_analise.uuid}',
        'erro': 'falta_de_informacoes',
        'operacao': 'salvar-analise',
        'mensagem': 'Faltou informar o campo devolucao_tesouro.'
    }

    assert result == result_esperado, "Deveria ter retornado erro falta_de_informacoes."


def test_api_salvar_prestacao_conta_exige_analises_de_conta_da_prestacao(client, prestacao_conta_em_analise):
    payload = {
        'devolucao_tesouro': True,
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_em_analise.uuid}/salvar-analise/'

    response = client.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_em_analise.uuid}',
        'erro': 'falta_de_informacoes',
        'operacao': 'salvar-analise',
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

def test_api_salva_analise_prestacao_conta_nao_pode_aceitar_status_diferente_de_nao_recebida(client,
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
    }
    url = f'/api/prestacoes-contas/{prestacao_conta_recebida.uuid}/salvar-analise/'

    response = client.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_recebida.uuid}',
        'erro': 'status_nao_permite_operacao',
        'status': PrestacaoConta.STATUS_RECEBIDA,
        'operacao': 'salvar-analise',
        'mensagem': 'Você não pode salvar análise de uma prestação de contas com status diferente de EM_ANALISE.'
    }

    assert result == result_esperado, "Deveria ter retornado erro status_nao_permite_operacao."
