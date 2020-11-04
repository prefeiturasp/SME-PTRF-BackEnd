import pytest

from rest_framework import status

from sme_ptrf_apps.dre.models import JustificativaRelatorioConsolidadoDRE

pytestmark = pytest.mark.django_db

def test_delete_cobranca_prestacao_conta(jwt_authenticated_client, justificativa_relatorio_dre_consolidado):
    assert JustificativaRelatorioConsolidadoDRE.objects.filter(uuid=justificativa_relatorio_dre_consolidado.uuid).exists(), "Deveria já existir"

    response = jwt_authenticated_client.delete(
        f'/api/justificativas-relatorios-consolidados-dre/{justificativa_relatorio_dre_consolidado.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not JustificativaRelatorioConsolidadoDRE.objects.filter(uuid=justificativa_relatorio_dre_consolidado.uuid).exists(), "Não foi deletado"
