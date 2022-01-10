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


@pytest.fixture
def unidade_devolvida(dre):
    return baker.make(
        'Unidade',
        codigo_eol="190880",
        tipo_unidade="CEU",
        nome="Devolvida",
        sigla="",
        dre=dre,
    )


@pytest.fixture
def associacao_devolvida(unidade_devolvida, periodo, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Devolvida',
        unidade=unidade_devolvida,
        periodo_inicial=periodo_anterior,
        cnpj='38.507.153/0001-00'
    )


@pytest.fixture
def prestacao_conta_devolvida(periodo, associacao_devolvida):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao_devolvida,
        status="DEVOLVIDA"
    )


@pytest.fixture
def unidade_devolvida_retornada(dre):
    return baker.make(
        'Unidade',
        codigo_eol="190881",
        tipo_unidade="CEU",
        nome="Devolvida Retornada",
        sigla="",
        dre=dre,
    )


@pytest.fixture
def associacao_devolvida_retornada(unidade_devolvida_retornada, periodo, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Devolvida Retornada',
        unidade=unidade_devolvida_retornada,
        periodo_inicial=periodo_anterior,
        cnpj='65.375.219/0001-10'
    )


@pytest.fixture
def prestacao_conta_devolvida_retornada(periodo, associacao_devolvida_retornada):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao_devolvida_retornada,
        status="DEVOLVIDA_RETORNADA"
    )

@pytest.fixture
def unidade_devolvida_recebida(dre):
    return baker.make(
        'Unidade',
        codigo_eol="190882",
        tipo_unidade="CEU",
        nome="Devolvida Recebida",
        sigla="",
        dre=dre,
    )


@pytest.fixture
def associacao_devolvida_recebida(unidade_devolvida_recebida, periodo, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Devolvida Recebida',
        unidade=unidade_devolvida_recebida,
        periodo_inicial=periodo_anterior,
        cnpj='43.880.463/0001-06'
    )


@pytest.fixture
def prestacao_conta_devolvida_recebida(periodo, associacao_devolvida_recebida):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao_devolvida_recebida,
        status="DEVOLVIDA_RECEBIDA"
    )


def test_dashboard(
    jwt_authenticated_client_a,
    prestacao_conta_aprovada,
    prestacao_conta_em_analise,
    prestacao_conta_aprovada_ressalva,
    prestacao_conta_nao_recebida,
    prestacao_conta_devolvida,
    prestacao_conta_devolvida_retornada,
    prestacao_conta_devolvida_recebida,
    periodo,
    dre,
    _associacao_que_nao_apresentou_pc1,
):
    response = jwt_authenticated_client_a.get(
        f"/api/prestacoes-contas/dashboard/?periodo={periodo.uuid}&dre_uuid={dre.uuid}")
    result = response.json()

    esperado = {
        'total_associacoes_dre': 8,
        'cards': [
            {
                'titulo': 'Prestações de contas não recebidas',
                'quantidade_nao_recebida': 1,
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
                'quantidade_prestacoes': 3,  # Devolvida + Retornada após acertos + Recebida após acertos
                'quantidade_retornadas': 1,  # Retornada após acertos
                'status': 'DEVOLVIDA'},
            {
                'titulo': 'Prestações de contas aprovadas',
                'quantidade_prestacoes': 2,  # Aprovada + Aprovada com ressalva
                'status': 'APROVADA'},
            {
                'titulo': 'Prestações de contas reprovadas',
                'quantidade_prestacoes': 0,
                'status': 'REPROVADA'}
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_dashboard_add_aprovada_ressalva(
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
        f"/api/prestacoes-contas/dashboard/?periodo={periodo.uuid}&dre_uuid={dre.uuid}&add_aprovadas_ressalva=SIM")
    result = response.json()

    esperado = {
        'total_associacoes_dre': 5,
        'cards': [
            {
                'titulo': 'Prestações de contas não recebidas',
                'quantidade_nao_recebida': 1,
                'quantidade_prestacoes': 2,
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
                'quantidade_retornadas': 0,
                'status': 'DEVOLVIDA'},
            {
                'titulo': 'Prestações de contas aprovadas',
                'quantidade_prestacoes': 1,
                'status': 'APROVADA'},
            {
                'titulo': 'Prestações de contas reprovadas',
                'quantidade_prestacoes': 0,
                'status': 'REPROVADA'},
            {
                'titulo': 'Prestações de contas aprovadas com ressalvas',
                'quantidade_prestacoes': 1,
                'status': 'APROVADA_RESSALVA'}
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_dashboard_erro(jwt_authenticated_client_a, prestacao_conta_aprovada, prestacao_conta_em_analise, periodo, dre):
    response = jwt_authenticated_client_a.get(f"/api/prestacoes-contas/dashboard/?periodo=&dre_uuid=")
    result = response.json()

    erro_esperado = {
        'erro': 'parametros_requerido',
        'mensagem': 'É necessário enviar o uuid da dre (dre_uuid) e o periodo como parâmetros.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert erro_esperado == result


def test_dashboard_outro_periodo(jwt_authenticated_client_a, prestacao_conta_aprovada, prestacao_conta_em_analise,
                                 periodo_2020_1, dre):
    response = jwt_authenticated_client_a.get(
        f"/api/prestacoes-contas/dashboard/?periodo={periodo_2020_1.uuid}&dre_uuid={dre.uuid}")
    result = response.json()

    esperado = {
        'total_associacoes_dre': 2,
        'cards': [
            {
                'titulo': 'Prestações de contas não recebidas',
                'quantidade_nao_recebida': 0,
                'quantidade_prestacoes': 2,
                'status': 'NAO_RECEBIDA'},
            {
                'titulo': 'Prestações de contas recebidas aguardando análise',
                'quantidade_prestacoes': 0,
                'status': 'RECEBIDA'},
            {
                'titulo': 'Prestações de contas em análise',
                'quantidade_prestacoes': 0,
                'status': 'EM_ANALISE'},
            {
                'titulo': 'Prestações de conta devolvidas para acertos',
                'quantidade_prestacoes': 0,
                'quantidade_retornadas': 0,
                'status': 'DEVOLVIDA'},
            {
                'titulo': 'Prestações de contas aprovadas',
                'quantidade_prestacoes': 0,
                'status': 'APROVADA'},
            {
                'titulo': 'Prestações de contas reprovadas',
                'quantidade_prestacoes': 0,
                'status': 'REPROVADA'}
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
