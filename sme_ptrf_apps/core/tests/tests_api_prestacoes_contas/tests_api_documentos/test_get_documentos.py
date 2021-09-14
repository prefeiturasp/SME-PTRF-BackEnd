import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_documentos_para_analise(
    jwt_authenticated_client_a,
    periodo_2020_1,
    conta_associacao_cartao,
    tipo_documento_prestacao_conta_ata,
    tipo_documento_prestacao_conta_declaracao,
    analise_documento_prestacao_conta_2020_1_ata_correta,
    analise_documento_prestacao_conta_2020_1_declaracao_cartao_correta,
    conta_associacao_cheque,
    tipo_conta_carteira  # Não pode ser listada
):

    analise_pc = analise_documento_prestacao_conta_2020_1_ata_correta.analise_prestacao_conta
    prestacao_conta = analise_pc.prestacao_conta

    resultado_esperado = [
        {
            'tipo_documento_prestacao_conta': {
                'uuid': f'{tipo_documento_prestacao_conta_ata.uuid}',
                'nome': tipo_documento_prestacao_conta_ata.nome,
                'documento_por_conta': False,
                'conta_associacao': None,
            },
            'analise_documento': {
                'uuid': f'{analise_documento_prestacao_conta_2020_1_ata_correta.uuid}',
                'resultado': analise_documento_prestacao_conta_2020_1_ata_correta.resultado,
                'tipo_conta': None,
                'conta_associacao': None,
            }
        },
        {
            'tipo_documento_prestacao_conta': {
                'uuid': f'{tipo_documento_prestacao_conta_declaracao.uuid}',
                'nome': f'{tipo_documento_prestacao_conta_declaracao.nome} Cartão',
                'documento_por_conta': True,
                'conta_associacao': f'{conta_associacao_cartao.uuid}',
            },
            'analise_documento': {
                'uuid': f'{analise_documento_prestacao_conta_2020_1_declaracao_cartao_correta.uuid}',
                'resultado': analise_documento_prestacao_conta_2020_1_declaracao_cartao_correta.resultado,
                'tipo_conta': 'Cartão',
                'conta_associacao': f'{conta_associacao_cartao.uuid}',
            }
        },
        {
            'tipo_documento_prestacao_conta': {
                'uuid': f'{tipo_documento_prestacao_conta_declaracao.uuid}',
                'nome': f'{tipo_documento_prestacao_conta_declaracao.nome} Cheque',
                'documento_por_conta': True,
                'conta_associacao': f'{conta_associacao_cheque.uuid}',
            },
            'analise_documento': None
        },
    ]

    url = f'/api/prestacoes-contas/{prestacao_conta.uuid}/documentos/?analise_prestacao={analise_pc.uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado, "Não retornou a lista de documentos esperados."
