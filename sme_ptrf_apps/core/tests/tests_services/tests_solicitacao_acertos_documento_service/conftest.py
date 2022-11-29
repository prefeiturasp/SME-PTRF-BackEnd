import pytest
from model_bakery import baker


@pytest.fixture
def analise_documento_realizado_service_01(
    analise_prestacao_conta_2020_1,
    tipo_documento_prestacao_conta_ata,
    conta_associacao_cartao
):
    return baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_documento_prestacao_conta=tipo_documento_prestacao_conta_ata,
        conta_associacao=conta_associacao_cartao,
        resultado='CORRETO',
        status_realizacao="REALIZADO"
    )


@pytest.fixture
def tipo_acerto_inclusao_de_credito_service():
    return baker.make('TipoAcertoDocumento', nome='Inclusão de Crédito', categoria='INCLUSAO_CREDITO')


@pytest.fixture
def tipo_acerto_inclusao_de_gasto_service():
    return baker.make('TipoAcertoDocumento', nome='Inclusão de Gasto', categoria='INCLUSAO_GASTO')


@pytest.fixture
def tipo_acerto_solicitacao_esclarecimento_service():
    return baker.make('TipoAcertoDocumento', nome='Solicitacao esclarecimento', categoria='SOLICITACAO_ESCLARECIMENTO')


@pytest.fixture
def solicitacao_acerto_documento_realizado_service_01(
    analise_documento_realizado_service_01,
    tipo_acerto_inclusao_de_credito_service
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_realizado_service_01,
        tipo_acerto=tipo_acerto_inclusao_de_credito_service,
        status_realizacao="REALIZADO"
    )


@pytest.fixture
def solicitacao_acerto_documento_realizado_service_02(
    analise_documento_realizado_service_01,
    tipo_acerto_inclusao_de_credito_service
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_realizado_service_01,
        tipo_acerto=tipo_acerto_inclusao_de_credito_service,
        detalhamento="teste detalhaemnto",
        status_realizacao="REALIZADO"
    )


@pytest.fixture
def solicitacao_acerto_documento_pendente_service_01(
    analise_documento_realizado_service_01,
    tipo_acerto_inclusao_de_credito_service,
    receita_100_no_periodo,
    despesa_no_periodo
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_realizado_service_01,
        tipo_acerto=tipo_acerto_inclusao_de_credito_service,
        detalhamento="teste detalhaemnto",
        status_realizacao="PENDENTE",
        receita_incluida=receita_100_no_periodo,
    )


@pytest.fixture
def solicitacao_acerto_documento_pendente_service_02(
    analise_documento_realizado_service_01,
    tipo_acerto_inclusao_de_credito_service
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_realizado_service_01,
        tipo_acerto=tipo_acerto_inclusao_de_credito_service,
        detalhamento="teste detalhaemnto",
        status_realizacao="PENDENTE",
        justificativa="justificativa"
    )


@pytest.fixture
def solicitacao_acerto_documento_pendente_service_03(
    analise_documento_realizado_service_01,
    tipo_acerto_inclusao_de_gasto_service,
    receita_100_no_periodo,
    despesa_no_periodo
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_realizado_service_01,
        tipo_acerto=tipo_acerto_inclusao_de_gasto_service,
        detalhamento="teste detalhaemnto",
        status_realizacao="PENDENTE",
        despesa_incluida=despesa_no_periodo,
    )


@pytest.fixture
def solicitacao_acerto_documento_pendente_service_04(
    analise_documento_realizado_service_01,
    tipo_acerto_inclusao_de_gasto_service
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_realizado_service_01,
        tipo_acerto=tipo_acerto_inclusao_de_gasto_service,
        detalhamento="teste detalhaemnto",
        status_realizacao="PENDENTE",
        justificativa="justificativa"
    )


@pytest.fixture
def solicitacao_acerto_documento_pendente_service_05(
    analise_documento_realizado_service_01,
    tipo_acerto_solicitacao_esclarecimento_service,
    receita_100_no_periodo,
    despesa_no_periodo
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_realizado_service_01,
        tipo_acerto=tipo_acerto_solicitacao_esclarecimento_service,
        detalhamento="teste detalhaemnto",
        status_realizacao="PENDENTE",
        esclarecimentos="teste esclarecimento"
    )


@pytest.fixture
def solicitacao_acerto_documento_pendente_service_06(
    analise_documento_realizado_service_01,
    tipo_acerto_solicitacao_esclarecimento_service
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_realizado_service_01,
        tipo_acerto=tipo_acerto_solicitacao_esclarecimento_service,
        detalhamento="teste detalhaemnto",
        status_realizacao="PENDENTE",
        justificativa="justificativa"
    )
