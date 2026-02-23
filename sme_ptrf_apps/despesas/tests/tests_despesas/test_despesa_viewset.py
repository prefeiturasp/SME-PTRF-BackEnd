import pytest

from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.despesas_viewset import DespesasViewSet


pytestmark = pytest.mark.django_db


def test_view_set(despesa, rateio_despesa_instalacao_eletrica_ptrf, usuario_permissao_despesa, recurso_legado):
    request = APIRequestFactory().get("")
    request.recurso = recurso_legado
    detalhe = DespesasViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_despesa)
    response = detalhe(request, uuid=despesa.uuid)
    assert response.status_code == status.HTTP_200_OK
