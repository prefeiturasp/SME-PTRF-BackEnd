import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import CobrancaPrestacaoConta

pytestmark = pytest.mark.django_db

def test_delete_cobranca_prestacao_conta(jwt_authenticated_client_a, cobranca_prestacao_recebimento):
    assert CobrancaPrestacaoConta.objects.filter(uuid=cobranca_prestacao_recebimento.uuid).exists(), "Deveria já existir"

    response = jwt_authenticated_client_a.delete(
        f'/api/cobrancas-prestacoes-contas/{cobranca_prestacao_recebimento.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not CobrancaPrestacaoConta.objects.filter(uuid=cobranca_prestacao_recebimento.uuid).exists(), "Não foi deletado"
