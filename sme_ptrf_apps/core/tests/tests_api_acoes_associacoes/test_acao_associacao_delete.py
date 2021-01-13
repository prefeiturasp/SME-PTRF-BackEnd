import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import AcaoAssociacao

pytestmark = pytest.mark.django_db


def test_delete_acao_associacao(
    jwt_authenticated_client_a,
    acao_associacao_charli_bravo_000086_x
):
    assert AcaoAssociacao.objects.filter(uuid=acao_associacao_charli_bravo_000086_x.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/acoes-associacoes/{acao_associacao_charli_bravo_000086_x.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not AcaoAssociacao.objects.filter(uuid=acao_associacao_charli_bravo_000086_x.uuid).exists()
