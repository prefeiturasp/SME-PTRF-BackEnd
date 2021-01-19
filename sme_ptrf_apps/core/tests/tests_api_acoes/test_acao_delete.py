import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import Acao

pytestmark = pytest.mark.django_db


def test_delete_acao(
    jwt_authenticated_client_a,
    acao_x
):
    assert Acao.objects.filter(uuid=acao_x.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/acoes/{acao_x.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Acao.objects.filter(uuid=acao_x.uuid).exists()
