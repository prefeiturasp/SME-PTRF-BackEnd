import pytest
from model_bakery import baker


@pytest.fixture
def analise_lancamento_justificado_service_01(analise_prestacao_conta_2020_1):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_lancamento='CREDITO',
        receita=None,
        resultado='CORRETO',
        justificativa="teste",
        status_realizacao="JUSTIFICADO"
    )




@pytest.fixture
def analise_lancamento_realizado_service_01(analise_prestacao_conta_2020_1):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_lancamento='CREDITO',
        receita=None,
        resultado='CORRETO',
        status_realizacao="REALIZADO"
    )


@pytest.fixture
def analise_lancamento_pendente_service_01(analise_prestacao_conta_2020_1):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_lancamento='CREDITO',
        receita=None,
        resultado='CORRETO',
        status_realizacao="PENDENTE"
    )


@pytest.fixture
def analise_lancamento_pendente_service_02(analise_prestacao_conta_2020_1):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_lancamento='CREDITO',
        receita=None,
        resultado='CORRETO',
        status_realizacao="PENDENTE",
        lancamento_atualizado=True,
        devolucao_tesouro_atualizada=True,
        lancamento_excluido=True
    )


@pytest.fixture
def tipo_acerto_edicao_de_lancamento_service_01():
    return baker.make('TipoAcertoLancamento', nome='Edição de Lançamento', categoria='EDICAO_LANCAMENTO')


@pytest.fixture
def tipo_acerto_devolucao_service_01():
    return baker.make('TipoAcertoLancamento', nome='Edição de Lançamento', categoria='DEVOLUCAO')


@pytest.fixture
def tipo_acerto_exclusao_service_01():
    return baker.make('TipoAcertoLancamento', nome='Edição de Lançamento', categoria='EXCLUSAO_LANCAMENTO')


@pytest.fixture
def tipo_acerto_solicitacao_esclarecimento_service_01():
    return baker.make('TipoAcertoLancamento', nome='Edição de Lançamento', categoria='SOLICITACAO_ESCLARECIMENTO')


@pytest.fixture
def solicitacao_acerto_lancamento_realizado_service_01(analise_lancamento_realizado_service_01, tipo_acerto_edicao_de_lancamento_service_01):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_realizado_service_01,
        tipo_acerto=tipo_acerto_edicao_de_lancamento_service_01,
        detalhamento="teste detalhaemnto",
        justificativa="justificativa",
        status_realizacao="REALIZADO",
        esclarecimentos="esclarecimento"
    )


@pytest.fixture
def solicitacao_acerto_lancamento_realizado_service_02(analise_lancamento_realizado_service_01, tipo_acerto_edicao_de_lancamento_service_01):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_realizado_service_01,
        tipo_acerto=tipo_acerto_edicao_de_lancamento_service_01,
        detalhamento="teste detalhaemnto",
        justificativa="justificativa",
        status_realizacao="REALIZADO",
        esclarecimentos="esclarecimento"
    )


@pytest.fixture
def solicitacao_acerto_lancamento_pendente_service_01(analise_lancamento_realizado_service_01, tipo_acerto_edicao_de_lancamento_service_01):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_realizado_service_01,
        tipo_acerto=tipo_acerto_edicao_de_lancamento_service_01,
        detalhamento="teste detalhaemnto",
        justificativa="justificativa",
        status_realizacao="PENDENTE",
        esclarecimentos="esclarecimento"
    )


@pytest.fixture
def solicitacao_acerto_lancamento_pendente_service_02(analise_lancamento_realizado_service_01, tipo_acerto_edicao_de_lancamento_service_01):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_realizado_service_01,
        tipo_acerto=tipo_acerto_edicao_de_lancamento_service_01,
        detalhamento="teste detalhaemnto",
        justificativa="justificativa",
        status_realizacao="PENDENTE",
        esclarecimentos="esclarecimento"
    )


