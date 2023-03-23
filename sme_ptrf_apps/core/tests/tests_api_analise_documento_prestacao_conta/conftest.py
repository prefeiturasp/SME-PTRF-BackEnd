from datetime import date

import pytest
from model_bakery import baker

from sme_ptrf_apps.core.models import TipoAcertoDocumento


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


# Edição de Informação


@pytest.fixture
def periodo_anterior_edicao_informacao_teste_api():
    return baker.make(
        'Periodo',
        referencia='2019.1',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 8, 31),
    )


@pytest.fixture
def periodo_edicao_informacao_teste_api(periodo_anterior_edicao_informacao_teste_api):
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 9, 1),
        data_fim_realizacao_despesas=date(2019, 11, 30),
        data_prevista_repasse=date(2019, 10, 1),
        data_inicio_prestacao_contas=date(2019, 12, 1),
        data_fim_prestacao_contas=date(2019, 12, 5),
        periodo_anterior=periodo_anterior_edicao_informacao_teste_api,
    )

@pytest.fixture
def observacao_conciliacao(periodo_edicao_informacao_teste_api, conta_associacao_cartao):
    return baker.make(
        'ObservacaoConciliacao',
        periodo=periodo_edicao_informacao_teste_api,
        associacao=conta_associacao_cartao.associacao,
        conta_associacao=conta_associacao_cartao,
        texto="Uma bela observação.",
        data_extrato = date(2020, 7, 1),
        saldo_extrato = 1000
    )

@pytest.fixture
def tipo_documento_prestacao_conta_demonstrativo_financeiro_edicao_informacao_teste_api():
    return baker.make(
        'TipoDocumentoPrestacaoConta',
        nome='Tipo Documento Demonstrativo Financeiro'
    )

@pytest.fixture
def tipo_acerto_documento_edicao_informacao_teste_api(tipo_documento_prestacao_conta_demonstrativo_financeiro_edicao_informacao_teste_api):
    tipo_acerto = baker.make(
        'TipoAcertoDocumento',
        nome='Edição de Informação',
        categoria=TipoAcertoDocumento.CATEGORIA_EDICAO_INFORMACAO
    )
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_demonstrativo_financeiro_edicao_informacao_teste_api)
    tipo_acerto.save()
    return tipo_acerto


@pytest.fixture
def solicitacao_acerto_documento_edicao_informacao_teste_api(
    analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao_teste_api,
    tipo_acerto_documento_edicao_informacao_teste_api,
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao_teste_api,
        tipo_acerto=tipo_acerto_documento_edicao_informacao_teste_api,
        detalhamento="Detalhamento motivo acerto no documento",
    )


@pytest.fixture
def analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao_teste_api(
    analise_prestacao_conta_2020_1,
    tipo_documento_prestacao_conta_demonstrativo_financeiro_edicao_informacao_teste_api,
    conta_associacao_cartao
):
    return baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_documento_prestacao_conta=tipo_documento_prestacao_conta_demonstrativo_financeiro_edicao_informacao_teste_api,
        conta_associacao=conta_associacao_cartao,
        resultado='AJUSTE'
    )
