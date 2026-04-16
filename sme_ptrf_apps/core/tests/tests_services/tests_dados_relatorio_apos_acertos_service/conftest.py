import datetime

import pytest
from model_bakery import baker


@pytest.fixture
def analise_conta_com_data_extrato(analise_prestacao_conta_2020_1, conta_associacao):
    """AnaliseContaPrestacaoConta com data_extrato preenchido — deve aparecer nos dados de extratos."""
    return baker.make(
        'AnaliseContaPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        conta_associacao=conta_associacao,
        data_extrato=datetime.date(2020, 7, 1),
        saldo_extrato=1000.00,
        solicitar_envio_do_comprovante_do_saldo_da_conta=False,
        solicitar_correcao_da_data_do_saldo_da_conta=False,
        solicitar_correcao_de_justificativa_de_conciliacao=False,
        observacao_solicitar_envio_do_comprovante_do_saldo_da_conta='',
    )


@pytest.fixture
def analise_conta_com_flag_comprovante(analise_prestacao_conta_2020_1, conta_associacao):
    """AnaliseContaPrestacaoConta com flag de envio de comprovante ativa."""
    return baker.make(
        'AnaliseContaPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        conta_associacao=conta_associacao,
        data_extrato=None,
        saldo_extrato=None,
        solicitar_envio_do_comprovante_do_saldo_da_conta=True,
        solicitar_correcao_da_data_do_saldo_da_conta=False,
        solicitar_correcao_de_justificativa_de_conciliacao=False,
        observacao_solicitar_envio_do_comprovante_do_saldo_da_conta='Comprovante necessário',
    )


@pytest.fixture
def analise_conta_sem_dados_exibiveis(analise_prestacao_conta_2020_1, conta_associacao):
    """AnaliseContaPrestacaoConta sem nenhum dado exibível — NÃO deve aparecer nos extratos."""
    return baker.make(
        'AnaliseContaPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        conta_associacao=conta_associacao,
        data_extrato=None,
        saldo_extrato=None,
        solicitar_envio_do_comprovante_do_saldo_da_conta=False,
        solicitar_correcao_da_data_do_saldo_da_conta=False,
        solicitar_correcao_de_justificativa_de_conciliacao=False,
    )


@pytest.fixture
def tipo_documento_pc(tipo_documento_prestacao_conta_factory):
    return tipo_documento_prestacao_conta_factory(nome='Demonstrativo Financeiro')


@pytest.fixture
def analise_documento_resultado_ajuste(analise_prestacao_conta_2020_1, tipo_documento_prestacao_conta_ata):
    """Documento com resultado AJUSTE — deve aparecer em dados_documentos."""
    return baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_documento_prestacao_conta=tipo_documento_prestacao_conta_ata,
        resultado='AJUSTE',
    )


@pytest.fixture
def analise_documento_resultado_correto(analise_prestacao_conta_2020_1, tipo_documento_prestacao_conta_ata):
    """Documento com resultado CORRETO — NÃO deve aparecer em dados_documentos."""
    return baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_documento_prestacao_conta=tipo_documento_prestacao_conta_ata,
        resultado='CORRETO',
    )


@pytest.fixture
def flag_ajustes_despesas_anteriores_ativa():
    """Cria a flag waffle 'ajustes-despesas-anteriores' ativa para todos os usuários."""
    return baker.make('waffle.Flag', name='ajustes-despesas-anteriores', everyone=True)
