import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_list_analise_documento_consolidado_dre(
    jwt_authenticated_client_sme_teste_analise_documento_consolidado_dre,
    analise_consolidado_dre_01,
    documento_adicional_consolidado_dre_01,
    relatorio_consolidado_dre_01,
    ata_parecer_tecnico_consolidado_dre_01,
    analise_documento_consolidado_dre_01,
    analise_documento_consolidado_dre_02,
):
    response = jwt_authenticated_client_sme_teste_analise_documento_consolidado_dre.get(
        f'/api/analises-documentos-consolidados-dre/{analise_documento_consolidado_dre_01.uuid}/',
        content_type='application/json'
    )


    result = json.loads(response.content)

    esperado = {
            "analise_consolidado_dre": f"{analise_consolidado_dre_01.uuid}",
            "ata_parecer_tecnico": None,
            "documento_adicional": None,
            "relatorio_consolidao_dre": f"{relatorio_consolidado_dre_01.uuid}",
            "detalhamento": "",
            "resultado": "CORRETO",
            "uuid": f"{analise_documento_consolidado_dre_01.uuid}"
        }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
