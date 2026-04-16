import pytest

from sme_ptrf_apps.core.services.dados_relatorio_apos_acertos_service import DadosRelatorioAposAcertosService

pytestmark = pytest.mark.django_db


def test_dados_extratos_bancarios_vazio_sem_analises_de_extrato(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert resultado['dados_extratos_bancarios'] == []


def test_dados_extratos_bancarios_vazio_quando_analise_sem_dados_exibiveis(
    analise_prestacao_conta_2020_1,
    analise_conta_sem_dados_exibiveis,
):
    """Extrato sem data, saldo e nenhuma flag ativa não deve aparecer na lista."""
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert resultado['dados_extratos_bancarios'] == []


def test_dados_extratos_bancarios_exibe_quando_tem_data_extrato(
    analise_prestacao_conta_2020_1,
    analise_conta_com_data_extrato,
):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert len(resultado['dados_extratos_bancarios']) == 1


def test_dados_extratos_bancarios_exibe_quando_tem_flag_comprovante(
    analise_prestacao_conta_2020_1,
    analise_conta_com_flag_comprovante,
):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert len(resultado['dados_extratos_bancarios']) == 1


def test_dados_extratos_bancarios_estrutura_do_item(
    analise_prestacao_conta_2020_1,
    analise_conta_com_data_extrato,
):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    item = resultado['dados_extratos_bancarios'][0]
    assert 'nome_conta' in item
    assert 'data_extrato' in item
    assert 'saldo_extrato' in item
    assert 'solicitar_envio_do_comprovante_do_saldo_da_conta' in item
    assert 'solicitar_correcao_da_data_do_saldo_da_conta' in item
    assert 'observacao_solicitar_envio_do_comprovante_do_saldo_da_conta' in item
    assert 'solicitar_correcao_de_justificativa_de_conciliacao' in item


def test_dados_extratos_bancarios_valores_corretos(
    analise_prestacao_conta_2020_1,
    analise_conta_com_data_extrato,
    conta_associacao,
):
    import datetime
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    item = resultado['dados_extratos_bancarios'][0]
    assert item['data_extrato'] == datetime.date(2020, 7, 1)
    assert item['saldo_extrato'] == 1000.00
    assert item['nome_conta'] == conta_associacao.tipo_conta.nome


def test_dados_extratos_bancarios_observacao_comprovante(
    analise_prestacao_conta_2020_1,
    analise_conta_com_flag_comprovante,
):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    item = resultado['dados_extratos_bancarios'][0]
    assert item['solicitar_envio_do_comprovante_do_saldo_da_conta'] is True
    assert item['observacao_solicitar_envio_do_comprovante_do_saldo_da_conta'] == 'Comprovante necessário'


def test_dados_extratos_bancarios_saldo_none_ainda_exibe(
    analise_prestacao_conta_2020_1,
    conta_associacao,
):
    """saldo_extrato=0 não é None, então deve exibir; saldo_extrato=None sem outros dados não exibe."""
    from model_bakery import baker
    baker.make(
        'AnaliseContaPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        conta_associacao=conta_associacao,
        data_extrato=None,
        saldo_extrato=0,
        solicitar_envio_do_comprovante_do_saldo_da_conta=False,
        solicitar_correcao_da_data_do_saldo_da_conta=False,
        solicitar_correcao_de_justificativa_de_conciliacao=False,
    )
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    # saldo_extrato=0 é not None → exibe
    assert len(resultado['dados_extratos_bancarios']) == 1
