import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_marcar_como_esclarecido(
    solicitacao_acerto_documento_pendente_01,
    jwt_authenticated_client_a
):

    payload = {
        'esclarecimento': "Este é o esclarecimento",
        'uuid_solicitacao_acerto': f"{solicitacao_acerto_documento_pendente_01.uuid}"
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-esclarecido/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


def test_marcar_como_esclarecido_sem_chave_esclarecimento(
    solicitacao_acerto_documento_pendente_01,
    jwt_authenticated_client_a
):

    payload = {

        'uuid_solicitacao_acerto': f"{solicitacao_acerto_documento_pendente_01.uuid}"
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-esclarecido/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_marcar_como_esclarecido_sem_esclarecimento(
    solicitacao_acerto_documento_pendente_01,
    jwt_authenticated_client_a
):

    payload = {
        'esclarecimento': "",
        'uuid_solicitacao_acerto': f"{solicitacao_acerto_documento_pendente_01.uuid}"
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-esclarecido/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_marcar_como_esclarecido_sem_chave_uuid_solicitacao_acerto(
    solicitacao_acerto_documento_pendente_01,
    jwt_authenticated_client_a
):
    payload = {
        'esclarecimento': "Este é o esclarecimento",
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-esclarecido/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_marcar_como_esclarecido_sem_uuid_solicitacao_acerto(
    solicitacao_acerto_documento_pendente_01,
    jwt_authenticated_client_a
):
    payload = {
        'esclarecimento': "Este é o esclarecimento",
        'uuid_solicitacao_acerto': f""
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-esclarecido/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
