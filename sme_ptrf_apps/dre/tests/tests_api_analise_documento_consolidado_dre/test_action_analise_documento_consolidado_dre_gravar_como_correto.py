import json
import pytest
from rest_framework import status

from sme_ptrf_apps.dre.models import AnaliseDocumentoConsolidadoDre

pytestmark = pytest.mark.django_db


def test_action_analise_documento_consolidado_dre_gravar_como_correto_analise_documento_nao_existente(
    jwt_authenticated_client_relatorio_consolidado,
    analise_consolidado_dre_01,
    relatorio_consolidado_dre_01,
):

    assert not AnaliseDocumentoConsolidadoDre.objects.filter(
        analise_consolidado_dre=analise_consolidado_dre_01,
        relatorio_consolidao_dre=relatorio_consolidado_dre_01,
    ).exists()

    payload = {
        "analise_atual_consolidado": f"{analise_consolidado_dre_01.uuid}",
        "documentos":
            [
                {
                    "tipo_documento": "RELATORIO_CONSOLIDADO",
                    "uuid_documento": f"{relatorio_consolidado_dre_01.uuid}"
                },
            ]
    }

    response = jwt_authenticated_client_relatorio_consolidado.patch(
        f'/api/analises-documentos-consolidados-dre/marcar-como-correto/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    result = json.loads(response.content)

    esperado = {
        "mensagem": "Documentos alterados com sucesso!"
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
    analise_documento = AnaliseDocumentoConsolidadoDre.objects.filter(
        analise_consolidado_dre=analise_consolidado_dre_01,
        relatorio_consolidao_dre=relatorio_consolidado_dre_01,
    ).first()
    assert analise_documento
    assert analise_documento.detalhamento == ""
    assert analise_documento.resultado == "CORRETO"


def test_action_analise_documento_consolidado_dre_gravar_como_correto_analise_documento_ja_existente(
    jwt_authenticated_client_relatorio_consolidado,
    analise_consolidado_dre_01,
    relatorio_consolidado_dre_01,
    analise_documento_consolidado_dre_marcar_como_correto_analise_existente,
):
    payload = {
        "analise_atual_consolidado": f"{analise_consolidado_dre_01.uuid}",
        "documentos":
            [
                {
                    "tipo_documento": "RELATORIO_CONSOLIDADO",
                    "uuid_documento": f"{relatorio_consolidado_dre_01.uuid}"
                },
            ]
    }

    response = jwt_authenticated_client_relatorio_consolidado.patch(
        f'/api/analises-documentos-consolidados-dre/marcar-como-correto/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    result = json.loads(response.content)

    esperado = {
        "mensagem": "Documentos alterados com sucesso!"
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
    analise_documento = AnaliseDocumentoConsolidadoDre.objects.filter(
        analise_consolidado_dre=analise_consolidado_dre_01,
        relatorio_consolidao_dre=relatorio_consolidado_dre_01,
    ).first()
    assert analise_documento
    assert analise_documento.detalhamento == ""
    assert analise_documento.resultado == "CORRETO"
