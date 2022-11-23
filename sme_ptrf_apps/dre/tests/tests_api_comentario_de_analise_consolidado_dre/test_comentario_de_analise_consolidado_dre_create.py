import json

import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import ComentarioAnalisePrestacao
from ...models.comentario_analise_consolidado_dre import ComentarioAnaliseConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_comentario(consolidado_dre_teste_api_comentario_analise_consolidado_dre):
    payload = {
        'consolidado_dre': f'{consolidado_dre_teste_api_comentario_analise_consolidado_dre.uuid}',
        'ordem': 1,
        'comentario': 'Teste'
    }
    return payload


def test_create_comentario_analise_consolidado_dre(
    jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre,
    payload_comentario
):
    response = jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre.post(
        '/api/comentarios-de-analises-consolidados-dre/',
        data=json.dumps(payload_comentario),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert ComentarioAnaliseConsolidadoDRE.objects.filter(uuid=result['uuid']).exists()
