import json

import pytest

from rest_framework import status


pytestmark = pytest.mark.django_db


def test_api_get_solicitacoes_acerto_de_um_lancamento(
    jwt_authenticated_client_a,
    despesa_2020_1,
    rateio_despesa_2020_role_conferido,
    rateio_despesa_2020_ptrf_conferido,
    rateio_despesa_2020_role_cheque_conferido,
    rateio_despesa_2020_role_nao_conferido,
    periodo_2020_1,
    conta_associacao_cartao,
    receita_2020_1_ptrf_repasse_conferida,
    receita_2020_1_role_outras_nao_conferida,
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    tipo_acerto_lancamento_basico,
    tipo_acerto_lancamento_devolucao,
    tipo_devolucao_ao_tesouro_teste,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
    solicitacao_acerto_lancamento_devolucao
):
    resultado_esperado = {
        'analise_prestacao_conta': f'{analise_prestacao_conta_2020_1_em_analise.uuid}',
        'tipo_lancamento': 'GASTO',
        'despesa': f'{despesa_2020_1.uuid}',
        'receita': None,
        'resultado': 'CORRETO',
        'devolucao_tesouro_atualizada': False,
        'requer_atualizacao_devolucao_ao_tesouro': True,
        'requer_atualizacao_lancamento': False,
        'lancamento_atualizado': False,
        'requer_exclusao_lancamento': False,
        'lancamento_excluido': False,
        'requer_ajustes_externos': False,
        'requer_esclarecimentos': False,
        'esclarecimentos': None,
        'solicitacoes_de_ajuste_da_analise': [
            {
                'analise_lancamento': f'{analise_lancamento_despesa_prestacao_conta_2020_1_em_analise.uuid}',
                'copiado': False,
                'detalhamento': 'teste',
                'devolucao_ao_tesouro': {
                    'data': '2020-07-01',
                    'despesa': {
                        'associacao': f'{despesa_2020_1.associacao.uuid}',
                        'cpf_cnpj_fornecedor': '11.478.276/0001-04',
                        'data_documento': '2020-03-10',
                        'data_transacao': '2020-03-10',
                        'documento_transacao': '',
                        'nome_fornecedor': 'Fornecedor '
                                           'SA',
                        'numero_documento': '123456',
                        'tipo_documento': {'id': despesa_2020_1.tipo_documento.id, 'nome': 'NFe'},
                        'tipo_transacao': {'id': despesa_2020_1.tipo_transacao.id, 'nome': 'Boleto', 'tem_documento': False},
                        'uuid': f'{despesa_2020_1.uuid}',
                        'valor_ptrf': 90.0,
                        'valor_total': '100.00'
                    },
                    'devolucao_total': False,
                    'motivo': 'teste',
                    'prestacao_conta': f'{prestacao_conta_2020_1_em_analise.uuid}',
                    'tipo': {'id': solicitacao_acerto_lancamento_devolucao.devolucao_ao_tesouro.tipo.id,
                             'nome': 'Devolução '
                                     'teste',
                             'uuid': f'{solicitacao_acerto_lancamento_devolucao.devolucao_ao_tesouro.tipo.uuid}'},
                    'uuid': f'{solicitacao_acerto_lancamento_devolucao.devolucao_ao_tesouro.uuid}',
                    'valor': '100.00',
                    'visao_criacao': 'DRE'
                },
                'id': solicitacao_acerto_lancamento_devolucao.id,
                'tipo_acerto': {'ativo': True,
                                'categoria': 'DEVOLUCAO',
                                'id': tipo_acerto_lancamento_devolucao.id,
                                'nome': 'Devolução',
                                'uuid': f'{tipo_acerto_lancamento_devolucao.uuid}'},
                'uuid': f'{solicitacao_acerto_lancamento_devolucao.uuid}'
            }
        ],
        'id': analise_lancamento_despesa_prestacao_conta_2020_1_em_analise.id,
        'justificativa': None,
        'status_realizacao': 'PENDENTE',
        'uuid': f'{analise_lancamento_despesa_prestacao_conta_2020_1_em_analise.uuid}'
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_2020_1_em_analise.uuid}/analises-de-lancamento/?analise_lancamento={analise_lancamento_despesa_prestacao_conta_2020_1_em_analise.uuid}'
    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
