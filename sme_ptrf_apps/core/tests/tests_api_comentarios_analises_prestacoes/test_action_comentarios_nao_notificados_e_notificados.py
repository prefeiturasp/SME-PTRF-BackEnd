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
def comentario_analise_prestacao_com_associacao_e_periodo_nao_notificado_01(associacao, periodo):
    return baker.make(
        'ComentarioAnalisePrestacao',
        associacao=associacao,
        periodo=periodo,
        ordem=1,
        comentario='Teste nao notificado com associação e período 01',
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

@pytest.fixture
def comentario_analise_prestacao_com_associacao_e_periodo_notificado_01(associacao, periodo):
    return baker.make(
        'ComentarioAnalisePrestacao',
        associacao=associacao,
        periodo=periodo,
        ordem=1,
        comentario='Teste notificado com associação e período 01',
        notificado=True,
        notificado_em=date(2019, 5, 18),
    )

def test_list_comentarios_nao_notificados_e_notificados_com_pc(
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

    result_uuids = []
    for _result in result["comentarios_nao_notificados"]:
        result_uuids.append(_result["uuid"])
    for _result in result["comentarios_notificados"]:
        result_uuids.append(_result["uuid"])

    esperado_uuids = [
        f"{comentario_analise_prestacao_nao_notificado_01.uuid}",
        f"{comentario_analise_prestacao_nao_notificado_02.uuid}",
        f"{comentario_analise_prestacao_notificado_02.uuid}",
        f"{comentario_analise_prestacao_notificado_01.uuid}",
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result_uuids == esperado_uuids

def test_list_comentarios_nao_notificados_e_notificados_com_associacao_e_periodo(
    jwt_authenticated_client_a,
    associacao,
    periodo,
    comentario_analise_prestacao_com_associacao_e_periodo_nao_notificado_01,
    comentario_analise_prestacao_com_associacao_e_periodo_notificado_01,
):

    associacao_uuid = associacao.uuid
    periodo_uuid = periodo.uuid

    response = jwt_authenticated_client_a.get(
        f'/api/comentarios-de-analises/comentarios/?prestacao_conta__uuid=&associacao_uuid={associacao_uuid}&periodo_uuid={periodo_uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)

    result_uuids = []
    for _result in result["comentarios_nao_notificados"]:
        result_uuids.append(_result["uuid"])
    for _result in result["comentarios_notificados"]:
        result_uuids.append(_result["uuid"])

    esperado_uuids = [
        f"{comentario_analise_prestacao_com_associacao_e_periodo_nao_notificado_01.uuid}",
        f"{comentario_analise_prestacao_com_associacao_e_periodo_notificado_01.uuid}",
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result_uuids == esperado_uuids

def test_list_comentarios_nao_notificados_e_notificados_com_erro_de_parametro(
    jwt_authenticated_client_a,
    associacao,
):
    associacao_uuid = associacao.uuid

    response = jwt_authenticated_client_a.get(
        f'/api/comentarios-de-analises/comentarios/?prestacao_conta__uuid=&associacao_uuid={associacao_uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)

    esperado = {
        "erro": "parametros_requerido",
        "mensagem": "É necessário enviar o uuid da prestação de contas ou o uuid da associação e o uuid do período."
    }
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado
