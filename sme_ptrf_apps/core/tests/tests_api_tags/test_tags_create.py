import json
import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import Tag

pytestmark = pytest.mark.django_db


def test_create_tag(jwt_authenticated_client_a):

    payload_nova_tag = {
        'nome': "Tag Nova",
        'status': "ATIVO"
    }

    response = jwt_authenticated_client_a.post(
        f'/api/tags/', data=json.dumps(payload_nova_tag), content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED
    assert Tag.objects.filter(uuid=result['uuid']).exists()


def test_create_tag_nome_igual(jwt_authenticated_client_a, tag_c):
    payload_tag_nova = {
        'nome': 'TagXpto',
        'status': 'ATIVO'
    }

    response = jwt_authenticated_client_a.post(
        f'/api/tags/', data=json.dumps(payload_tag_nova), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    assert result == {
      "non_field_errors": [
        "The fields nome must make a unique set."
      ]
    }

