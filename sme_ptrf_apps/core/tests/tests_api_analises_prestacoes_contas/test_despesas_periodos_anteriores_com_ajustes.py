import uuid

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def get_url(analise_uuid, conta_uuid, extra=""):
    return (
        f"/api/analises-prestacoes-contas/{analise_uuid}/"
        f"despesas-periodos-anteriores-com-ajustes/?conta_associacao={conta_uuid}{extra}"
    )


def test_api_despesas_periodos_anteriores_com_ajustes(
    jwt_authenticated_client_a,
    despesa_2020_1,
    rateio_despesa_2020_role_conferido,
    conta_associacao_cartao,
    analise_prestacao_conta_2020_1_teste_analises,
    analise_lancamento_despesa_prestacao_conta_2020_1_teste_analises,
):
    url = get_url(analise_prestacao_conta_2020_1_teste_analises.uuid, conta_associacao_cartao.uuid)

    response = jwt_authenticated_client_a.get(url, content_type="application/json")

    assert response.status_code == status.HTTP_200_OK


def test_api_despesas_periodos_anteriores_com_ajustes_sem_conta_associacao(
    jwt_authenticated_client_a,
    analise_prestacao_conta_2020_1_teste_analises,
):
    url = (
        f"/api/analises-prestacoes-contas/{analise_prestacao_conta_2020_1_teste_analises.uuid}/"
        f"despesas-periodos-anteriores-com-ajustes/"
    )

    response = jwt_authenticated_client_a.get(url, content_type="application/json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["erro"] == "parametros_requeridos"


def test_api_despesas_periodos_anteriores_com_ajustes_conta_associacao_nao_encontrada(
    jwt_authenticated_client_a,
    analise_prestacao_conta_2020_1_teste_analises,
):
    conta_inexistente = uuid.uuid4()
    url = get_url(analise_prestacao_conta_2020_1_teste_analises.uuid, conta_inexistente)

    response = jwt_authenticated_client_a.get(url, content_type="application/json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["erro"] == "Objeto não encontrado."


def test_api_despesas_periodos_anteriores_com_ajustes_acao_associacao_nao_encontrada(
    jwt_authenticated_client_a,
    conta_associacao_cartao,
    analise_prestacao_conta_2020_1_teste_analises,
):
    acao_inexistente = uuid.uuid4()
    url = get_url(
        analise_prestacao_conta_2020_1_teste_analises.uuid,
        conta_associacao_cartao.uuid,
        extra=f"&acao_associacao={acao_inexistente}",
    )

    response = jwt_authenticated_client_a.get(url, content_type="application/json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["erro"] == "Objeto não encontrado."


def test_api_despesas_periodos_anteriores_com_ajustes_tipo_invalido(
    jwt_authenticated_client_a,
    conta_associacao_cartao,
    analise_prestacao_conta_2020_1_teste_analises,
):
    url = get_url(
        analise_prestacao_conta_2020_1_teste_analises.uuid,
        conta_associacao_cartao.uuid,
        extra="&tipo=INVALIDO",
    )

    response = jwt_authenticated_client_a.get(url, content_type="application/json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["erro"] == "parametro_inválido"


def test_api_despesas_periodos_anteriores_com_ajustes_tipo_acerto_nao_encontrado(
    jwt_authenticated_client_a,
    conta_associacao_cartao,
    analise_prestacao_conta_2020_1_teste_analises,
):
    tipo_acerto_inexistente = uuid.uuid4()
    url = get_url(
        analise_prestacao_conta_2020_1_teste_analises.uuid,
        conta_associacao_cartao.uuid,
        extra=f"&tipo_acerto={tipo_acerto_inexistente}",
    )

    response = jwt_authenticated_client_a.get(url, content_type="application/json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["erro"] == "Objeto não encontrado."
