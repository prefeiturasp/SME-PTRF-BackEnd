import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

def test_action_editar_informacao_conciliacao(
    analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao_teste_api,
    jwt_authenticated_client_a
):

    payload = {
        "uuid_analise_documento": f"{analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao_teste_api.uuid}",
        "justificativa_conciliacao": "Justificativa Conciliacao ATUALIZADA"
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/editar-informacao-conciliacao/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


def test_action_editar_informacao_conciliacao_deve_gerar_erro_sem_analise(
    analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao_teste_api,
    jwt_authenticated_client_a
):

    payload = {
        "justificativa_conciliacao": "Justificativa Conciliacao ATUALIZADA"
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/editar-informacao-conciliacao/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_action_editar_informacao_conciliacao_deve_gerar_erro_uuid_analise_errado(
    analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao_teste_api,
    jwt_authenticated_client_a
):

    payload = {
        "uuid_analise_documento": f"{analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao_teste_api.uuid}XXX",
        "justificativa_conciliacao": "Justificativa Conciliacao ATUALIZADA"
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/editar-informacao-conciliacao/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_action_editar_informacao_conciliacao_deve_gerar_erro_justificativa(
    analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao_teste_api,
    jwt_authenticated_client_a
):

    payload = {
        "uuid_analise_documento": f"{analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao_teste_api.uuid}",
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-documento-prestacao-conta/editar-informacao-conciliacao/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
