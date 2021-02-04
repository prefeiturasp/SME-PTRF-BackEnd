import json
import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import Tag

pytestmark = pytest.mark.django_db


def test_update_tag(jwt_authenticated_client_a, tag_a, payload_update_tag):

    assert Tag.objects.get(uuid=tag_a.uuid).nome == 'TagA'

    response = jwt_authenticated_client_a.patch(
        f'/api/tags/{tag_a.uuid}/',
        data=json.dumps(payload_update_tag),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK

    assert Tag.objects.get(uuid=tag_a.uuid).nome == payload_update_tag['nome']
