import json

import pytest
from rest_framework import status


pytestmark = pytest.mark.django_db


def test_api_list_analise_consolidado(jwt_authenticated_client_sme_teste_analise_documento_consolidado_dre, analise_consolidado_dre_01, relatorio_consolidado_dre_01):
    response = jwt_authenticated_client_sme_teste_analise_documento_consolidado_dre.get(
        f'/api/analises-consolidados-dre/',
    )
    result = json.loads(response.content)
    resultado_esperado = [
        {
            'uuid': str(analise_consolidado_dre_01.uuid),
            'consolidado_dre': str(analise_consolidado_dre_01.consolidado_dre.uuid),
            'analises_de_documentos_da_analise_do_consolidado': list(analise_consolidado_dre_01.analises_de_documentos_da_analise_do_consolidado.all()),
            'data_devolucao': analise_consolidado_dre_01.data_devolucao.strftime('%Y-%m-%d'),
            'data_limite': analise_consolidado_dre_01.data_limite.strftime('%Y-%m-%d'),
            'data_retorno_analise': analise_consolidado_dre_01.data_retorno_analise.strftime('%Y-%m-%d'),
            'comentarios_de_analise_do_consolidado_dre': list(analise_consolidado_dre_01.analises_de_documentos_da_analise_do_consolidado.all()),
            'analises_de_documentos_do_relatorio_consolidao_dre': result[0]['analises_de_documentos_do_relatorio_consolidao_dre'],
            'relatorio_acertos_pdf': analise_consolidado_dre_01.relatorio_acertos_pdf._file,
            'relatorio_acertos_versao': str(analise_consolidado_dre_01.relatorio_acertos_versao),
            'relatorio_acertos_status': analise_consolidado_dre_01.relatorio_acertos_status,
            'relatorio_acertos_gerado_em': analise_consolidado_dre_01.relatorio_acertos_gerado_em.isoformat("T"),
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_list_analise_consolidado_com_campos_divergentes(jwt_authenticated_client_sme_teste_analise_documento_consolidado_dre, analise_consolidado_dre_01, relatorio_consolidado_dre_01):
    response = jwt_authenticated_client_sme_teste_analise_documento_consolidado_dre.get(
        f'/api/analises-consolidados-dre/',
    )
    result = json.loads(response.content)
    resultado_esperado = [
        {
            'uuid': str(analise_consolidado_dre_01.uuid),
            'consolidado_dre': str(analise_consolidado_dre_01.consolidado_dre.uuid),
            'analises_de_documentos_da_analise_do_consolidado': list(analise_consolidado_dre_01.analises_de_documentos_da_analise_do_consolidado.all()),
            'data_devolucao': analise_consolidado_dre_01.data_devolucao.strftime('%Y-%m-%d'),
            'data_limite': analise_consolidado_dre_01.data_limite.strftime('%Y-%m-%d'),
            'data_retorno_analise': analise_consolidado_dre_01.data_retorno_analise.strftime('%Y-%m-%d'),
            'comentarios_de_analise_do_consolidado_dre': list(analise_consolidado_dre_01.analises_de_documentos_da_analise_do_consolidado.all()),
            'analises_de_documentos_do_relatorio_consolidao_dre': result[0]['analises_de_documentos_do_relatorio_consolidao_dre'],
            'relatorio_acertos_pdf': analise_consolidado_dre_01.relatorio_acertos_pdf._file,
            'relatorio_acertos_versao': str(analise_consolidado_dre_01.relatorio_acertos_versao),
            'relatorio_acertos_status': analise_consolidado_dre_01.relatorio_acertos_status,
            'relatorio_acertos_gerado_em': None,
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert not result[0]['relatorio_acertos_gerado_em'] == resultado_esperado[0]['relatorio_acertos_gerado_em']
