import pytest
from model_bakery import baker


@pytest.fixture
def analise_lancamento_pendente_01(analise_prestacao_conta_2020_1):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_lancamento='CREDITO',
        receita=None,
        resultado='CORRETO',
        status_realizacao="PENDENTE"
    )


@pytest.fixture
def analise_lancamento_realizado_01(analise_prestacao_conta_2020_1):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_lancamento='CREDITO',
        receita=None,
        resultado='CORRETO',
        status_realizacao="REALIZADO"
    )


@pytest.fixture
def tipo_acerto_edicao_de_lancamento_01():
    return baker.make('TipoAcertoLancamento', nome='Edição de Lançamento', categoria='EDICAO_LANCAMENTO')


@pytest.fixture
def solicitacao_acerto_lancamento_realizado_01(analise_lancamento_realizado_01, tipo_acerto_edicao_de_lancamento_01):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_realizado_01,
        tipo_acerto=tipo_acerto_edicao_de_lancamento_01,
        detalhamento="teste detalhaemnto",
        justificativa="justificativa",
        status_realizacao="REALIZADO",
        esclarecimentos="esclarecimento"
    )


@pytest.fixture
def solicitacao_acerto_lancamento_realizado_02(analise_lancamento_realizado_01, tipo_acerto_edicao_de_lancamento_01):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_realizado_01,
        tipo_acerto=tipo_acerto_edicao_de_lancamento_01,
        detalhamento="teste detalhaemnto",
        justificativa="justificativa",
        status_realizacao="REALIZADO",
        esclarecimentos="esclarecimento"
    )


@pytest.fixture
def solicitacao_acerto_lancamento_pendente_01(analise_lancamento_pendente_01, tipo_acerto_edicao_de_lancamento_01):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_pendente_01,
        tipo_acerto=tipo_acerto_edicao_de_lancamento_01,
        detalhamento="teste detalhaemnto",
        justificativa="justificativa",
        status_realizacao="PENDENTE",
        esclarecimentos="esclarecimento"
    )

@pytest.fixture
def analise_lancamento_realizado_02(analise_prestacao_conta_2020_1):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_lancamento='CREDITO',
        receita=None,
        resultado='CORRETO',
        justificativa="teste",
        status_realizacao="REALIZADO"
    )


@pytest.fixture
def analise_lancamento_justificado_01(analise_prestacao_conta_2020_1):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_lancamento='CREDITO',
        receita=None,
        resultado='CORRETO',
        justificativa="teste",
        status_realizacao="JUSTIFICADO"
    )
