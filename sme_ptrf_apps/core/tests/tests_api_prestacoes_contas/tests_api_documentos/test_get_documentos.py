import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


# def test_api_get_documentos_para_analise(
#     jwt_authenticated_client_a,
#     periodo_2020_1,
#     conta_associacao_cartao,
#     prestacao_conta_2020_1_em_analise,
#     analise_prestacao_conta_2020_1_em_analise,
#     tipo_documento_prestacao_conta_ata,
#     tipo_documento_prestacao_conta_declaracao,
#     analise_documento_prestacao_conta_2020_1_ata_correta,
# ):
#     conta_uuid = conta_associacao_cartao.uuid
#
#     resultado_esperado = [
#         {
#             'tipo_documento_prestacao_conta': {
#                 'uuid': f'{tipo_documento_prestacao_conta_ata.uuid}',
#                 'nome': tipo_documento_prestacao_conta_ata.nome,
#             },
#             'analise_documento': {
#                 'uuid': f'{analise_documento_prestacao_conta_2020_1_ata_correta.uuid}',
#                 'resultado': analise_documento_prestacao_conta_2020_1_ata_correta.resultado,
#             }
#         },
#         {
#             'tipo_documento_prestacao_conta': {
#                 'uuid': f'{tipo_documento_prestacao_conta_declaracao.uuid}',
#                 'nome': tipo_documento_prestacao_conta_declaracao.nome,
#             },
#             'analise_documento': None
#         },
#     ]
#
#     url = f'/api/prestacoes-contas/{prestacao_conta_2020_1_em_analise.uuid}/documentos/?analise_prestacao={analise_prestacao_conta_2020_1_em_analise.uuid}'
#
#     response = jwt_authenticated_client_a.get(url, content_type='application/json')
#
#     result = json.loads(response.content)
#
#     assert response.status_code == status.HTTP_200_OK
#     assert result == resultado_esperado, "Não retornou a lista de documentos esperados."
