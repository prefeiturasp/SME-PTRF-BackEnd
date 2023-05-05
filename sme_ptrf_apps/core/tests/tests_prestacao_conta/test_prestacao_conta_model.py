import pytest
from django.contrib import admin
from model_bakery import baker

from ...models import PrestacaoConta, Associacao, Periodo


pytestmark = pytest.mark.django_db


def test_instance_model(prestacao_conta):
    model = prestacao_conta
    assert isinstance(model, PrestacaoConta)
    assert isinstance(model.associacao, Associacao)
    assert isinstance(model.periodo, Periodo)
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.status
    assert model.data_recebimento
    assert model.data_ultima_analise
    assert model.motivos_reprovacao
    assert model.outros_motivos_reprovacao
    assert model.motivos_aprovacao_ressalva
    assert model.outros_motivos_aprovacao_ressalva
    assert model.recomendacoes
    assert model.analise_atual is None
    assert model.publicada is None
    assert model.consolidado_dre is None
    assert model.justificativa_pendencia_realizacao


def test_srt_model(prestacao_conta):
    assert prestacao_conta.__str__() == '2019.2 - 2019-09-01 a 2019-11-30 - NAO_APRESENTADA'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[PrestacaoConta]


@pytest.fixture
def prestacao_conta1(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        status="EM_ANALISE"
    )


@pytest.fixture
def prestacao_conta2(periodo, outra_associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=outra_associacao,
        status="APROVADA"
    )


def test_dash_board(prestacao_conta1, prestacao_conta2, periodo, dre):
    esperado = [
        {
            'titulo': 'Prestações de contas não recebidas',
            'quantidade_nao_recebida': 0,
            'quantidade_prestacoes': 0,
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
            'titulo': 'Prestações de contas reprovadas',
            'quantidade_prestacoes': 0,
            'status': 'REPROVADA'}
    ]

    assert esperado == prestacao_conta1.dashboard(periodo.uuid, dre.uuid)


def test_dashboard_deve_desconsiderar_associacoes_nao_iniciadas_parametro_ativo(
    associacao_iniciada_2020_1,
    associacao_iniciada_2020_2,
    periodo_2020_2,
    parametros_desconsidera_nao_iniciadas,
):
    result = PrestacaoConta.dashboard(
        periodo_2020_2.uuid,
        associacao_iniciada_2020_1.unidade.dre.uuid,
    )

    # Quantidade de prestações deve ser 1, pois a associacao iniciada em 2020_2 nao deve ser considerada
    assert result[0]['titulo'] == 'Prestações de contas não recebidas'
    assert result[0]['quantidade_prestacoes'] == 1


def test_dashboard_deve_desconsiderar_associacoes_nao_iniciadas_parametro_inativo(
    associacao_iniciada_2020_1,
    associacao_iniciada_2020_2,
    periodo_2020_2,
    parametros_nao_desconsidera_nao_iniciadas,
):
    result = PrestacaoConta.dashboard(
        periodo_2020_2.uuid,
        associacao_iniciada_2020_1.unidade.dre.uuid,
    )

    # Quantidade de prestações deve ser 2, pois o parâmetro de desconsiderar associacoes nao iniciadas esta inativo
    assert result[0]['titulo'] == 'Prestações de contas não recebidas'
    assert result[0]['quantidade_prestacoes'] == 2



def test_dashboard_deve_desconsiderar_associacoes_encerradas(
    associacao_encerrada_2020_1,
    associacao_encerrada_2020_2,
    periodo_2020_2,
):
    result = PrestacaoConta.dashboard(
        periodo_2020_2.uuid,
        associacao_encerrada_2020_1.unidade.dre.uuid,
    )

    # Quantidade de prestações deve ser 1, pois a associacao encerrada em 2020_1 nao deve ser considerada
    assert result[0]['titulo'] == 'Prestações de contas não recebidas'
    assert result[0]['quantidade_prestacoes'] == 1
