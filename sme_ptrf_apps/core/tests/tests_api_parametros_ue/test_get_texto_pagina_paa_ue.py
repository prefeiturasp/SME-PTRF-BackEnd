import json

from model_bakery import baker
import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db

@pytest.fixture
def payload_update_texto_paa_ue():
    payload = {
        'texto_pagina_paa_ue': '<p>x alterada</p>',
    }
    return payload


@pytest.fixture
def parametro_texto_pagina_paa_ue():
    return baker.make(
        'Parametros',
        texto_pagina_paa_ue='Texto PAA',
    )


def test_api_get_texto_paa_ue(jwt_authenticated_client_a, parametros):
    response = jwt_authenticated_client_a.get(
        '/api/parametros-ue/texto-pagina-paa-ue/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {'detail': 'Teste PAA UE'}

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_update_texto_paa_ue(jwt_authenticated_client_a, parametro_texto_pagina_paa_ue, payload_update_texto_paa_ue):
    response = jwt_authenticated_client_a.patch('/api/parametros-ue/update-texto-pagina-paa-ue/',
        data=json.dumps(payload_update_texto_paa_ue),
        content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    assert 'detail' in response.data
    assert response.data['detail'] == 'Salvo com sucesso'


def test_update_texto_paa_ue_sem_parametro(jwt_authenticated_client_a, parametro_texto_pagina_paa_ue):
    response = jwt_authenticated_client_a.patch('/api/parametros-ue/update-texto-pagina-paa-ue/',
                                                data=json.dumps({'outra_prop': 'teste'}),
                                                content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'erro' in response.data
    assert 'operacao' in response.data
    assert 'mensagem' in response.data
