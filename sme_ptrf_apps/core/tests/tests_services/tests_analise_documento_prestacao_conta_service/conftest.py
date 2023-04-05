from datetime import date

import pytest
from model_bakery import baker

from sme_ptrf_apps.core.models import PrestacaoConta, TipoAcertoDocumento


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
        justificativa="teste",
        status_realizacao="REALIZADO"
    )


@pytest.fixture
def analise_documento_realizado_service_02(
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
        justificativa="teste",
        status_realizacao="REALIZADO"
    )


@pytest.fixture
def analise_documento_pendente_service_01(
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
        justificativa="teste",
        status_realizacao="PENDENTE"
    )


@pytest.fixture
def analise_documento_pendente_service_02(
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
        justificativa="teste",
        status_realizacao="PENDENTE"
    )


@pytest.fixture
def analise_documento_justificado_service_01(
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
        justificativa="teste",
        status_realizacao="JUSTIFICADO"
    )


# Restaurar justificativa original


@pytest.fixture
def tipo_documento_prestacao_conta_demonstrativo_financeiro_edicao_informacao_teste_service():
    return baker.make(
        'TipoDocumentoPrestacaoConta',
        nome='Tipo Documento Demonstrativo Financeiro'
    )

@pytest.fixture
def tipo_acerto_documento_edicao_informacao_teste_service(
    tipo_documento_prestacao_conta_demonstrativo_financeiro_edicao_informacao_teste_service
):
    tipo_acerto = baker.make(
        'TipoAcertoDocumento',
        nome='Edição de Informação',
        categoria=TipoAcertoDocumento.CATEGORIA_EDICAO_INFORMACAO
    )
    tipo_acerto.tipos_documento_prestacao.add(
        tipo_documento_prestacao_conta_demonstrativo_financeiro_edicao_informacao_teste_service
    )
    tipo_acerto.save()
    return tipo_acerto


@pytest.fixture
def solicitacao_acerto_documento_edicao_informacao_teste_service(
    analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao_teste_service,
    tipo_acerto_documento_edicao_informacao_teste_service,
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao_teste_service,
        tipo_acerto=tipo_acerto_documento_edicao_informacao_teste_service,
        detalhamento="Detalhamento motivo acerto no documento",
    )


# Editar informação da concilicação

@pytest.fixture
def prestacao_conta_2020_1_conciliada(periodo_teste_service, conta_associacao_teste_service):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_teste_service,
        associacao=conta_associacao_teste_service.associacao,
        status=PrestacaoConta.STATUS_NAO_RECEBIDA
    )


@pytest.fixture
def analise_prestacao_conta_2020_1_teste_service(prestacao_conta_2020_1_conciliada, devolucao_prestacao_conta_2020_1):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        devolucao_prestacao_conta=devolucao_prestacao_conta_2020_1
    )


@pytest.fixture
def analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao_teste_service(
    analise_prestacao_conta_2020_1_teste_service,
    tipo_documento_prestacao_conta_demonstrativo_financeiro,
    conta_associacao_teste_service
):
    return baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1_teste_service,
        tipo_documento_prestacao_conta=tipo_documento_prestacao_conta_demonstrativo_financeiro,
        conta_associacao=conta_associacao_teste_service,
        resultado='AJUSTE'
    )


@pytest.fixture
def observacao_conciliacao_teste_service(periodo_teste_service, conta_associacao_teste_service):
    return baker.make(
        'ObservacaoConciliacao',
        periodo=periodo_teste_service,
        associacao=conta_associacao_teste_service.associacao,
        conta_associacao=conta_associacao_teste_service,
        texto="Uma bela observação.",
        justificativa_original="Uma bela observação.",
        data_extrato=date(2020, 7, 1),
        saldo_extrato=1000
    )

@pytest.fixture
def observacao_conciliacao_teste_service_02(periodo_teste_service, conta_associacao_teste_service):
    return baker.make(
        'ObservacaoConciliacao',
        periodo=periodo_teste_service,
        associacao=conta_associacao_teste_service.associacao,
        conta_associacao=conta_associacao_teste_service,
        texto="Uma bela observação.",
        justificativa_original="Esta é a justificativa original",
        data_extrato=date(2020, 7, 1),
        saldo_extrato=1000
    )


@pytest.fixture
def periodo_anterior_teste_service():
    return baker.make(
        'Periodo',
        referencia='2019.1',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 8, 31),
    )


@pytest.fixture
def periodo_teste_service(periodo_anterior_teste_service):
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 9, 1),
        data_fim_realizacao_despesas=date(2019, 11, 30),
        data_prevista_repasse=date(2019, 10, 1),
        data_inicio_prestacao_contas=date(2019, 12, 1),
        data_fim_prestacao_contas=date(2019, 12, 5),
        periodo_anterior=periodo_anterior_teste_service,
    )


@pytest.fixture
def tipo_conta_teste_service():
    return baker.make(
        'TipoConta',
        nome='Cheque',
        banco_nome='Banco do Inter',
        agencia='67945',
        numero_conta='935556-x',
        numero_cartao='987644164221'
    )


@pytest.fixture
def conta_associacao_teste_service(associacao_teste_service, tipo_conta_teste_service):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao_teste_service,
        tipo_conta=tipo_conta_teste_service,
        banco_nome='Banco do Brasil',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='534653264523'
    )


@pytest.fixture
def unidade_teste_service(dre):
    return baker.make(
        'Unidade',
        nome='Escola Teste',
        tipo_unidade='CEU',
        codigo_eol='987452',
        dre=dre,
        sigla='ET',
        cep='5868120',
        tipo_logradouro='Travessa',
        logradouro='dos Testes',
        bairro='COHAB INSTITUTO ADVENTISTA',
        numero='200',
        complemento='fundos',
        telefone='58212627',
        email='emefjopfilho@sme.prefeitura.sp.gov.br',
        diretor_nome='Pedro Amaro',
        dre_cnpj='04.560.968/0001-23',
        dre_diretor_regional_rf='1234567',
        dre_diretor_regional_nome='Anthony Edward Stark',
        dre_designacao_portaria='Portaria nº 0.000',
        dre_designacao_ano='2017',
    )


@pytest.fixture
def associacao_teste_service(unidade_teste_service, periodo_teste_service):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='17.045.420/0001-97',
        unidade=unidade_teste_service,
        periodo_inicial=periodo_teste_service,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456'
    )
