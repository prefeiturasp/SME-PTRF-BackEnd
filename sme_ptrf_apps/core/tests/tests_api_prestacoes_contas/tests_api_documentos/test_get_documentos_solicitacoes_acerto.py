import json

import pytest

from rest_framework import status


pytestmark = pytest.mark.django_db


def test_api_get_solicitacoes_acerto_de_um_documento_nao_por_conta(
    jwt_authenticated_client_a,
    tipo_documento_prestacao_conta_ata,
    tipo_acerto_documento_assinatura,
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    solicitacao_acerto_documento_ata
):
    analise_prestacao = analise_documento_prestacao_conta_2020_1_ata_ajuste.analise_prestacao_conta
    prestacao_conta = analise_prestacao.prestacao_conta

    resultado_esperado = {
        'uuid': f'{analise_documento_prestacao_conta_2020_1_ata_ajuste.uuid}',
        'id': analise_documento_prestacao_conta_2020_1_ata_ajuste.id,
        'status_realizacao': 'PENDENTE',
        'resultado': 'AJUSTE',
        'conta_associacao': None,
        'analise_prestacao_conta': f'{analise_prestacao.uuid}',
        'documento': 'Cópia da ata da prestação de contas',
        'tipo_documento_prestacao_conta': {
            'uuid': f'{tipo_documento_prestacao_conta_ata.uuid}',
            'id': tipo_documento_prestacao_conta_ata.id,
            'nome': tipo_documento_prestacao_conta_ata.nome,
            'documento_por_conta': False,
        },
        'solicitacoes_de_ajuste_da_analise': [
            {
                'analise_documento': f'{analise_documento_prestacao_conta_2020_1_ata_ajuste.uuid}',
                'copiado': False,
                'detalhamento': '',
                'texto_do_acerto_do_tipo_edicao_de_informacao': '',
                'tipo_acerto': {
                    'ativo': tipo_acerto_documento_assinatura.ativo,
                    'categoria': tipo_acerto_documento_assinatura.categoria,
                    'id': tipo_acerto_documento_assinatura.id,
                    'nome': 'Enviar com assinatura',
                    'uuid': f'{tipo_acerto_documento_assinatura.uuid}',
                    'tipos_documento_prestacao': [tipo_documento_prestacao_conta_ata.id]
                },
                'esclarecimentos': None,
                'id': solicitacao_acerto_documento_ata.id,
                'justificativa': None,
                'status_realizacao': 'PENDENTE',
                'uuid': f'{solicitacao_acerto_documento_ata.uuid}'
            },
        ],
        'requer_ajuste_externo': False,
        'requer_edicao_informacao_conciliacao': False,
        'requer_esclarecimentos': True,
        'requer_inclusao_credito': False,
        'requer_inclusao_gasto': False,
        'solicitacoes_de_ajuste_da_analise_total': 1
    }

    url = f'/api/prestacoes-contas/{prestacao_conta.uuid}/analises-de-documento/?analise_documento={analise_documento_prestacao_conta_2020_1_ata_ajuste.uuid}'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_get_solicitacoes_acerto_de_um_documento_por_conta(
    jwt_authenticated_client_a,
    analise_documento_prestacao_conta_2020_1_declaracao_cartao_ajuste,
):
    analise_prestacao = analise_documento_prestacao_conta_2020_1_declaracao_cartao_ajuste.analise_prestacao_conta
    prestacao_conta = analise_prestacao.prestacao_conta

    uuid_esperado = f'{analise_documento_prestacao_conta_2020_1_declaracao_cartao_ajuste.uuid}'

    url = f'/api/prestacoes-contas/{prestacao_conta.uuid}/analises-de-documento/?analise_documento={analise_documento_prestacao_conta_2020_1_declaracao_cartao_ajuste.uuid}'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)
    result_uuid = result['uuid']

    assert response.status_code == status.HTTP_200_OK
    assert result_uuid == uuid_esperado
