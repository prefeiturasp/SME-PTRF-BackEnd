import json

import pytest

from datetime import date

from rest_framework import status

from ....models import SolicitacaoAcertoLancamento

pytestmark = pytest.mark.django_db


def test_api_post_solicitacoes_acerto_em_lote(
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
):
    payload = {
        'analise_prestacao': f'{analise_prestacao_conta_2020_1_em_analise.uuid}',
        'lancamentos': [
            {
                'tipo_lancamento': 'CREDITO',
                'lancamento_uuid': f'{receita_2020_1_ptrf_repasse_conferida.uuid}',
            },
            {
                'tipo_lancamento': 'GASTO',
                'lancamento_uuid': f'{despesa_2020_1.uuid}',
            },
        ],
        'solicitacoes_acerto': [
            {
                'uuid': None,
                'copiado': False,
                'tipo_acerto': f'{tipo_acerto_lancamento_basico.uuid}',
                'detalhamento': 'Teste de acerto',
                'devolucao_tesouro': None,
            },
            {
                'uuid': None,
                'copiado': False,
                'tipo_acerto': f'{tipo_acerto_lancamento_devolucao.uuid}',
                'detalhamento': 'Teste devolução ao tesouro',
                'devolucao_tesouro': {
                    'tipo': f'{tipo_devolucao_ao_tesouro_teste.uuid}',
                    'data': f'{date(2021, 8, 27)}',
                    'devolucao_total': False,
                    'valor': 10.00,
                }
            },
        ]
    }

    assert analise_prestacao_conta_2020_1_em_analise.analises_de_lancamentos.count() == 1
    assert not prestacao_conta_2020_1_em_analise.devolucoes_ao_tesouro_da_prestacao.exists()
    assert not SolicitacaoAcertoLancamento.objects.exists()

    url = f'/api/prestacoes-contas/{prestacao_conta_2020_1_em_analise.uuid}/solicitacoes-de-acerto/'
    response = jwt_authenticated_client_a.post(url, data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {'message': 'Solicitações de acerto gravadas para os lançamentos.'}

    assert analise_prestacao_conta_2020_1_em_analise.analises_de_lancamentos.count() == 2
    assert prestacao_conta_2020_1_em_analise.devolucoes_ao_tesouro_da_prestacao.count() == 1
    assert SolicitacaoAcertoLancamento.objects.count() == 3


def test_api_post_solicitacoes_acerto_individual(
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
):
    payload = {
        'analise_prestacao': f'{analise_prestacao_conta_2020_1_em_analise.uuid}',
        'lancamentos': [
            {
                'tipo_lancamento': 'GASTO',
                'lancamento_uuid': f'{despesa_2020_1.uuid}',
            },
        ],
        'solicitacoes_acerto': [
            {
                'uuid': None,
                'copiado': False,
                'tipo_acerto': f'{tipo_acerto_lancamento_basico.uuid}',
                'detalhamento': 'Teste de acerto',
                'devolucao_tesouro': None,
            },
            {
                'uuid': None,
                'copiado': False,
                'tipo_acerto': f'{tipo_acerto_lancamento_devolucao.uuid}',
                'detalhamento': 'Teste devolução ao tesouro',
                'devolucao_tesouro': {
                    'tipo': f'{tipo_devolucao_ao_tesouro_teste.uuid}',
                    'data': f'{date(2021, 8, 27)}',
                    'devolucao_total': False,
                    'valor': 10.00,
                }
            },
        ]
    }

    assert analise_prestacao_conta_2020_1_em_analise.analises_de_lancamentos.count() == 1
    assert not prestacao_conta_2020_1_em_analise.devolucoes_ao_tesouro_da_prestacao.exists()
    assert not SolicitacaoAcertoLancamento.objects.exists()

    url = f'/api/prestacoes-contas/{prestacao_conta_2020_1_em_analise.uuid}/solicitacoes-de-acerto/'
    response = jwt_authenticated_client_a.post(url, data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {'message': 'Solicitações de acerto gravadas para os lançamentos.'}

    assert analise_prestacao_conta_2020_1_em_analise.analises_de_lancamentos.count() == 1
    assert prestacao_conta_2020_1_em_analise.devolucoes_ao_tesouro_da_prestacao.count() == 1
    assert SolicitacaoAcertoLancamento.objects.count() == 2


def test_api_post_solicitacoes_sem_acertos_individual(
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
    payload = {
        'analise_prestacao': f'{analise_prestacao_conta_2020_1_em_analise.uuid}',
        'lancamentos': [
            {
                'tipo_lancamento': 'GASTO',
                'lancamento_uuid': f'{despesa_2020_1.uuid}',
            },
        ],
        'solicitacoes_acerto': []
    }

    assert analise_prestacao_conta_2020_1_em_analise.analises_de_lancamentos.count() == 1
    assert prestacao_conta_2020_1_em_analise.devolucoes_ao_tesouro_da_prestacao.exists()
    assert SolicitacaoAcertoLancamento.objects.count() == 1

    url = f'/api/prestacoes-contas/{prestacao_conta_2020_1_em_analise.uuid}/solicitacoes-de-acerto/'
    response = jwt_authenticated_client_a.post(url, data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {'message': 'Solicitações de acerto gravadas para os lançamentos.'}

    assert analise_prestacao_conta_2020_1_em_analise.analises_de_lancamentos.count() == 1
    assert prestacao_conta_2020_1_em_analise.devolucoes_ao_tesouro_da_prestacao.count() == 0
    assert SolicitacaoAcertoLancamento.objects.count() == 0


def test_api_post_solicitacoes_sem_acertos_em_lote(
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
    analise_lancamento_receita_prestacao_conta_2020_1_em_analise,
    solicitacao_acerto_lancamento_devolucao
):
    payload = {
        'analise_prestacao': f'{analise_prestacao_conta_2020_1_em_analise.uuid}',
        'lancamentos': [
            {
                'tipo_lancamento': 'CREDITO',
                'lancamento_uuid': f'{receita_2020_1_ptrf_repasse_conferida.uuid}',
            },
            {
                'tipo_lancamento': 'GASTO',
                'lancamento_uuid': f'{despesa_2020_1.uuid}',
            },
        ],
        'solicitacoes_acerto': []
    }

    assert analise_prestacao_conta_2020_1_em_analise.analises_de_lancamentos.count() == 2
    assert prestacao_conta_2020_1_em_analise.devolucoes_ao_tesouro_da_prestacao.count() == 1
    assert SolicitacaoAcertoLancamento.objects.count() == 1

    url = f'/api/prestacoes-contas/{prestacao_conta_2020_1_em_analise.uuid}/solicitacoes-de-acerto/'
    response = jwt_authenticated_client_a.post(url, data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {'message': 'Solicitações de acerto gravadas para os lançamentos.'}

    assert analise_prestacao_conta_2020_1_em_analise.analises_de_lancamentos.count() == 2
    assert prestacao_conta_2020_1_em_analise.devolucoes_ao_tesouro_da_prestacao.count() == 1
    assert SolicitacaoAcertoLancamento.objects.count() == 1
