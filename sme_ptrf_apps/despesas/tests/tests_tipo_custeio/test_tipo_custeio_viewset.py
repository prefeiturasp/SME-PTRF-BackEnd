import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from model_bakery import baker
from ...api.views.tipos_custeio_viewset import TiposCusteioViewSet

pytestmark = pytest.mark.django_db

@pytest.fixture
def tipo_custeio_x():
    return baker.make('TipoCusteio', nome='x')


def test_tipo_custeio_view_set(tipo_custeio_x, usuario_permissao_despesa):
    request = APIRequestFactory().get('')
    detalhe = TiposCusteioViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_despesa)
    response = detalhe(request, uuid=tipo_custeio_x.uuid)

    assert response.status_code == status.HTTP_200_OK
