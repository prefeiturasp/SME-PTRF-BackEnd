import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_retrieve_comentario_analise_consolidado_dre(
    jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre,
    consolidado_dre_teste_api_comentario_analise_consolidado_dre,
    comentario_analise_consolidado_dre_01,
    comentario_analise_consolidado_dre_02,
):
    comentario_uuid = f"{comentario_analise_consolidado_dre_01.uuid}"

    response = jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre.delete(
        f'/api/comentarios-de-analises-consolidados-dre/{comentario_uuid}/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

