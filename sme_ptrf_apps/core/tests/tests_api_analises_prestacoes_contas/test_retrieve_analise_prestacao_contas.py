import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_retrieve_analise_prestacao_contas_existente(
    jwt_authenticated_client_a,
    despesa_2020_1,
    rateio_despesa_2020_role_conferido,
    rateio_despesa_2020_ptrf_conferido,
    rateio_despesa_2020_role_cheque_conferido,
    rateio_despesa_2020_role_nao_conferido,
    receita_2020_1_ptrf_repasse_conferida,
    receita_2020_1_role_outras_nao_conferida,
    solicitacao_acerto_documento_ata_teste_analises,
    solicitacao_acerto_documento_declaracao_cartao_teste_analises,
    solicitacao_acerto_lancamento_devolucao_teste_analises


):
    analise_prestacao = solicitacao_acerto_documento_ata_teste_analises.analise_documento.analise_prestacao_conta

    result_esperado = {
        'criado_em': analise_prestacao.criado_em.isoformat("T"),
        'devolucao_prestacao_conta': {'data': '2020-10-05',
                                      'data_limite_ue': '2020-08-01',
                                      'data_retorno_ue': None,
                                      'prestacao_conta': f'{analise_prestacao.prestacao_conta.uuid}',
                                      'uuid': f'{analise_prestacao.devolucao_prestacao_conta.uuid}'},
        'id': analise_prestacao.id,
        'pode_reprocessar_relatorio_apos_acertos': False,
        'prestacao_conta': f'{analise_prestacao.prestacao_conta.uuid}',
        'status': 'EM_ANALISE',
        'uuid': f'{analise_prestacao.uuid}',
        'versao': analise_prestacao.versao,
        'versao_pdf_apresentacao_apos_acertos': analise_prestacao.versao_pdf_apresentacao_apos_acertos
    }

    url = f'/api/analises-prestacoes-contas/{analise_prestacao.uuid}/'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_retrieve_analise_prestacao_contas_existente_com_falha_geracao_doc_apos_acertos(
    jwt_authenticated_client_a,
    analise_prestacao_conta_2020_1_teste_analises_com_falha_geracao_doc_apos_acertos
):
    analise_prestacao = analise_prestacao_conta_2020_1_teste_analises_com_falha_geracao_doc_apos_acertos

    result_esperado = {
        'criado_em': analise_prestacao.criado_em.isoformat("T"),
        'devolucao_prestacao_conta': {'data': '2020-10-05',
                                      'data_limite_ue': '2020-08-01',
                                      'data_retorno_ue': None,
                                      'prestacao_conta': f'{analise_prestacao.prestacao_conta.uuid}',
                                      'uuid': f'{analise_prestacao.devolucao_prestacao_conta.uuid}'},
        'id': analise_prestacao.id,
        'pode_reprocessar_relatorio_apos_acertos': True,
        'prestacao_conta': f'{analise_prestacao.prestacao_conta.uuid}',
        'status': 'EM_ANALISE',
        'uuid': f'{analise_prestacao.uuid}',
        'versao': analise_prestacao.versao,
        'versao_pdf_apresentacao_apos_acertos': analise_prestacao.versao_pdf_apresentacao_apos_acertos
    }

    url = f'/api/analises-prestacoes-contas/{analise_prestacao.uuid}/'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado
