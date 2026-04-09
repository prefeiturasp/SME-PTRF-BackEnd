import pytest

from sme_ptrf_apps.core.services.dados_relatorio_apos_acertos_service import DadosRelatorioAposAcertosService

pytestmark = pytest.mark.django_db


def test_dados_documentos_vazio_sem_analises(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert list(resultado['dados_documentos']) == []


def test_dados_documentos_inclui_apenas_resultado_ajuste(
    analise_prestacao_conta_2020_1,
    analise_documento_resultado_ajuste,
    analise_documento_resultado_correto,
):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert len(resultado['dados_documentos']) == 1


def test_dados_documentos_nao_inclui_resultado_correto(
    analise_prestacao_conta_2020_1,
    analise_documento_resultado_correto,
):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert list(resultado['dados_documentos']) == []


def test_dados_documentos_multiplos_ajustes(
    analise_prestacao_conta_2020_1,
    tipo_documento_prestacao_conta_ata,
):
    from model_bakery import baker
    baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_documento_prestacao_conta=tipo_documento_prestacao_conta_ata,
        resultado='AJUSTE',
        _quantity=3,
    )
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert len(resultado['dados_documentos']) == 3


# --- blocos ---

def test_blocos_apenas_identificacao_quando_sem_dados_adicionais(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    blocos = resultado['blocos']
    assert 'identificacao_associacao' in blocos
    assert blocos['identificacao_associacao'] == 'Bloco 1 - Identificação da Associação da Unidade Educacional'
    # Sem extratos, lancamentos ou documentos: apenas o bloco 1
    assert len(blocos) == 1


def test_blocos_inclui_extratos_como_bloco_2(
    analise_prestacao_conta_2020_1,
    analise_conta_com_data_extrato,
):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    blocos = resultado['blocos']
    assert 'acertos_extratos_bancarios' in blocos
    assert blocos['acertos_extratos_bancarios'] == 'Bloco 2 - Acertos nas informações de extrato bancário'


def test_blocos_inclui_documentos_no_numero_correto(
    analise_prestacao_conta_2020_1,
    analise_documento_resultado_ajuste,
):
    """Sem extratos nem lancamentos, documentos devem ser Bloco 2."""
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    blocos = resultado['blocos']
    assert 'acertos_documentos' in blocos
    assert blocos['acertos_documentos'] == 'Bloco 2 - Acertos nos documentos'


def test_blocos_numeracao_sequencial_extratos_e_documentos(
    analise_prestacao_conta_2020_1,
    analise_conta_com_data_extrato,
    analise_documento_resultado_ajuste,
):
    """Com extratos (bloco 2) e documentos, documentos devem ser bloco 3."""
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    blocos = resultado['blocos']
    assert 'identificacao_associacao' in blocos
    assert 'acertos_extratos_bancarios' in blocos
    assert 'acertos_documentos' in blocos
    assert 'Bloco 1' in blocos['identificacao_associacao']
    assert 'Bloco 2' in blocos['acertos_extratos_bancarios']
    assert 'Bloco 3' in blocos['acertos_documentos']


def test_blocos_despesas_periodos_anteriores_quando_flag_ativa(
    analise_prestacao_conta_2020_1,
    flag_ajustes_despesas_anteriores_ativa,
):
    """Com a flag ativa, bloco de despesas de períodos anteriores pode aparecer
    (mas só se houver lançamentos). Verificamos que a flag é lida sem erro."""
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert 'acertos_despesas_periodos_anteriores' not in resultado['blocos']


def test_dados_despesas_periodos_anteriores_lista_vazia_sem_flag(analise_prestacao_conta_2020_1):
    """Sem a flag ativa, dados_despesas_periodos_anteriores deve ser lista vazia."""
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert resultado['dados_despesas_periodos_anteriores'] == []
