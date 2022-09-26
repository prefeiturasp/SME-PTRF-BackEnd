import pytest
from model_bakery import baker
import datetime


@pytest.fixture
def tipo_acerto_lancamento_create():
    return baker.make('TipoAcertoLancamento', nome='Teste nome igual', categoria='DEVOLUCAO')


@pytest.fixture
def tipo_acerto_lancamento_delete():
    return baker.make('TipoAcertoLancamento', nome='Teste', categoria='DEVOLUCAO')


@pytest.fixture
def tipo_acerto_lancamento_delete_02():
    return baker.make('TipoAcertoLancamento', nome='Teste 2', categoria='DEVOLUCAO')


@pytest.fixture
def solicitacao_acerto_lancamento_delete(
    analise_lancamento_delete,
    tipo_acerto_lancamento_delete_02,
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_delete,
        tipo_acerto=tipo_acerto_lancamento_delete_02,
        detalhamento="teste"
    )


@pytest.fixture
def analise_lancamento_delete(
    analise_prestacao_conta_delete,
):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_delete,
        tipo_lancamento='GASTO',
        resultado='AJUSTE'
    )


@pytest.fixture
def analise_prestacao_conta_delete(
    prestacao_conta_delete,
):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_delete,
    )


@pytest.fixture
def prestacao_conta_delete(periodo_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
        data_recebimento=datetime.date(2020, 10, 1),
        status="EM_ANALISE"
    )


@pytest.fixture
def tipo_acerto_lancamento():
    return baker.make('TipoAcertoLancamento', nome='Teste lanca', categoria='EXCLUSAO_LANCAMENTO')


@pytest.fixture
def tipo_acerto_lancamento_02():
    return baker.make('TipoAcertoLancamento', nome='Teste filtro nome', categoria='EDICAO_LANCAMENTO', ativo=False)


@pytest.fixture
def tipo_acerto_lancamento_03():
    return baker.make('TipoAcertoLancamento', nome='tipo lancamento', categoria='EXCLUSAO_LANCAMENTO', ativo=False)

@pytest.fixture
def tipo_acerto_lancamento_retrieve():
    return baker.make('TipoAcertoLancamento', nome='Teste retrieve', categoria='DEVOLUCAO')


@pytest.fixture
def tipo_acerto_lancamento_update():
    return baker.make('TipoAcertoLancamento', nome='Teste update', categoria='DEVOLUCAO')


@pytest.fixture
def tipo_acerto_lancamento_update_nome_igual():
    return baker.make('TipoAcertoLancamento', nome='Teste nome igual update', categoria='DEVOLUCAO')
