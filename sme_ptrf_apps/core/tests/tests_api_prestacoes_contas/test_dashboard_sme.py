import json

import pytest
from rest_framework import status
from model_bakery import baker

pytestmark = pytest.mark.django_db


@pytest.fixture
def prestacao_conta_em_analise(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        status="EM_ANALISE"
    )


@pytest.fixture
def prestacao_conta_aprovada(periodo, outra_associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=outra_associacao,
        status="APROVADA"
    )


@pytest.fixture
def associacao_3(unidade, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Terceira',
        cnpj='52.302.275/0001-00',
        unidade=unidade,
        periodo_inicial=periodo_anterior,
    )


@pytest.fixture
def prestacao_conta_aprovada_ressalva(periodo, associacao_3):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao_3,
        status="APROVADA_RESSALVA"
    )


@pytest.fixture
def _unidade_que_nao_apresentou_pc(dre):
    return baker.make(
        'Unidade',
        codigo_eol="000102",
        tipo_unidade="CEU",
        nome="Codorna",
        sigla="",
        dre=dre,
    )


@pytest.fixture
def _unidade_c_dre_1_ceu(dre):
    return baker.make(
        'Unidade',
        codigo_eol="000545",
        tipo_unidade="CEU",
        nome="Codorna",
        sigla="",
        dre=dre,
    )


@pytest.fixture
def _associacao_c_dre_1(_unidade_c_dre_1_ceu, periodo, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Cuba',
        cnpj='88.102.703/0001-55',
        unidade=_unidade_c_dre_1_ceu,
        periodo_inicial=periodo_anterior
    )


@pytest.fixture
def prestacao_conta_nao_recebida(periodo, _associacao_c_dre_1):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=_associacao_c_dre_1,
        status="NAO_RECEBIDA"
    )


@pytest.fixture
def _associacao_que_nao_apresentou_pc1(_unidade_que_nao_apresentou_pc, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Cuba',
        cnpj='88.102.703/0001-79',
        unidade=_unidade_que_nao_apresentou_pc,
        periodo_inicial=periodo_anterior
    )


def test_dashboard_sme(
    jwt_authenticated_client_a,
    prestacao_conta_aprovada,
    prestacao_conta_em_analise,
    prestacao_conta_aprovada_ressalva,
    prestacao_conta_nao_recebida,
    periodo,
    dre,
    _associacao_que_nao_apresentou_pc1
):
    response = jwt_authenticated_client_a.get(
        f"/api/prestacoes-contas/dashboard-sme/?periodo={periodo.uuid}")
    result = response.json()

    esperado = {
        'cards': [
            {
                'titulo': 'Total de unidades educacionais',
                'quantidade_prestacoes': 5,
                'status': 'TOTAL_UNIDADES'},
            {
                'titulo': 'Prestações de contas não recebidas',
                'quantidade_prestacoes': 2,  # Uma PC não recebida + Uma Associação sem PC.
                'status': 'NAO_RECEBIDA'},
            {
                'titulo': 'Prestações de contas recebidas aguardando análise',
                'quantidade_prestacoes': 0,
                'status': 'RECEBIDA'},
            {
                'titulo': 'Prestações de contas em análise',
                'quantidade_prestacoes': 1,
                'status': 'EM_ANALISE'},
            {
                'titulo': 'Prestações de conta devolvidas para acertos',
                'quantidade_prestacoes': 0,
                'status': 'DEVOLVIDA'},
            {
                'titulo': 'Prestações de contas aprovadas',
                'quantidade_prestacoes': 1,
                'status': 'APROVADA'},
            {
                'titulo': 'Prestações de contas aprovadas com ressalvas',
                'quantidade_prestacoes': 1,
                'status': 'APROVADA_RESSALVA'},
            {
                'titulo': 'Prestações de contas reprovadas',
                'quantidade_prestacoes': 0,
                'status': 'REPROVADA'}
        ],
        'status': {
            'cor_idx': 0,
            'status_txt': 'Período em andamento para DREs e aberto para validações.'
        }
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_dashboard_sme_periodo_sem_pendencias_nas_dres(jwt_authenticated_client_a, prestacao_conta_aprovada,
                                                       prestacao_conta_em_analise,
                                                       periodo_2020_1, dre):
    response = jwt_authenticated_client_a.get(
        f"/api/prestacoes-contas/dashboard-sme/?periodo={periodo_2020_1.uuid}")
    result = response.json()

    esperado = {
        'cards': [
            {
                'titulo': 'Total de unidades educacionais',
                'quantidade_prestacoes': 5,
                'status': 'TOTAL_UNIDADES'},
            {
                'titulo': 'Prestações de contas não recebidas',
                'quantidade_prestacoes': 5,
                'status': 'NAO_APRESENTADAS'},
            {
                'titulo': 'Prestações de contas aprovadas',
                'quantidade_prestacoes': 0,
                'status': 'APROVADA'},
            {
                'titulo': 'Prestações de contas aprovadas com ressalvas',
                'quantidade_prestacoes': 0,
                'status': 'APROVADA_RESSALVA'},
            {
                'titulo': 'Prestações de contas reprovadas',
                'quantidade_prestacoes': 0,
                'status': 'REPROVADA'}
        ],
        'status': {
            'cor_idx': 1,
            'status_txt': 'Período concluído.'
        }
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
