import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.tipos_devolucao_ao_tesouro_viewset import TiposDevolucaoAoTesouroViewSet

pytestmark = pytest.mark.django_db

@pytest.fixture
def tipo_devolucao_ao_tesouro():
    return baker.make('TipoDevolucaoAoTesouro', nome='Teste')

def test_view_set(tipo_devolucao_ao_tesouro, usuario_permissao_associacao):
    request = APIRequestFactory().get("")
    detalhe = TiposDevolucaoAoTesouroViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=tipo_devolucao_ao_tesouro.uuid)

    assert response.status_code == status.HTTP_200_OK
