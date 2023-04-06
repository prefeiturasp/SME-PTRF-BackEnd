import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

def test_action_restaurar_justificativa_original(
    solicitacao_acerto_documento_edicao_informacao_teste_api,
    jwt_authenticated_client_a
):

    payload = {
        "uuid_solicitacao_acerto": f"{solicitacao_acerto_documento_edicao_informacao_teste_api.uuid}",
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/restaurar-justificativa-original/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK

def test_action_restaurar_justificativa_original_deve_gerar_erro_uuid_errado(
    solicitacao_acerto_documento_edicao_informacao_teste_api,
    jwt_authenticated_client_a
):

    payload = {
        "uuid_solicitacao_acerto": f"{solicitacao_acerto_documento_edicao_informacao_teste_api.uuid}x",
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/restaurar-justificativa-original/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_action_restaurar_justificativa_original_deve_gerar_erro_sem_uuid(
    solicitacao_acerto_documento_edicao_informacao_teste_api,
    jwt_authenticated_client_a
):

    payload = {
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/restaurar-justificativa-original/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
