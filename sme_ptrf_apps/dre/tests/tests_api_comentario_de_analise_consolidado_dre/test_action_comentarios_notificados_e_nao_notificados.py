import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_comentarios_notificados_e_nao_notificados_consolidado_dre_uuid_errado(
    jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre,
    consolidado_dre_teste_api_comentario_analise_consolidado_dre
):
    consolidado_dre_uuid = f"{consolidado_dre_teste_api_comentario_analise_consolidado_dre.uuid}XXX"

    response = jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre.get(
        f'/api/comentarios-de-analises-consolidados-dre/comentarios/?consolidado_dre={consolidado_dre_uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)

    erro = {
        'erro': 'Objeto não encontrado.',
        'mensagem': f"O objeto Consolidado DRE para o uuid {consolidado_dre_uuid} não foi encontrado na base."
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == erro


def test_comentarios_notificados_e_nao_notificados_sem_consolidado_dre_uuid(
    jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre,
):

    response = jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre.get(
        f'/api/comentarios-de-analises-consolidados-dre/comentarios/',
        content_type='application/json'
    )

    result = json.loads(response.content)

    erro = {
        'erro': 'parametros_requerido',
        'mensagem': 'É necessário enviar o uuid do Consolidado DRE.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == erro


def test_comentarios_notificados_e_nao_notificados(
    jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre,
    consolidado_dre_teste_api_comentario_analise_consolidado_dre
):
    consolidado_dre_uuid = consolidado_dre_teste_api_comentario_analise_consolidado_dre.uuid

    response = jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre.get(
        f'/api/comentarios-de-analises-consolidados-dre/comentarios/?consolidado_dre={consolidado_dre_uuid}',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
