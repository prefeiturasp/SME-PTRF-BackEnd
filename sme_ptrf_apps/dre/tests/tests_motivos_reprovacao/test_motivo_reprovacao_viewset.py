import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.motivo_reprovacao_viewset import MotivoReprovacaoViewSet

pytestmark = pytest.mark.django_db


def test_view_set(motivo_reprovacao_x, fake_user):
    request = APIRequestFactory().get("")
    detalhe = MotivoReprovacaoViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = detalhe(request, uuid=motivo_reprovacao_x.uuid)

    assert response.status_code == status.HTTP_200_OK
