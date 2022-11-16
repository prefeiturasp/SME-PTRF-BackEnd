import json
import pytest
from rest_framework import status

from ...models import AnaliseDocumentoConsolidadoDre

pytestmark = pytest.mark.django_db


def test_update_analise_documento_consolidado_dre(
    jwt_authenticated_client_sme_teste_analise_documento_consolidado_dre,
    analise_consolidado_dre_01,
    documento_adicional_consolidado_dre_01,
    relatorio_consolidado_dre_01,
    ata_parecer_tecnico_consolidado_dre_01,
    analise_documento_consolidado_dre_03,
):

    uuid_analise_documento = f"{analise_documento_consolidado_dre_03.uuid}"

    assert analise_documento_consolidado_dre_03.detalhamento == 'Este é o detalhamento da analise de documento 03'

    response = jwt_authenticated_client_sme_teste_analise_documento_consolidado_dre.delete(
        f'/api/analises-documentos-consolidados-dre/{uuid_analise_documento}/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


