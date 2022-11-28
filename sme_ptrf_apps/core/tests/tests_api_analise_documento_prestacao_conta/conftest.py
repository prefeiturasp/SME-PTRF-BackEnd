import pytest
from model_bakery import baker


@pytest.fixture
def analise_documento_realizado_01(
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
def analise_documento_pendente_01(
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
        status_realizacao="PENDENTE"
    )


@pytest.fixture
def analise_documento_justificado_01(
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
        status_realizacao="JUSTIFICADO"
    )


@pytest.fixture
def tipo_acerto_inclusao_de_credito_01():
    return baker.make('TipoAcertoDocumento', nome='Inclusão de Crédito', categoria='INCLUSAO_CREDITO')


@pytest.fixture
def solicitacao_acerto_documento_realizado_01(analise_documento_realizado_01, tipo_acerto_inclusao_de_credito_01):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_realizado_01,
        tipo_acerto=tipo_acerto_inclusao_de_credito_01,
        detalhamento="teste detalhaemnto",
        status_realizacao="REALIZADO"
    )


@pytest.fixture
def solicitacao_acerto_documento_pendente_01(analise_documento_realizado_01, tipo_acerto_inclusao_de_credito_01):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_realizado_01,
        tipo_acerto=tipo_acerto_inclusao_de_credito_01,
        detalhamento="teste detalhaemnto",
        status_realizacao="PENDENTE"
    )
