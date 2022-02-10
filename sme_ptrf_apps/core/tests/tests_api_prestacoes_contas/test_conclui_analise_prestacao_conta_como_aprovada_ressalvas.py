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


@pytest.fixture
def motivo_aprovacao_ressalva_x():
    return baker.make(
        'MotivoAprovacaoRessalva',
        motivo='X'
    )


@freeze_time('2020-09-01')
def test_api_conclui_analise_prestacao_conta_aprovada_ressalvas(jwt_authenticated_client_a, prestacao_conta_em_analise,
                                                                conta_associacao, motivo_aprovacao_ressalva_x):
    payload = {
        'devolucao_tesouro': True,
        'analises_de_conta_da_prestacao': [
            {
                'conta_associacao': f'{conta_associacao.uuid}',
                'data_extrato': '2020-07-01',
                'saldo_extrato': 100.00,
            },
        ],
        'resultado_analise': PrestacaoConta.STATUS_APROVADA_RESSALVA,
        'motivos_aprovacao_ressalva': [f'{motivo_aprovacao_ressalva_x.uuid}', ],
        'outros_motivos_aprovacao_ressalva': 'outro motivo',
        'recomendacoes': 'recomendacao'
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_em_analise.uuid}/concluir-analise/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_em_analise.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_APROVADA_RESSALVA, 'Status deveria ter passado para APROVADA_RESSALVA.'
    assert prestacao_atualizada.motivos_aprovacao_ressalva.get(pk=motivo_aprovacao_ressalva_x.pk) == motivo_aprovacao_ressalva_x, 'Não gravou os motivos da ressalva.'
    assert prestacao_atualizada.outros_motivos_aprovacao_ressalva == 'outro motivo', 'Não gravou outros motivos.'
    assert prestacao_atualizada.recomendacoes == 'recomendacao', 'Não gravou recomendacoes.'


def test_api_conclui_analise_prestacao_conta_aprovada_ressalva_exige_ressalva(jwt_authenticated_client_a,
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
        ],
        'resultado_analise': PrestacaoConta.STATUS_APROVADA_RESSALVA,
    }
    url = f'/api/prestacoes-contas/{prestacao_conta_em_analise.uuid}/concluir-analise/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_em_analise.uuid}',
        'erro': 'falta_de_informacoes',
        'operacao': 'concluir-analise',
        'mensagem': 'Para concluir como APROVADO_RESSALVA é necessário informar motivos_aprovacao_ressalva ou outros_motivos_aprovacao_ressalva.'
    }

    assert result == result_esperado, "Deveria ter retornado erro falta_de_informacoes."


def test_api_conclui_analise_prestacao_conta_aprovada_ressalva_exige_recomendacoes(jwt_authenticated_client_a,
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
        ],
        'resultado_analise': PrestacaoConta.STATUS_APROVADA_RESSALVA,
        'outros_motivos_aprovacao_ressalva': 'motivo'
    }
    url = f'/api/prestacoes-contas/{prestacao_conta_em_analise.uuid}/concluir-analise/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_em_analise.uuid}',
        'erro': 'falta_de_informacoes',
        'operacao': 'concluir-analise',
        'mensagem': 'Para concluir como APROVADO_RESSALVA é necessário informar as recomendações.'
    }

    assert result == result_esperado, "Deveria ter retornado erro falta_de_informacoes."
