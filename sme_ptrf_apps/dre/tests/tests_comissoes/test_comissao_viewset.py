import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.comissoes_viewset import ComissoesViewSet

pytestmark = pytest.mark.django_db


def test_view_set(comissao_exame_contas, fake_user):
    request = APIRequestFactory().get("")
    detalhe = ComissoesViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = detalhe(request, uuid=comissao_exame_contas.uuid)

    assert response.status_code == status.HTTP_200_OK
