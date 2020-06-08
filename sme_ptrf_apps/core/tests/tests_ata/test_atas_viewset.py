import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.atas_viewset import AtasViewSet

pytestmark = pytest.mark.django_db


def test_view_set(ata_2020_1_cheque_aprovada, fake_user):
    request = APIRequestFactory().get("")
    detalhe = AtasViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = detalhe(request, uuid=ata_2020_1_cheque_aprovada.uuid)

    assert response.status_code == status.HTTP_200_OK
