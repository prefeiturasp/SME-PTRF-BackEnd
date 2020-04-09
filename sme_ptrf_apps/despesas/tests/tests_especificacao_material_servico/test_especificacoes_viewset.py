import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.especificacoes_viewset import EspecificacaoMaterialServicoViewSet

pytestmark = pytest.mark.django_db


def test_view_set(especificacao_material_servico, fake_user):
    request = APIRequestFactory().get("")
    detalhe = EspecificacaoMaterialServicoViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = detalhe(request, id=especificacao_material_servico.id)

    assert response.status_code == status.HTTP_200_OK
