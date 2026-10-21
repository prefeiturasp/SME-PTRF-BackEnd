import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_tags_list(jwt_authenticated_client_a, tag_a, tag_b):
    response = jwt_authenticated_client_a.get(f'/api/tags/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'id': tag_a.id,
            'nome': 'TagA',
            'criado_em': tag_a.criado_em.isoformat("T"),
            'alterado_em': tag_a.alterado_em.isoformat("T"),
            'uuid': f'{tag_a.uuid}',
            'status': "Inativo",
            'recurso': f'{tag_a.recurso.uuid}'
        },
        {
            'id': tag_b.id,
            'nome': 'TagB',
            'criado_em': tag_b.criado_em.isoformat("T"),
            'alterado_em': tag_b.alterado_em.isoformat("T"),
            'uuid': f'{tag_b.uuid}',
            'status': "Inativo",
            'recurso': f'{tag_b.recurso.uuid}'
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
