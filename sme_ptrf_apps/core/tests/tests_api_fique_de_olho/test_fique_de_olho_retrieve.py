import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_retrieve_fique_de_olho(jwt_authenticated_client_a, fique_de_olho_a):
    response = jwt_authenticated_client_a.get(
        f'/api/fique-de-olho/{fique_de_olho_a.uuid}/', content_type='applicaton/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'id': fique_de_olho_a.id,
        'uuid': f'{fique_de_olho_a.uuid}',
        'texto': fique_de_olho_a.texto,
        'tipo_texto': fique_de_olho_a.tipo_texto,
        'recurso': f'{fique_de_olho_a.recurso.uuid}',
        'short_texto': fique_de_olho_a.get_short_texto(),
        'tipo_texto_display': fique_de_olho_a.get_tipo_texto_display(),
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
