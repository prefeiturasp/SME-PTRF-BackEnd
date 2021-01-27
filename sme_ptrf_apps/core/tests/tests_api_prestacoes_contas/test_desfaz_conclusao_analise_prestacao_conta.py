import json
import pytest

from datetime import date

from model_bakery import baker
from rest_framework import status

from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db


@pytest.fixture
def _prestacao_conta_em_aprovada_ressalva(periodo, associacao, motivo_aprovacao_ressalva_x):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        data_ultima_analise=date(2020, 10, 1),
        status=PrestacaoConta.STATUS_APROVADA_RESSALVA,
        outros_motivos_aprovacao_ressalva='outros motivos',
        motivos_aprovacao_ressalva=[motivo_aprovacao_ressalva_x, ]
    )


def test_api_desfaz_conclusao_analise_prestacao_conta_aprovada_com_ressalva(jwt_authenticated_client_a, _prestacao_conta_em_aprovada_ressalva):
    url = f'/api/prestacoes-contas/{_prestacao_conta_em_aprovada_ressalva.uuid}/desfazer-conclusao-analise/'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    prestacao_atualizada = PrestacaoConta.by_uuid(_prestacao_conta_em_aprovada_ressalva.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_EM_ANALISE, 'Status não atualizado para EM_ANALISE.'
    assert prestacao_atualizada.outros_motivos_aprovacao_ressalva == '', 'Não limpou outros motivos.'
    assert not prestacao_atualizada.motivos_aprovacao_ressalva.exists(), 'Não limpou motivos de aprovação com ressalva'


@pytest.fixture
def _prestacao_conta_nao_recebida(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        status=PrestacaoConta.STATUS_NAO_RECEBIDA
    )


def test_api_desfaz_analise_prestacao_conta_erro_se_nao_em_analise(jwt_authenticated_client_a, _prestacao_conta_nao_recebida):
    url = f'/api/prestacoes-contas/{_prestacao_conta_nao_recebida.uuid}/desfazer-conclusao-analise/'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{_prestacao_conta_nao_recebida.uuid}',
        'erro': 'status_nao_permite_operacao',
        'status': _prestacao_conta_nao_recebida.status,
        'operacao': 'desfazer-conclusao-analise',
        'mensagem': 'Impossível desfazer conclusão de análise de uma PC com status diferente de APROVADA, APROVADA_RESSALVA ou REPROVADA.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == result_esperado

    prestacao_atualizada = PrestacaoConta.by_uuid(_prestacao_conta_nao_recebida.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_NAO_RECEBIDA, 'Status não deveria ter sido alterado.'

