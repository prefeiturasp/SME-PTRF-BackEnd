import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.anos_analise_regularidade_viewset import AnosAnaliseRegularidadeViewSet

pytestmark = pytest.mark.django_db


def test_view_set(ano_analise_regularidade_2021, usuario_permissao_atribuicao):
    request = APIRequestFactory().get("")
    detalhe = AnosAnaliseRegularidadeViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_atribuicao)
    response = detalhe(request, ano=ano_analise_regularidade_2021.ano)

    assert response.status_code == status.HTTP_200_OK
