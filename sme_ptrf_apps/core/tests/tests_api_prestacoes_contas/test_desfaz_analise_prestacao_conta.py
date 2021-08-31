import json
import pytest

from datetime import date

from model_bakery import baker
from rest_framework import status

from ...models import PrestacaoConta, AnalisePrestacaoConta

pytestmark = pytest.mark.django_db


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


@pytest.fixture
def _analise_prestacao_conta_em_analise(_prestacao_conta_em_analise,):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=_prestacao_conta_em_analise,
    )


@pytest.fixture
def _prestacao_de_conta_com_analise_atual(_prestacao_conta_em_analise, _analise_prestacao_conta_em_analise):
    _prestacao_conta_em_analise.analise_atual = _analise_prestacao_conta_em_analise
    _prestacao_conta_em_analise.save()
    return _prestacao_conta_em_analise


def test_api_desfaz_analise_prestacao_conta(jwt_authenticated_client_a, _prestacao_de_conta_com_analise_atual, _analise_prestacao_conta_em_analise):
    assert AnalisePrestacaoConta.objects.filter(prestacao_conta=_prestacao_de_conta_com_analise_atual).exists()

    url = f'/api/prestacoes-contas/{_prestacao_de_conta_com_analise_atual.uuid}/desfazer-analise/'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    prestacao_atualizada = PrestacaoConta.by_uuid(_prestacao_de_conta_com_analise_atual.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_RECEBIDA, 'Status não atualizado para RECEBIDA.'
    assert prestacao_atualizada.analise_atual is None
    assert not AnalisePrestacaoConta.objects.filter(prestacao_conta=_prestacao_de_conta_com_analise_atual).exists()


@pytest.fixture
def _prestacao_conta_nao_recebida(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        status=PrestacaoConta.STATUS_NAO_RECEBIDA
    )


def test_api_desfaz_analise_prestacao_conta_erro_se_nao_em_analise(jwt_authenticated_client_a, _prestacao_conta_nao_recebida):
    url = f'/api/prestacoes-contas/{_prestacao_conta_nao_recebida.uuid}/desfazer-analise/'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{_prestacao_conta_nao_recebida.uuid}',
        'erro': 'status_nao_permite_operacao',
        'status': _prestacao_conta_nao_recebida.status,
        'operacao': 'desfazer-analise',
        'mensagem': 'Impossível desfazer análise de uma PC com status diferente de EM_ANALISE.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == result_esperado

    prestacao_atualizada = PrestacaoConta.by_uuid(_prestacao_conta_nao_recebida.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_NAO_RECEBIDA, 'Status não deveria ter sido alterado.'


@pytest.fixture
def _analise_prestacao_conta(_prestacao_conta_em_analise):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=_prestacao_conta_em_analise,
    )


@pytest.fixture
def _prestacao_de_contas_com_analise_corrente(_prestacao_conta_em_analise, _analise_prestacao_conta):
    _prestacao_conta_em_analise.analise_atual = _analise_prestacao_conta
    _prestacao_conta_em_analise.save()
    return _prestacao_conta_em_analise


def test_api_desfaz_analise_prestacao_conta_deve_apagar_registro_de_analise_corrente(
    jwt_authenticated_client_a,
    _prestacao_de_contas_com_analise_corrente
):
    url = f'/api/prestacoes-contas/{_prestacao_de_contas_com_analise_corrente.uuid}/desfazer-analise/'

    jwt_authenticated_client_a.patch(url, content_type='application/json')

    prestacao_atualizada = PrestacaoConta.by_uuid(_prestacao_de_contas_com_analise_corrente.uuid)
    assert not prestacao_atualizada.analises_da_prestacao.exists(), 'Deveria apagar a análise da prestação.'
    assert prestacao_atualizada.analise_atual is None, 'Deveria ter limpado o campo análise atual.'
