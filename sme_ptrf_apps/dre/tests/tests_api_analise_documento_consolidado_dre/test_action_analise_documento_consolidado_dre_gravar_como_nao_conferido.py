import json
import pytest
from rest_framework import status

from sme_ptrf_apps.dre.models import AnaliseDocumentoConsolidadoDre

pytestmark = pytest.mark.django_db


def test_action_analise_documento_consolidado_dre_gravar_como_correto_nao_conferido_analise_com_ajuste(
    jwt_authenticated_client_relatorio_consolidado,
    analise_consolidado_dre_01,
    relatorio_consolidado_dre_01,
    analise_documento_consolidado_dre_marcar_como_correto_analise_existente,
):

    assert analise_documento_consolidado_dre_marcar_como_correto_analise_existente.resultado == "AJUSTE"

    payload = {
        "analise_atual_consolidado": f"{analise_consolidado_dre_01.uuid}",
        "uuids_analises_documentos": [f"{analise_documento_consolidado_dre_marcar_como_correto_analise_existente.uuid}"]
    }

    response = jwt_authenticated_client_relatorio_consolidado.patch(
        f'/api/analises-documentos-consolidados-dre/marcar-como-nao-conferido/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    result = json.loads(response.content)

    esperado = {
        "mensagem": "Status de documento conferido foi aplicado com sucesso."
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
    assert not AnaliseDocumentoConsolidadoDre.objects.filter(uuid=f"{analise_documento_consolidado_dre_marcar_como_correto_analise_existente.uuid}").first()

