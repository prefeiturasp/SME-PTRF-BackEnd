import json
import pytest
from datetime import date

from model_bakery import baker
from rest_framework import status

from sme_ptrf_apps.core.models import ComentarioAnalisePrestacao

pytestmark = pytest.mark.django_db


@pytest.fixture
def comentario_analise_prestacao(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'ComentarioAnalisePrestacao',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        ordem=1,
        comentario='Teste',
    )


@pytest.fixture
def comentario_analise_prestacao_notificado_01_nao_atualiza(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'ComentarioAnalisePrestacao',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        ordem=1,
        comentario='Teste notificado 02',
        notificado=True,
        notificado_em=date(2019, 5, 19),
    )


@pytest.fixture
def payload_altera_comentario(prestacao_conta_2020_1_conciliada):
    payload = {
        'comentario': 'Teste Alterado'
    }
    return payload


@pytest.fixture
def payload_nao_altera_comentario_ja_notificado(prestacao_conta_2020_1_conciliada):
    payload = {
        "comentario": "Teste de Comentário 04 - ALTERADO",
        "notificado": True,
        "notificado_em": '',
    }
    return payload


def test_update_comentario_analise_prestacao(jwt_authenticated_client, comentario_analise_prestacao,
                                             payload_altera_comentario):
    response = jwt_authenticated_client.patch(
        f'/api/comentarios-de-analises/{comentario_analise_prestacao.uuid}/',
        data=json.dumps(payload_altera_comentario),
        content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    comentario = ComentarioAnalisePrestacao.objects.filter(uuid=result['uuid']).get()

    assert comentario.comentario == 'Teste Alterado', "Alteração não foi feita"


def test_nao_update_comentario_ja_notificado(
    jwt_authenticated_client,
    comentario_analise_prestacao_notificado_01_nao_atualiza,
    payload_nao_altera_comentario_ja_notificado
):
    response = jwt_authenticated_client.patch(
        f'/api/comentarios-de-analises/{comentario_analise_prestacao_notificado_01_nao_atualiza.uuid}/',
        data=json.dumps(payload_nao_altera_comentario_ja_notificado),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    erro = {"detail": "Comentários já notificados não podem mais ser editados ou removidos."}

    assert result == erro

