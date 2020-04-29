import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.fornecedores_viewset import FornecedoresViewSet

pytestmark = pytest.mark.django_db


def test_view_set(fornecedor_jose, fake_user):
    request = APIRequestFactory().get("")
    detalhe = FornecedoresViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = detalhe(request, pk=fornecedor_jose.pk)

    assert response.status_code == status.HTTP_200_OK
