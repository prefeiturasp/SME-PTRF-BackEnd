import pytest
from rest_framework import status
import json
pytestmark = pytest.mark.django_db


def test_endpoint_marcar_como_credito_incluido(
    jwt_authenticated_client_a,
    receita_100_no_periodo,
    solicitacao_acerto_documento_pendente_01
):

    payload = {
        "uuid_credito_incluido": f"{receita_100_no_periodo.uuid}",
        "uuid_solicitacao_acerto": f"{solicitacao_acerto_documento_pendente_01.uuid}"
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-credito-incluido/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


def test_endpoint_marcar_como_credito_incluido_sem_chave_uuid_credito(
    jwt_authenticated_client_a,
    receita_100_no_periodo,
    solicitacao_acerto_documento_pendente_01
):

    payload = {
        "uuid_solicitacao_acerto": f"{solicitacao_acerto_documento_pendente_01.uuid}"
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-credito-incluido/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_marcar_como_credito_incluido_sem_uuid_credito(
    jwt_authenticated_client_a,
    receita_100_no_periodo,
    solicitacao_acerto_documento_pendente_01
):

    payload = {
        "uuid_credito_incluido": f"",
        "uuid_solicitacao_acerto": f"{solicitacao_acerto_documento_pendente_01.uuid}"
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-credito-incluido/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_marcar_como_credito_incluido_sem_chave_uuid_solicitacao_acerto(
    jwt_authenticated_client_a,
    receita_100_no_periodo,
    solicitacao_acerto_documento_pendente_01
):

    payload = {
        "uuid_credito_incluido": f"{receita_100_no_periodo.uuid}",
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-credito-incluido/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_marcar_como_credito_incluido_sem_uuid_solicitacao_acerto(
    jwt_authenticated_client_a,
    receita_100_no_periodo,
    solicitacao_acerto_documento_pendente_01
):

    payload = {
        "uuid_credito_incluido": f"{receita_100_no_periodo.uuid}",
        "uuid_solicitacao_acerto": f""
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-credito-incluido/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
