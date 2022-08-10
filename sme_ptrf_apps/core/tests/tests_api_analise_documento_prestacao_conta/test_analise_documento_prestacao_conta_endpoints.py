import pytest
from rest_framework import status
import json
pytestmark = pytest.mark.django_db


def test_endpoint_tabelas(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(
        f'/api/analises-documento-prestacao-conta/tabelas/', content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        "status_realizacao": [
            {
                "id": "PENDENTE",
                "nome": "Pendente"
            },
            {
                "id": "REALIZADO",
                "nome": "Realizado"
            },
            {
                "id": "JUSTIFICADO",
                "nome": "Justificado"
            }
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert resultado_esperado["status_realizacao"] == result["status_realizacao"]


def test_endpoint_limpar_status(jwt_authenticated_client_a, analise_documento_realizado_01):
    payload = {
        "uuids_analises_documentos": [
            f"{analise_documento_realizado_01.uuid}"
        ]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/limpar-status/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


def test_endpoint_limpar_status_sem_uuid_analises(jwt_authenticated_client_a, analise_documento_realizado_01):
    payload = {
        "uuids_analises_documentos": [

        ]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/limpar-status/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_limpar_status_sem_chave_uuid_analises(jwt_authenticated_client_a, analise_documento_realizado_01):
    payload = {

    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/limpar-status/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_limpar_status_pendente(jwt_authenticated_client_a, analise_documento_pendente_01):
    payload = {
        "uuids_analises_documentos": [
            f"{analise_documento_pendente_01.uuid}"
        ]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/limpar-status/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_marcar_realizado(jwt_authenticated_client_a, analise_documento_pendente_01):
    payload = {
        "uuids_analises_documentos": [
            f"{analise_documento_pendente_01.uuid}"
        ]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-realizado/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


def test_endpoint_marcar_realizado_sem_uuid_analises(jwt_authenticated_client_a, analise_documento_pendente_01):
    payload = {
        "uuids_analises_documentos": [

        ]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-realizado/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_marcar_realizado_sem_chave_uuid_analises(jwt_authenticated_client_a, analise_documento_pendente_01):
    payload = {

    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-realizado/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_marcar_realizado_status_realizado(jwt_authenticated_client_a, analise_documento_realizado_01):
    payload = {
        "uuids_analises_documentos": [
            f"{analise_documento_realizado_01.uuid}"
        ]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-realizado/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_justificar_nao_realizacao(jwt_authenticated_client_a, analise_documento_realizado_01):
    payload = {
        "justificativa": "teste",
        "uuids_analises_documentos": [
            f"{analise_documento_realizado_01.uuid}"
        ]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/justificar-nao-realizacao/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


def test_endpoint_justificar_nao_realizado_sem_uuid_analises(
    jwt_authenticated_client_a,
    analise_documento_realizado_01
):
    payload = {
        "uuids_analises_documentos": [

        ]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/justificar-nao-realizacao/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_justificar_nao_realizado_sem_chave_uuid_analises(
    jwt_authenticated_client_a,
    analise_documento_realizado_01
):
    payload = {

    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/justificar-nao-realizacao/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_justificar_nao_realizado_sem_chave_justificativa(
    jwt_authenticated_client_a,
    analise_documento_realizado_01
):
    payload = {
        "uuids_analises_documentos": [
            f"{analise_documento_realizado_01.uuid}"
        ]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/justificar-nao-realizacao/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_justificar_nao_realizado_status_justificar(
    jwt_authenticated_client_a,
    analise_documento_justificado_01
):
    payload = {
        "uuids_analises_documentos": [
            f"{analise_documento_justificado_01.uuid}"
        ]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/justificar-nao-realizacao/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
