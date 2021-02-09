import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_retrieve_tag(jwt_authenticated_client_a, tag_a):
    response = jwt_authenticated_client_a.get(
        f'/api/tags/{tag_a.uuid}/', content_type='applicaton/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'id': tag_a.id,
        'nome': tag_a.nome,
        'criado_em': tag_a.criado_em.isoformat("T"),
        'alterado_em': tag_a.alterado_em.isoformat("T"),
        'uuid': f'{tag_a.uuid}',
        'status': "Inativo"
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
