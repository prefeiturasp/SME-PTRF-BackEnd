import json
import pytest

from freezegun import freeze_time
from datetime import date

from model_bakery import baker
from rest_framework import status

from ...models import PrestacaoConta, ComentarioAnalisePrestacao

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
def comentario_analise_A(prestacao_conta_em_analise):
    return baker.make(
        'ComentarioAnalisePrestacao',
        prestacao_conta=prestacao_conta_em_analise,
        ordem=1,
        comentario='A',
    )


@pytest.fixture
def comentario_analise_B(prestacao_conta_em_analise):
    return baker.make(
        'ComentarioAnalisePrestacao',
        prestacao_conta=prestacao_conta_em_analise,
        ordem=2,
        comentario='B',
    )


@pytest.fixture
def comentario_analise_C(prestacao_conta_em_analise):
    return baker.make(
        'ComentarioAnalisePrestacao',
        prestacao_conta=prestacao_conta_em_analise,
        ordem=3,
        comentario='C',
    )


@freeze_time('2020-09-01')
def test_api_reordena_comentarios_prestacao_conta(jwt_authenticated_client, prestacao_conta_em_analise,
                                                  comentario_analise_A, comentario_analise_B, comentario_analise_C):
    payload = {
        'comentarios_de_analise': [
            {
                'uuid': f'{comentario_analise_C.uuid}',
                'ordem': 1
            },
            {
                'uuid': f'{comentario_analise_A.uuid}',
                'ordem': 2
            },
            {
                'uuid': f'{comentario_analise_B.uuid}',
                'ordem': 3
            }
        ]
    }

    url = f'/api/comentarios-de-analises/reordenar-comentarios/'

    response = jwt_authenticated_client.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    comentario_a_atualizado = ComentarioAnalisePrestacao.by_uuid(comentario_analise_A.uuid)
    assert comentario_a_atualizado.ordem == 2, 'Ordem do comentário A não está correta.'

    comentario_b_atualizado = ComentarioAnalisePrestacao.by_uuid(comentario_analise_B.uuid)
    assert comentario_b_atualizado.ordem == 3, 'Ordem do comentário B não está correta.'

    comentario_c_atualizado = ComentarioAnalisePrestacao.by_uuid(comentario_analise_C.uuid)
    assert comentario_c_atualizado.ordem == 1, 'Ordem do comentário C não está correta.'


def test_api_reordena_comentarios_prestacao_conta_exige_payload(jwt_authenticated_client, prestacao_conta_em_analise):
    url = f'/api/comentarios-de-analises/reordenar-comentarios/'

    response = jwt_authenticated_client.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'erro': 'falta_de_informacoes',
        'operacao': 'reordenar-comentarios',
        'mensagem': 'Faltou informar o campo comentarios_de_analise no payload.'
    }

    assert result == result_esperado, "Deveria ter retornado erro falta_de_informacoes."


def test_api_reordena_comentarios_prestacao_conta_valida_uuids(jwt_authenticated_client, prestacao_conta_em_analise):
    payload = {
        'comentarios_de_analise': [
            {
                'uuid': f'{prestacao_conta_em_analise.uuid}',   # UUID inválido
                'ordem': 1
            },
        ]
    }

    url = f'/api/comentarios-de-analises/reordenar-comentarios/'

    response = jwt_authenticated_client.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'erro': 'Objeto não encontrado.',
        'mensagem': 'Algum comentário da lista não foi encontrado pelo uuid informado.'
    }

    assert result == result_esperado, "Deveria ter retornado erro falta_de_informacoes."
