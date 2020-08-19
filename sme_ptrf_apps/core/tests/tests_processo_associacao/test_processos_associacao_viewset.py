import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.processos_associacao_viewset import ProcessosAssociacaoViewSet

pytestmark = pytest.mark.django_db


def test_view_set(processo_associacao_123456_2019, fake_user):
    request = APIRequestFactory().get("")
    detalhe = ProcessosAssociacaoViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = detalhe(request, uuid=processo_associacao_123456_2019.uuid)

    assert response.status_code == status.HTTP_200_OK
