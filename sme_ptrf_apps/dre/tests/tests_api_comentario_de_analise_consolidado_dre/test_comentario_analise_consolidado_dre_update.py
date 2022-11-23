import json
import pytest
from rest_framework import status
from ...models.comentario_analise_consolidado_dre import ComentarioAnaliseConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_altera_comentario():
    payload = {
        'comentario': 'Teste Alterado'
    }
    return payload


def test_update_comentario_analise_consolidado_dre(
    jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre,
    comentario_analise_consolidado_dre_01,
    payload_altera_comentario
):

    uuid_comentario = f"{comentario_analise_consolidado_dre_01.uuid}"

    assert comentario_analise_consolidado_dre_01.comentario == 'Este é um comentario de analise de consolidadodo DRE'

    response = jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre.patch(
        f'/api/comentarios-de-analises-consolidados-dre/{uuid_comentario}/',
        data=json.dumps(payload_altera_comentario),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK

    comentario = ComentarioAnaliseConsolidadoDRE.objects.filter(uuid=uuid_comentario).get()

    assert comentario.comentario == 'Teste Alterado'


