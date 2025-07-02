import json

import pytest

from datetime import date

from rest_framework import status

from ....models import SolicitacaoAcertoLancamento, SolicitacaoDevolucaoAoTesouro

import sme_ptrf_apps.core.services.prestacao_contas_services as prestacao_contas_services

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
    assert prestacao_conta_2020_1_em_analise.devolucoes_ao_tesouro_da_prestacao.count() == 0
    assert SolicitacaoDevolucaoAoTesouro.objects.count() == 1
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
    assert prestacao_conta_2020_1_em_analise.devolucoes_ao_tesouro_da_prestacao.count() == 0
    assert SolicitacaoDevolucaoAoTesouro.objects.count() == 1
    assert SolicitacaoAcertoLancamento.objects.count() == 2


@pytest.mark.django_db
def test_api_post_solicitacoes_acerto_individual_rollback_em_falha_criar_solicitacao_devolucao_tesouro(
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
    monkeypatch,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
):
    def mock_create_fail(*args, **kwargs):
        raise IntegrityError("Erro simulado na criação da devolução ao tesouro")

    monkeypatch.setattr(
        SolicitacaoDevolucaoAoTesouro.objects,
        "create",
        mock_create_fail
    )

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
                'detalhamento': 'Teste devolução com erro',
                'devolucao_tesouro': {
                    'tipo': f'{tipo_devolucao_ao_tesouro_teste.uuid}',
                    'data': f'{date(2021, 8, 27)}',
                    'devolucao_total': False,
                    'valor': 10.00,
                }
            },
        ]
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_2020_1_em_analise.uuid}/solicitacoes-de-acerto/'
    response = jwt_authenticated_client_a.post(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert SolicitacaoDevolucaoAoTesouro.objects.count() == 0
    assert SolicitacaoAcertoLancamento.objects.count() == 0


@pytest.mark.django_db
def test_api_post_solicitacoes_acerto_individual_rollback_em_falha_criar_solicitacao_acerto_lancamento(
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
    monkeypatch,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
):
    def mock_create_fail(*args, **kwargs):
        raise IntegrityError("Erro simulado na criação do acerto")

    monkeypatch.setattr(
        SolicitacaoAcertoLancamento.objects,
        "create",
        mock_create_fail
    )

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
                'detalhamento': 'Acerto que vai falhar',
                'devolucao_tesouro': None,
            },
            {
                'uuid': None,
                'copiado': False,
                'tipo_acerto': f'{tipo_acerto_lancamento_devolucao.uuid}',
                'detalhamento': 'Devolução deveria ser descartada por rollback',
                'devolucao_tesouro': {
                    'tipo': f'{tipo_devolucao_ao_tesouro_teste.uuid}',
                    'data': f'{date(2021, 8, 27)}',
                    'devolucao_total': False,
                    'valor': 10.00,
                }
            },
        ]
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_2020_1_em_analise.uuid}/solicitacoes-de-acerto/'
    response = jwt_authenticated_client_a.post(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert SolicitacaoAcertoLancamento.objects.count() == 0
    assert SolicitacaoDevolucaoAoTesouro.objects.count() == 0


@pytest.mark.django_db
def test_api_post_solicitacoes_acerto_individual_erro_analise_lancamento_nao_encontrada(
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
    monkeypatch,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
):
    monkeypatch.setattr(
        prestacao_contas_services,
        "__get_analise_lancamento",
        lambda *args, **kwargs: None
    )

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
                'detalhamento': 'Vai falhar por ausência de análise',
                'devolucao_tesouro': None,
            },
        ]
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_2020_1_em_analise.uuid}/solicitacoes-de-acerto/'
    response = jwt_authenticated_client_a.post(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert SolicitacaoAcertoLancamento.objects.count() == 0
    assert SolicitacaoDevolucaoAoTesouro.objects.count() == 0
    

@pytest.mark.django_db
def test_api_post_solicitacoes_acerto_individual_erro_em_criacao_analise_lancamento(
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
    monkeypatch,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
):
    monkeypatch.setattr(
        prestacao_contas_services,
        "__get_analise_lancamento",
        lambda *args, **kwargs: None
    )

    def mock_cria_analise_lancamento(*args, **kwargs):
        raise IntegrityError("Falha simulada na criação da análise de lançamento")

    monkeypatch.setattr(
        prestacao_contas_services,
        "__cria_analise_lancamento_solicitacao_acerto",
        mock_cria_analise_lancamento
    )

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
                'detalhamento': 'Erro esperado na criação da análise',
                'devolucao_tesouro': None,
            },
        ]
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_2020_1_em_analise.uuid}/solicitacoes-de-acerto/'
    response = jwt_authenticated_client_a.post(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert SolicitacaoAcertoLancamento.objects.count() == 0
    assert SolicitacaoDevolucaoAoTesouro.objects.count() == 0


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
    solicitacao_acerto_lancamento_devolucao,
    solicitacao_devolucao_ao_tesouro
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
    assert SolicitacaoDevolucaoAoTesouro.objects.count() == 1

    url = f'/api/prestacoes-contas/{prestacao_conta_2020_1_em_analise.uuid}/solicitacoes-de-acerto/'
    response = jwt_authenticated_client_a.post(url, data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {'message': 'Solicitações de acerto gravadas para os lançamentos.'}

    assert analise_prestacao_conta_2020_1_em_analise.analises_de_lancamentos.count() == 1
    assert prestacao_conta_2020_1_em_analise.devolucoes_ao_tesouro_da_prestacao.count() == 1
    assert SolicitacaoAcertoLancamento.objects.count() == 0
    assert SolicitacaoDevolucaoAoTesouro.objects.count() == 0


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
