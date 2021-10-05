import json
import pytest

from datetime import date

from model_bakery import baker
from rest_framework import status

from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db


@pytest.fixture
def _prestacao_conta_recebida_apos_acertos(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        data_ultima_analise=date(2020, 10, 1),
        status=PrestacaoConta.STATUS_DEVOLVIDA_RECEBIDA
    )


def test_api_desfaz_recebimento_prestacao_conta_apos_acertos(
    jwt_authenticated_client_a,
    _prestacao_conta_recebida_apos_acertos
):
    url = f'/api/prestacoes-contas/{_prestacao_conta_recebida_apos_acertos.uuid}/desfazer-recebimento-apos-acertos/'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    prestacao_atualizada = PrestacaoConta.by_uuid(_prestacao_conta_recebida_apos_acertos.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_DEVOLVIDA_RETORNADA, 'Status não atualizado.'
    assert not prestacao_atualizada.data_recebimento_apos_acertos, 'Data de recebimento após acertos não foi apagada.'


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


def test_api_desfaz_recebimento_prestacao_conta_apos_acerto_erro_se_nao_retornana_apos_acerto(
    jwt_authenticated_client_a,
    _prestacao_conta_em_analise
):
    url = f'/api/prestacoes-contas/{_prestacao_conta_em_analise.uuid}/desfazer-recebimento-apos-acertos/'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{_prestacao_conta_em_analise.uuid}',
        'erro': 'status_nao_permite_operacao',
        'status': _prestacao_conta_em_analise.status,
        'operacao': 'desfazer-recebimento-apos-acertos',
        'mensagem': 'Impossível desfazer recebimento após acertos de uma PC com status diferente de DEVOLVIDA_RECEBIDA.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == result_esperado

    prestacao_atualizada = PrestacaoConta.by_uuid(_prestacao_conta_em_analise.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_EM_ANALISE, 'Status não deveria ter sido alterado.'
    assert prestacao_atualizada.data_recebimento, 'Data de recebimento não deveria ter sido apagada.'
