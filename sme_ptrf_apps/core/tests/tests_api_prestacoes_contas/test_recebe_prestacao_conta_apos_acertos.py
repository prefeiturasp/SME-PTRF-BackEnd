import json
import pytest

from datetime import date

from model_bakery import baker
from rest_framework import status

from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db


@pytest.fixture
def prestacao_conta_retornada_apos_acerto(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        status=PrestacaoConta.STATUS_DEVOLVIDA_RETORNADA
    )


def test_api_recebe_prestacao_conta_apos_acetos(jwt_authenticated_client_a, prestacao_conta_retornada_apos_acerto):
    payload = {
        'data_recebimento_apos_acertos': '2020-10-01',
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_retornada_apos_acerto.uuid}/receber-apos-acertos/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_retornada_apos_acerto.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_DEVOLVIDA_RECEBIDA, 'Status não atualizado para DEVOLVIDA_RECEBIDA.'
    assert prestacao_atualizada.data_recebimento_apos_acertos == date(2020, 10, 1), 'Data de recebimento não atualizada.'


def test_api_recebe_prestacao_conta_apos_acetos_exige_data_recebimento(jwt_authenticated_client_a, prestacao_conta_retornada_apos_acerto):
    url = f'/api/prestacoes-contas/{prestacao_conta_retornada_apos_acerto.uuid}/receber-apos-acertos/'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_retornada_apos_acerto.uuid}',
        'erro': 'falta_de_informacoes',
        'operacao': 'receber-apos-acertos',
        'mensagem': 'Faltou informar a data de recebimento da Prestação de Contas. data_recebimento_apos_acertos'
    }

    assert result == result_esperado, "Deveria ter retornado erro falta_de_informacoes."

    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_retornada_apos_acerto.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_DEVOLVIDA_RETORNADA, 'Status não deveria ter sido alterado.'


@pytest.fixture
def prestacao_conta_devolvidae(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        status=PrestacaoConta.STATUS_DEVOLVIDA
    )


def test_api_recebe_prestacao_conta_apos_acetos_nao_pode_aceitar_status_diferente_de_retornada_apos_acertos(
    jwt_authenticated_client_a,
    prestacao_conta_devolvidae):
    payload = {
        'data_recebimento_apos_acertos': '2020-10-01',
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_devolvidae.uuid}/receber-apos-acertos/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_devolvidae.uuid}',
        'erro': 'status_nao_permite_operacao',
        'status': PrestacaoConta.STATUS_DEVOLVIDA,
        'operacao': 'receber-apos-acertos',
        'mensagem': 'Você não pode receber após acertos uma prestação de contas com status diferente de DEVOLVIDA_RETORNADA.'
    }

    assert result == result_esperado, "Deveria ter retornado erro status_nao_permite_operacao."

    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_devolvidae.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_DEVOLVIDA, 'Status não deveria ter sido alterado.'