@pytest.fixture
def solicitacao_acerto_lancamento_pendente_categoria_edicao_lancamento_service_01(
    analise_lancamento_pendente_service_01,
    tipo_acerto_edicao_de_lancamento_service_01
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_pendente_service_01,
        tipo_acerto=tipo_acerto_edicao_de_lancamento_service_01,
        detalhamento="teste detalhaemnto",
        justificativa="justificativa",
        status_realizacao="PENDENTE",
        esclarecimentos="esclarecimento"
    )


@pytest.fixture
def solicitacao_acerto_lancamento_pendente_categoria_edicao_lancamento_service_02(
    analise_lancamento_pendente_service_02,
    tipo_acerto_edicao_de_lancamento_service_01
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_pendente_service_02,
        tipo_acerto=tipo_acerto_edicao_de_lancamento_service_01,
        detalhamento="teste detalhaemnto",
        justificativa="justificativa",
        status_realizacao="PENDENTE",
        esclarecimentos="esclarecimento"
    )


@pytest.fixture
def solicitacao_acerto_lancamento_pendente_categoria_devolucao_service_01(
    analise_lancamento_pendente_service_01,
    tipo_acerto_devolucao_service_01
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_pendente_service_01,
        tipo_acerto=tipo_acerto_devolucao_service_01,
        detalhamento="teste detalhaemnto",
        justificativa="justificativa",
        status_realizacao="PENDENTE",
        esclarecimentos="esclarecimento"
    )


@pytest.fixture
def solicitacao_acerto_lancamento_pendente_categoria_devolucao_service_02(
    analise_lancamento_pendente_service_02,
    tipo_acerto_devolucao_service_01
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_pendente_service_02,
        tipo_acerto=tipo_acerto_devolucao_service_01,
        detalhamento="teste detalhaemnto",
        justificativa="justificativa",
        status_realizacao="PENDENTE",
        esclarecimentos="esclarecimento"
    )


@pytest.fixture
def solicitacao_acerto_lancamento_pendente_categoria_exclusao_lancamento_service_01(
    analise_lancamento_pendente_service_01,
    tipo_acerto_exclusao_service_01
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_pendente_service_01,
        tipo_acerto=tipo_acerto_exclusao_service_01,
        detalhamento="teste detalhaemnto",
        justificativa="justificativa",
        status_realizacao="PENDENTE",
        esclarecimentos="esclarecimento"
    )


@pytest.fixture
def solicitacao_acerto_lancamento_pendente_categoria_exclusao_lancamento_service_02(
    analise_lancamento_pendente_service_02,
    tipo_acerto_exclusao_service_01
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_pendente_service_02,
        tipo_acerto=tipo_acerto_exclusao_service_01,
        detalhamento="teste detalhaemnto",
        justificativa="justificativa",
        status_realizacao="PENDENTE",
        esclarecimentos="esclarecimento"
    )


@pytest.fixture
def solicitacao_acerto_lancamento_pendente_categoria_solicitacao_esclarecimento_service_01(
    analise_lancamento_pendente_service_01,
    tipo_acerto_solicitacao_esclarecimento_service_01
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_pendente_service_01,
        tipo_acerto=tipo_acerto_solicitacao_esclarecimento_service_01,
        detalhamento="teste detalhaemnto",
        justificativa="justificativa",
        status_realizacao="PENDENTE",
    )


@pytest.fixture
def solicitacao_acerto_lancamento_pendente_categoria_solicitacao_esclarecimento_service_02(
    analise_lancamento_pendente_service_02,
    tipo_acerto_solicitacao_esclarecimento_service_01
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_pendente_service_02,
        tipo_acerto=tipo_acerto_solicitacao_esclarecimento_service_01,
        detalhamento="teste detalhaemnto",
        justificativa="justificativa",
        status_realizacao="PENDENTE",
        esclarecimentos="esclarecimento"
    )
