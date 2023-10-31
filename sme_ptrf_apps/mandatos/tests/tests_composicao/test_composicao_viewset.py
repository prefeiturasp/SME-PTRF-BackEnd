import pytest
from rest_framework import status
from waffle.testutils import override_flag
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views import ComposicoesViewSet

pytestmark = pytest.mark.django_db


@override_flag('historico-de-membros', active=True)
def test_view_set(composicao_01_2023_a_2025, usuario_permissao_sme):
    request = APIRequestFactory().get('')
    detalhe = ComposicoesViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_sme)
    response = detalhe(request, uuid=composicao_01_2023_a_2025.uuid)
    assert response.status_code == status.HTTP_200_OK
