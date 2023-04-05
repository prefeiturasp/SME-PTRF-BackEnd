import pytest

from ...api.serializers.analise_consolidado_dre_serializer import AnaliseConsolidadoDreRetriveSerializer

pytestmark = pytest.mark.django_db


def test_serializer(analise_consolidado_dre_01):
    serializer = AnaliseConsolidadoDreRetriveSerializer(analise_consolidado_dre_01)

    result = {
        'alterado_em': serializer.instance.alterado_em,
        'consolidado_dre_id': serializer.instance.consolidado_dre_id,
        'criado_em': serializer.instance.criado_em,
        'data_devolucao': serializer.instance.data_devolucao,
        'data_limite': serializer.instance.data_limite,
        'data_retorno_analise': serializer.instance.data_retorno_analise,
        'id': serializer.instance.id,
        'relatorio_acertos_gerado_em': serializer.instance.relatorio_acertos_gerado_em,
        'relatorio_acertos_pdf': serializer.instance.relatorio_acertos_pdf,
        'relatorio_acertos_status': serializer.instance.relatorio_acertos_status,
        'relatorio_acertos_versao': serializer.instance.relatorio_acertos_versao,
        'uuid': serializer.instance.uuid
    }
    expected_result = {
        'alterado_em': analise_consolidado_dre_01.alterado_em,
        'consolidado_dre_id': analise_consolidado_dre_01.consolidado_dre_id,
        'criado_em': analise_consolidado_dre_01.criado_em,
        'data_devolucao': analise_consolidado_dre_01.data_devolucao,
        'data_limite': analise_consolidado_dre_01.data_limite,
        'data_retorno_analise': analise_consolidado_dre_01.data_retorno_analise,
        'id': analise_consolidado_dre_01.id,
        'relatorio_acertos_gerado_em': analise_consolidado_dre_01.relatorio_acertos_gerado_em,
        'relatorio_acertos_pdf': analise_consolidado_dre_01.relatorio_acertos_pdf,
        'relatorio_acertos_status': analise_consolidado_dre_01.relatorio_acertos_status,
        'relatorio_acertos_versao': analise_consolidado_dre_01.relatorio_acertos_versao,
        'uuid': analise_consolidado_dre_01.uuid
    }

    assert result == expected_result
