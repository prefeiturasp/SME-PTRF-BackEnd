import pytest
from rest_framework import status
import json
pytestmark = pytest.mark.django_db


def test_endpoint_tabelas(jwt_authenticated_client_a, analise_prestacao_conta_2020_1):
    response = jwt_authenticated_client_a.get(
        f'/api/analises-documento-prestacao-conta/tabelas/'
        f'?uuid_analise_prestacao={analise_prestacao_conta_2020_1.uuid}&visao=DRE', content_type='application/json')

    assert response.status_code == status.HTTP_200_OK


def test_endpoint_tabelas_editavel_false_visao_dre(jwt_authenticated_client_a, analise_prestacao_conta_2020_1):
    response = jwt_authenticated_client_a.get(
        f'/api/analises-documento-prestacao-conta/tabelas/'
        f'?uuid_analise_prestacao={analise_prestacao_conta_2020_1.uuid}&visao=DRE', content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        "editavel": False
    }

    assert response.status_code == status.HTTP_200_OK
    assert resultado_esperado["editavel"] == result["editavel"]


def test_endpoint_tabelas_editavel_false_visao_ue(
    jwt_authenticated_client_a,
    analise_prestacao_conta_2020_1,
    analise_prestacao_conta_2020_1_2
):
    response = jwt_authenticated_client_a.get(
        f'/api/analises-documento-prestacao-conta/tabelas/'
        f'?uuid_analise_prestacao={analise_prestacao_conta_2020_1.uuid}&visao=UE', content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        "editavel": False
    }

    assert response.status_code == status.HTTP_200_OK
    assert resultado_esperado["editavel"] == result["editavel"]


def test_endpoint_tabelas_editavel_true_visao_ue(jwt_authenticated_client_a, analise_prestacao_conta_2020_1):
    response = jwt_authenticated_client_a.get(
        f'/api/analises-documento-prestacao-conta/tabelas/'
        f'?uuid_analise_prestacao={analise_prestacao_conta_2020_1.uuid}&visao=UE', content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        "editavel": True
    }

    assert response.status_code == status.HTTP_200_OK
    assert resultado_esperado["editavel"] == result["editavel"]


def test_endpoint_tabelas_status_realizacao(jwt_authenticated_client_a, analise_prestacao_conta_2020_1):
    response = jwt_authenticated_client_a.get(
        f'/api/analises-documento-prestacao-conta/tabelas/'
        f'?uuid_analise_prestacao={analise_prestacao_conta_2020_1.uuid}&visao=DRE', content_type='application/json')

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
            },
            {
                "id": "REALIZADO_JUSTIFICADO",
                "nome": "Realizado e justificado"
            },
            {
                "id": "REALIZADO_PARCIALMENTE",
                "nome": "Realizado parcialmente"
            },
        ],
    }

    assert response.status_code == status.HTTP_200_OK
    assert resultado_esperado["status_realizacao"] == result["status_realizacao"]


def test_endpoint_tabelas_status_realizacao_solicitacao(jwt_authenticated_client_a, analise_prestacao_conta_2020_1):
    response = jwt_authenticated_client_a.get(
        f'/api/analises-documento-prestacao-conta/tabelas/'
        f'?uuid_analise_prestacao={analise_prestacao_conta_2020_1.uuid}&visao=DRE', content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        "status_realizacao_solicitacao": [
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
    assert resultado_esperado["status_realizacao_solicitacao"] == result["status_realizacao_solicitacao"]


def test_endpoint_limpar_status(jwt_authenticated_client_a, solicitacao_acerto_documento_realizado_01):
    payload = {
        "uuids_solicitacoes_acertos_documentos": [
            f"{solicitacao_acerto_documento_realizado_01.uuid}"
        ]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/limpar-status/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


def test_endpoint_limpar_status_sem_uuid_solicitacao(
    jwt_authenticated_client_a,
    solicitacao_acerto_documento_realizado_01
):
    payload = {
        "uuids_solicitacoes_acertos_documentos": [

        ]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/limpar-status/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_limpar_status_sem_chave_uuid_solicitacao(
    jwt_authenticated_client_a,
    solicitacao_acerto_documento_realizado_01
):
    payload = {

    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/limpar-status/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_marcar_realizado(jwt_authenticated_client_a, solicitacao_acerto_documento_pendente_01):
    payload = {
        "uuids_solicitacoes_acertos_documentos": [
            f"{solicitacao_acerto_documento_pendente_01.uuid}"
        ]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-realizado/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


def test_endpoint_marcar_realizado_sem_uuid_solicitacao(
    jwt_authenticated_client_a,
    solicitacao_acerto_documento_pendente_01
):
    payload = {
        "uuids_solicitacoes_acertos_documentos": [

        ]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-realizado/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_marcar_realizado_sem_chave_uuid_solicitacao(
    jwt_authenticated_client_a,
    solicitacao_acerto_documento_pendente_01
):
    payload = {

    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/marcar-como-realizado/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_justificar_nao_realizacao(jwt_authenticated_client_a, solicitacao_acerto_documento_realizado_01):
    payload = {
        "justificativa": "teste",
        "uuids_solicitacoes_acertos_documentos": [
            f"{solicitacao_acerto_documento_realizado_01.uuid}"
        ]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/justificar-nao-realizacao/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


def test_endpoint_justificar_nao_realizado_sem_uuid_solicitacao(
    jwt_authenticated_client_a,
    solicitacao_acerto_documento_realizado_01
):
    payload = {
        "uuids_solicitacoes_acertos_documentos": [

        ]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/justificar-nao-realizacao/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_justificar_nao_realizado_sem_chave_uuid_solicitacao(
    jwt_authenticated_client_a,
    solicitacao_acerto_documento_realizado_01
):
    payload = {

    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/justificar-nao-realizacao/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_justificar_nao_realizado_sem_justificativa(
    jwt_authenticated_client_a,
    solicitacao_acerto_documento_realizado_01
):
    payload = {
        "justificativa": "",
        "uuids_solicitacoes_acertos_documentos": [
            f"{solicitacao_acerto_documento_realizado_01.uuid}"
        ]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/justificar-nao-realizacao/', data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_endpoint_tags_informacoes_conferencia(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get( f'/api/analises-documento-prestacao-conta/tags-informacoes-conferencia/')

    assert response.status_code == status.HTTP_200_OK
