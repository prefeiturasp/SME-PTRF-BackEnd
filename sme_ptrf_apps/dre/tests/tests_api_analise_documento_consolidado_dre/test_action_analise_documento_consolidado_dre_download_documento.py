import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_action_analise_documento_consolidado_dre_download_documentos(
    jwt_authenticated_client_sme,
    analise_documento_consolidado_dre_teste_download_documentos,
    dre_teste_analise_documento_consolidado_dre_teste_download_documentos,
    relatorio_dre_consolidado_gerado_final_teste_api,
    ano_analise_regularidade_2022_teste_api,
    periodo_teste_api_consolidado_dre,
):

    relatorio_uuid = relatorio_dre_consolidado_gerado_final_teste_api.uuid

    url = f'/api/analises-documentos-consolidados-dre/download-documento/?tipo_documento=RELATORIO_CONSOLIDADO&documento_uuid={relatorio_uuid}'

    response = jwt_authenticated_client_sme.get(url)

    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Disposition'][0] == 'attachment; filename=relatorio_fisico_financeiro_dre.pdf'
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Type'][0] == 'application/pdf'
    assert response.status_code == status.HTTP_200_OK



