import json

import pytest
from model_bakery import baker
from rest_framework import status
from datetime import date

pytestmark = pytest.mark.django_db


@pytest.fixture
def comentario_analise_prestacao_nao_notificado_01(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'ComentarioAnalisePrestacao',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        ordem=1,
        comentario='Teste nao notificado 01',
        notificado=False,
        notificado_em=None
    )


@pytest.fixture
def comentario_analise_prestacao_nao_notificado_02(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'ComentarioAnalisePrestacao',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        ordem=1,
        comentario='Teste nao notificado 02',
        notificado=False,
        notificado_em=None
    )


@pytest.fixture
def comentario_analise_prestacao_notificado_01(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'ComentarioAnalisePrestacao',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        ordem=1,
        comentario='Teste notificado 01',
        notificado=True,
        notificado_em=date(2019, 5, 18),
    )


@pytest.fixture
def comentario_analise_prestacao_notificado_02(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'ComentarioAnalisePrestacao',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        ordem=1,
        comentario='Teste notificado 02',
        notificado=True,
        notificado_em=date(2019, 5, 19),
    )


def test_list_comentarios_nao_notificados_e_notificados_separados(
    jwt_authenticated_client_a,
    prestacao_conta_2020_1_conciliada,
    comentario_analise_prestacao_nao_notificado_01,
    comentario_analise_prestacao_nao_notificado_02,
    comentario_analise_prestacao_notificado_01,
    comentario_analise_prestacao_notificado_02
):
    prestacao_uuid = prestacao_conta_2020_1_conciliada.uuid

    response = jwt_authenticated_client_a.get(
        f'/api/comentarios-de-analises/comentarios/?prestacao_conta__uuid={prestacao_uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)

    # Já Notificados estão ordenados por .order_by('-notificado_em')
    esperado = {
        "comentarios_nao_notificados": [
            {
                "uuid": f"{comentario_analise_prestacao_nao_notificado_01.uuid}",
                "prestacao_conta": f"{prestacao_uuid}",
                "ordem": comentario_analise_prestacao_nao_notificado_01.ordem,
                "comentario": comentario_analise_prestacao_nao_notificado_01.comentario,
                "notificado": False,
                "notificado_em": None
            },
            {
                "uuid": f"{comentario_analise_prestacao_nao_notificado_02.uuid}",
                "prestacao_conta": f"{prestacao_uuid}",
                "ordem": comentario_analise_prestacao_nao_notificado_02.ordem,
                "comentario": comentario_analise_prestacao_nao_notificado_02.comentario,
                "notificado": False,
                "notificado_em": None
            },
        ],
        "comentarios_notificados": [
            {
                "uuid": f"{comentario_analise_prestacao_notificado_02.uuid}",
                "prestacao_conta": f"{prestacao_uuid}",
                "ordem": comentario_analise_prestacao_notificado_02.ordem,
                "comentario": comentario_analise_prestacao_notificado_02.comentario,
                "notificado": True,
                "notificado_em": '2019-05-19'
            },
            {
                "uuid": f"{comentario_analise_prestacao_notificado_01.uuid}",
                "prestacao_conta": f"{prestacao_uuid}",
                "ordem": comentario_analise_prestacao_notificado_01.ordem,
                "comentario": comentario_analise_prestacao_notificado_01.comentario,
                "notificado": True,
                "notificado_em": '2019-05-18'
            },
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
