import json
import pytest

from datetime import date

from model_bakery import baker
from rest_framework import status

from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db


@pytest.fixture
def prestacao_conta_recebida(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        status=PrestacaoConta.STATUS_RECEBIDA
    )


def test_api_analisar_prestacao_conta(jwt_authenticated_client_a, prestacao_conta_recebida):
    url = f'/api/prestacoes-contas/{prestacao_conta_recebida.uuid}/analisar/'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_recebida.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_EM_ANALISE, 'Status não atualizado.'


def test_api_analisar_prestacao_conta_deve_criar_registro_de_analise(
    jwt_authenticated_client_a,
    prestacao_conta_recebida
):
    url = f'/api/prestacoes-contas/{prestacao_conta_recebida.uuid}/analisar/'

    jwt_authenticated_client_a.patch(url, content_type='application/json')

    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_recebida.uuid)

    assert prestacao_atualizada.analises_da_prestacao.exists(), 'Deveria criar uma análise da prestação.'
    assert (prestacao_atualizada.analise_atual == prestacao_atualizada.analises_da_prestacao.first(),
            'A PC deveria referenciar a análise como análise atual.')


@pytest.fixture
def prestacao_conta_aprovada(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        status=PrestacaoConta.STATUS_APROVADA
    )


def test_api_analisar_prestacao_conta_nao_pode_aceitar_status_diferente_de_recebida(jwt_authenticated_client_a,
                                                                                    prestacao_conta_aprovada):
    url = f'/api/prestacoes-contas/{prestacao_conta_aprovada.uuid}/analisar/'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_aprovada.uuid}',
        'erro': 'status_nao_permite_operacao',
        'status': prestacao_conta_aprovada.status,
        'operacao': 'analisar',
        'mensagem': 'Você não pode analisar uma prestação de contas com status diferente de RECEBIDA.'
    }

    assert result == result_esperado, "Deveria ter retornado erro status_nao_permite_operacao."

    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_aprovada.uuid)
    assert prestacao_atualizada.status == prestacao_conta_aprovada.status, 'Status não deveria ter sido alterado.'
