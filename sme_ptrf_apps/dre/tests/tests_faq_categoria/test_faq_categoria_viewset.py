import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.faq_categorias_viewset import FaqCategoriasViewSet

pytestmark = pytest.mark.django_db


def test_view_set(faq_categoria, fake_user):
    request = APIRequestFactory().get("")
    detalhe = FaqCategoriasViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = detalhe(request, uuid=faq_categoria.uuid)

    assert response.status_code == status.HTTP_200_OK
