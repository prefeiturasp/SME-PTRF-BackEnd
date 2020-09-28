import json
import pytest

from datetime import date

from model_bakery import baker
from rest_framework import status

from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db


@pytest.fixture
def prestacao_conta_nao_recebida(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        status=PrestacaoConta.STATUS_NAO_RECEBIDA
    )


def test_api_recebe_prestacao_conta(client, prestacao_conta_nao_recebida):
    payload = {
        'data_recebimento': '2020-10-01',
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_nao_recebida.uuid}/receber/'

    response = client.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_nao_recebida.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_RECEBIDA, 'Status não atualizado para RECEBIDA.'
    assert prestacao_atualizada.data_recebimento == date(2020, 10, 1), 'Data de recebimento não atualizada.'


def test_api_recebe_prestacao_conta_exige_data_recebimento(client, prestacao_conta_nao_recebida):

    url = f'/api/prestacoes-contas/{prestacao_conta_nao_recebida.uuid}/receber/'

    response = client.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_nao_recebida.uuid}',
        'erro':'falta_de_informacoes',
        'operacao': 'receber',
        'mensagem': 'Faltou informar a data de recebimento da Prestação de Contas.'
    }

    assert result == result_esperado, "Deveria ter retornado erro falta_de_informacoes."

    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_nao_recebida.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_NAO_RECEBIDA, 'Status não deveria ter sido alterado.'


@pytest.fixture
def prestacao_conta_em_analise(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        status=PrestacaoConta.STATUS_EM_ANALISE
    )


def test_api_recebe_prestacao_conta_nao_pode_aceitar_status_diferente_de_nao_recebida(client,
                                                                                      prestacao_conta_em_analise):
    payload = {
        'data_recebimento': '2020-10-01',
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_em_analise.uuid}/receber/'

    response = client.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_em_analise.uuid}',
        'erro':'status_nao_permite_operacao',
        'status': PrestacaoConta.STATUS_EM_ANALISE,
        'operacao': 'receber',
        'mensagem': 'Você não pode receber uma prestação de contas com status diferente de NAO_RECEBIDA.'
    }

    assert result == result_esperado, "Deveria ter retornado erro status_nao_permite_operacao."

    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_em_analise.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_EM_ANALISE, 'Status não deveria ter sido alterado.'
