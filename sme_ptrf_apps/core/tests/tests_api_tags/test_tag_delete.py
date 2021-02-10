import json
import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import Tag

pytestmark = pytest.mark.django_db


def test_delete_tag(jwt_authenticated_client_a, tag_a):
    assert Tag.objects.filter(uuid=tag_a.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/tags/{tag_a.uuid}/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Tag.objects.filter(uuid=tag_a.uuid).exists()
