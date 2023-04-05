import json

import pytest
from rest_framework import status
from model_bakery import baker

pytestmark = pytest.mark.django_db


@pytest.fixture
def _dre_teste_1():
    return baker.make('Unidade', codigo_eol='111111', tipo_unidade='DRE', nome='DRE 1', sigla='D1')


@pytest.fixture
def _unidade_1(dre):
    return baker.make(
        'Unidade',
        nome='Escola Teste',
        tipo_unidade='CEU',
        codigo_eol='222222',
        dre=dre,
    )


@pytest.fixture
def _associacao_1(_unidade_1, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-83',
        unidade=_unidade_1,
        periodo_inicial=periodo_anterior,
    )


@pytest.fixture
def _unidade_2(dre):
    return baker.make(
        'Unidade',
        nome='Escola Teste 2',
        tipo_unidade='CEU',
        codigo_eol='333333',
        dre=dre,
    )


@pytest.fixture
def _associacao_2(_unidade_2, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Outra',
        cnpj='52.302.275/0001-99',
        unidade=_unidade_2,
        periodo_inicial=periodo_anterior,
    )


@pytest.fixture
def _prestacao_conta_em_analise(periodo, _associacao_1):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=_associacao_1,
        status="EM_ANALISE"
    )


@pytest.fixture
def _prestacao_conta_aprovada(periodo, _associacao_2):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=_associacao_2,
        status="APROVADA"
    )


@pytest.fixture
def _unidade_3(dre):
    return baker.make(
        'Unidade',
        nome='Escola Teste 3',
        tipo_unidade='CEU',
        codigo_eol='444444',
        dre=dre,
    )


@pytest.fixture
def _associacao_3(_unidade_3, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Terceira',
        cnpj='52.302.275/0001-00',
        unidade=_unidade_3,
        periodo_inicial=periodo_anterior,
    )


@pytest.fixture
def _prestacao_conta_aprovada_ressalva(periodo, _associacao_3):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=_associacao_3,
        status="APROVADA_RESSALVA"
    )


@pytest.fixture
def _unidade_que_nao_apresentou_pc(dre):
    return baker.make(
        'Unidade',
        codigo_eol="666666",
        tipo_unidade="CEU",
        nome="Codorna",
        sigla="",
        dre=dre,
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


@pytest.fixture
def _unidade_c_dre_teste_1_ceu(dre):
    return baker.make(
        'Unidade',
        codigo_eol="777777",
        tipo_unidade="CEU",
        nome="Codorna",
        sigla="",
        dre=dre,
    )


@pytest.fixture
def _associacao_c_dre_teste_1(_unidade_c_dre_teste_1_ceu, periodo, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Cuba',
        cnpj='88.102.703/0001-55',
        unidade=_unidade_c_dre_teste_1_ceu,
        periodo_inicial=periodo_anterior
    )


@pytest.fixture
def _prestacao_conta_nao_recebida(periodo, _associacao_c_dre_teste_1):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=_associacao_c_dre_teste_1,
        status="NAO_RECEBIDA"
    )



@pytest.fixture
def _dre_2():
    return baker.make('Unidade', codigo_eol='888888', tipo_unidade='DRE', nome='DRE 2', sigla='D2')


@pytest.fixture
def _unidade_x_dre_2_ceu(_dre_2):
    return baker.make(
        'Unidade',
        codigo_eol="999999",
        tipo_unidade="CEU",
        nome="Xingu",
        sigla="",
        dre=_dre_2,
    )

@pytest.fixture
def _associacao_x_dre_2(_unidade_x_dre_2_ceu, periodo, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Xua',
        cnpj='67.137.467/0001-59',
        unidade=_unidade_x_dre_2_ceu,
        periodo_inicial=periodo_anterior
    )


def test_dashboard_sme(
    jwt_authenticated_client_a,
    _prestacao_conta_aprovada,
    _prestacao_conta_em_analise,
    _prestacao_conta_aprovada_ressalva,
    _prestacao_conta_nao_recebida,
    periodo,
    _associacao_que_nao_apresentou_pc1,
    _associacao_x_dre_2,

):
    response = jwt_authenticated_client_a.get(
        f"/api/prestacoes-contas/dashboard-sme/?periodo={periodo.uuid}")
    result = response.json()

    esperado = {
        'cards': [
            {
                'titulo': 'Total de unidades educacionais',
                'quantidade_prestacoes': 6,
                'status': 'TOTAL_UNIDADES'},
            {
                'titulo': 'Prestações de contas não recebidas',
                'quantidade_prestacoes': 3,  # Uma PC não recebida + Duas Associações sem PC.
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
            'cor_idx': 1,
            'status_txt': 'Período de análise das prestações de contas pelas DREs em andamento.',
            'status': 'EM_ANDAMENTO'
        },
        'resumo_por_dre': [
            {
                'cards': {
                    'APROVADA': 0,
                    'APROVADA_RESSALVA': 0,
                    'DEVOLVIDA': 0,
                    'EM_ANALISE': 0,
                    'NAO_APRESENTADA': 1,
                    'NAO_RECEBIDA': 1,
                    'RECEBIDA': 0,
                    'REPROVADA': 0,
                    'TOTAL_UNIDADES': 1
                },
                'dre': {
                    'uuid': f'{_associacao_x_dre_2.unidade.dre.uuid}',
                    'sigla': 'D2',
                    'nome': 'DRE 2',
                },
                'periodo_completo': True
            },
            {
                'dre': {
                    'uuid': f'{_prestacao_conta_aprovada.associacao.unidade.dre.uuid}',
                    'sigla': 'TT',
                    'nome': 'DRE teste'
                },
                'cards': {
                    'APROVADA': 1,
                    'APROVADA_RESSALVA': 1,
                    'DEVOLVIDA': 0,
                    'EM_ANALISE': 1,
                    'NAO_APRESENTADA': 1,
                    'NAO_RECEBIDA': 2,
                    'RECEBIDA': 0,
                    'REPROVADA': 0,
                    'TOTAL_UNIDADES': 5
                },
                'periodo_completo': False,
            }

        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_dashboard_sme_periodo_sem_pendencias_nas_dres(jwt_authenticated_client_a, _prestacao_conta_aprovada,
                                                       _prestacao_conta_em_analise,
                                                       periodo_2020_1, dre):
    response = jwt_authenticated_client_a.get(
        f"/api/prestacoes-contas/dashboard-sme/?periodo={periodo_2020_1.uuid}")
    result = response.json()

    esperado = {
        'cards': [
            {
                'titulo': 'Total de unidades educacionais',
                'quantidade_prestacoes': 2,
                'status': 'TOTAL_UNIDADES'},
            {
                'titulo': 'Prestações de contas não apresentadas',
                'quantidade_prestacoes': 2,
                'status': 'NAO_APRESENTADA'},
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
            'cor_idx': 2,
            'status_txt': 'Período de análise das prestações de contas pelas DREs concluído.',
            'status': 'CONCLUIDO'
        },
        'resumo_por_dre': [
            {
                'dre': {
                    'uuid': f'{dre.uuid}',
                    'sigla': 'TT',
                    'nome': 'DRE teste'
                },
                'cards': {
                    'APROVADA': 0,
                    'APROVADA_RESSALVA': 0,
                    'DEVOLVIDA': 0,
                    'EM_ANALISE': 0,
                    'NAO_APRESENTADA': 2,
                    'NAO_RECEBIDA': 2,
                    'RECEBIDA': 0,
                    'REPROVADA': 0,
                    'TOTAL_UNIDADES': 2
                },
                'periodo_completo': True,
            }
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
