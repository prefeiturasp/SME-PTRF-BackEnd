import pytest
from rest_framework import status
import json
pytestmark = pytest.mark.django_db


def test_endpoint_marcar_como_gasto_incluido(
    jwt_authenticated_client_a,
    despesa_no_periodo,
    solicitacao_acerto_documento_pendente_01
):

    payload = {
        "uuid_gasto_incluido": f"{despesa_no_periodo.uuid}",
        "uuid_solicitacao_acerto": f"{solicitacao_acerto_documento_pendente_01.uuid}"
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-gasto-incluido/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


def test_endpoint_marcar_como_gasto_incluido_sem_chave_uuid_gasto(
    jwt_authenticated_client_a,
    despesa_no_periodo,
    solicitacao_acerto_documento_pendente_01
):

    payload = {
        "uuid_solicitacao_acerto": f"{solicitacao_acerto_documento_pendente_01.uuid}"
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-gasto-incluido/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_marcar_como_gasto_incluido_sem_uuid_gasto(
    jwt_authenticated_client_a,
    despesa_no_periodo,
    solicitacao_acerto_documento_pendente_01
):

    payload = {
        "uuid_gasto_incluido": f"",
        "uuid_solicitacao_acerto": f"{solicitacao_acerto_documento_pendente_01.uuid}"
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-gasto-incluido/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_marcar_como_gasto_incluido_sem_chave_uuid_solicitacao(
    jwt_authenticated_client_a,
    despesa_no_periodo,
    solicitacao_acerto_documento_pendente_01
):

    payload = {
        "uuid_gasto_incluido": f"{despesa_no_periodo.uuid}",
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-gasto-incluido/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_marcar_como_gasto_incluido_sem_uuid_solicitacao(
    jwt_authenticated_client_a,
    despesa_no_periodo,
    solicitacao_acerto_documento_pendente_01
):

    payload = {
        "uuid_gasto_incluido": f"{despesa_no_periodo.uuid}",
        "uuid_solicitacao_acerto": f""
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-gasto-incluido/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
