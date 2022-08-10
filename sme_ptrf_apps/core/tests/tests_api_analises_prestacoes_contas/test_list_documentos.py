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
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    solicitacao_acerto_documento_ata_teste_analises,
    tipo_acerto_documento_assinatura,
    analise_documento_prestacao_conta_2020_1_declaracao_cartao_correta,
    conta_associacao_cheque,
    tipo_conta_carteira,  # Não pode ser listada
    analise_documento_prestacao_conta_2020_1_declaracao_cartao_ajuste,
    solicitacao_acerto_documento_declaracao_cartao_teste_analises,


):

    analise_pc = analise_documento_prestacao_conta_2020_1_ata_ajuste.analise_prestacao_conta
    tipo_acerto_assinatura = tipo_acerto_documento_assinatura

    analise_doc_ata = analise_documento_prestacao_conta_2020_1_ata_ajuste
    tipo_doc_ata = tipo_documento_prestacao_conta_ata
    solicitacao_acerto_ata = solicitacao_acerto_documento_ata_teste_analises

    analise_doc_declaracao = analise_documento_prestacao_conta_2020_1_declaracao_cartao_ajuste
    tipo_doc_declaracao = tipo_documento_prestacao_conta_declaracao
    solicitacao_acerto_declaracao = solicitacao_acerto_documento_declaracao_cartao_teste_analises

    resultado_esperado = [
        {
            'analise_prestacao_conta': f'{analise_pc.uuid}',
            'documento': 'Cópia da ata da prestação de contas',
            'conta_associacao': None,
            'resultado': 'AJUSTE',
            'solicitacoes_de_ajuste_da_analise': [
                {
                    'analise_documento': f'{analise_doc_ata.uuid}',
                    'detalhamento': solicitacao_acerto_declaracao.detalhamento,
                    'tipo_acerto': {
                        'ativo': tipo_acerto_assinatura.ativo,
                        'categoria': tipo_acerto_assinatura.categoria,
                        'nome': 'Enviar com assinatura',
                        'uuid': f'{tipo_acerto_assinatura.uuid}',
                        'id': tipo_acerto_assinatura.id,
                        'tipos_documento_prestacao': [tipo_doc_ata.id]
                    },
                    'uuid': f'{solicitacao_acerto_ata.uuid}',
                    'id': solicitacao_acerto_ata.id,
                }
            ],
            'tipo_documento_prestacao_conta': {
                'documento_por_conta': False,
                'nome': 'Cópia da ata da prestação de contas',
                'uuid': f'{tipo_doc_ata.uuid}',
                'id': tipo_doc_ata.id,
            },
            'uuid': f'{analise_doc_ata.uuid}',
            'id': analise_doc_ata.id,
            'justificativa': None,
            'status_realizacao': 'PENDENTE',
        },
        {
            'analise_prestacao_conta': f'{analise_pc.uuid}',
            'documento': 'Declaração XPTO Cartão',
            'conta_associacao': {
                'nome': 'Cartão',
                'uuid': f'{conta_associacao_cartao.uuid}'
            },
            'resultado': 'AJUSTE',
            'solicitacoes_de_ajuste_da_analise': [
                {
                    'analise_documento': f'{analise_doc_declaracao.uuid}',
                    'detalhamento': '',
                    'tipo_acerto': {
                        'ativo': tipo_acerto_assinatura.ativo,
                        'categoria': tipo_acerto_assinatura.categoria,
                        'nome': 'Enviar com assinatura',
                        'uuid': f'{tipo_acerto_assinatura.uuid}',
                        'id': tipo_acerto_assinatura.id,
                        'tipos_documento_prestacao': [tipo_doc_ata.id]
                    },
                    'uuid': f'{solicitacao_acerto_declaracao.uuid}',
                    'id': solicitacao_acerto_declaracao.id,
                }
            ],
            'tipo_documento_prestacao_conta': {
                'documento_por_conta': True,
                'nome': 'Declaração XPTO',
                'uuid': f'{tipo_doc_declaracao.uuid}',
                'id': tipo_doc_declaracao.id,
            },
            'uuid': f'{analise_doc_declaracao.uuid}',
            'id': analise_doc_declaracao.id,
            'justificativa': None,
            'status_realizacao': 'PENDENTE',
        }
    ]

    url = f'/api/analises-prestacoes-contas/{analise_pc.uuid}/documentos-com-ajuste/?conta_associacao={conta_associacao_cartao.uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado, "Não retornou a lista de documentos esperados."
