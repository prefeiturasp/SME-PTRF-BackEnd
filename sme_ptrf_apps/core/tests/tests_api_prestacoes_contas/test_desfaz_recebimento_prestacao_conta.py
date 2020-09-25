import json
import pytest

from datetime import date

from model_bakery import baker
from rest_framework import status

from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db


@pytest.fixture
def _prestacao_conta_recebida(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        data_ultima_analise=date(2020, 10, 1),
        status=PrestacaoConta.STATUS_RECEBIDA
    )


def test_api_recebe_prestacao_conta(client, _prestacao_conta_recebida):
    url = f'/api/prestacoes-contas/{_prestacao_conta_recebida.uuid}/desfazer-recebimento/'

    response = client.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    prestacao_atualizada = PrestacaoConta.by_uuid(_prestacao_conta_recebida.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_NAO_RECEBIDA, 'Status não atualizado para NAO_RECEBIDA.'
    assert not prestacao_atualizada.data_recebimento, 'Data de recebimento não foi apagada.'


@pytest.fixture
def _prestacao_conta_em_analise(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        data_ultima_analise=date(2020, 10, 1),
        status=PrestacaoConta.STATUS_EM_ANALISE
    )


def test_api_recebe_prestacao_conta_erro_se_nao_recebida(client, _prestacao_conta_em_analise):
    url = f'/api/prestacoes-contas/{_prestacao_conta_em_analise.uuid}/desfazer-recebimento/'

    response = client.patch(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{_prestacao_conta_em_analise.uuid}',
        'erro': 'status_nao_permite_operacao',
        'status': _prestacao_conta_em_analise.status,
        'operacao': 'desfazer-recebimento',
        'mensagem': 'Impossível desfazer recebimento de uma PC com status diferente de RECEBIDA.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == result_esperado

    prestacao_atualizada = PrestacaoConta.by_uuid(_prestacao_conta_em_analise.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_EM_ANALISE, 'Status não deveria ter sido alterado.'
    assert prestacao_atualizada.data_recebimento, 'Data de recebimento não deveria ter sido apagada.'
