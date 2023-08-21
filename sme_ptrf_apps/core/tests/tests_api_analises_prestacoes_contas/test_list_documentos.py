import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_documentos_para_analise(
    jwt_authenticated_client_a,
    periodo_2020_1,
    conta_associacao_cartao,
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    analise_documento_prestacao_conta_2020_1_declaracao_cartao_ajuste,
):

    analise_pc = analise_documento_prestacao_conta_2020_1_ata_ajuste.analise_prestacao_conta

    analise_doc_ata = analise_documento_prestacao_conta_2020_1_ata_ajuste

    analise_doc_declaracao = analise_documento_prestacao_conta_2020_1_declaracao_cartao_ajuste

    esperado_uuids = [
        f'{analise_doc_ata.uuid}',
        f'{analise_doc_declaracao.uuid}'
    ]

    url = f'/api/analises-prestacoes-contas/{analise_pc.uuid}/documentos-com-ajuste/?conta_associacao={conta_associacao_cartao.uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_uuids = []
    for item in result:
        result_uuids.append(item['uuid'])

    assert response.status_code == status.HTTP_200_OK
    assert result_uuids == esperado_uuids, "Não retornou a lista de documentos esperados."
