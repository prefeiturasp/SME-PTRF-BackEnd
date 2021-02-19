import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from model_bakery import baker

from ...api.views.tags_viewset import TagsViewSet

pytestmark = pytest.mark.django_db

@pytest.fixture
def tag_x():
    return baker.make('Tag', nome='X')


def test_tag_view_set(tag_x, usuario_permissao_associacao):
    request = APIRequestFactory().get('')
    detalhe = TagsViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=tag_x.uuid)

    assert response.status_code == status.HTTP_200_OK

