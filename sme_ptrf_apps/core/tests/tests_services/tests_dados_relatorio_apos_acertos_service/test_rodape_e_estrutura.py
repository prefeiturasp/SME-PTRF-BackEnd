import pytest

from sme_ptrf_apps.core.services.dados_relatorio_apos_acertos_service import DadosRelatorioAposAcertosService

pytestmark = pytest.mark.django_db


def test_rodape_contem_nome_da_associacao(analise_prestacao_conta_2020_1, associacao):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert associacao.nome in resultado['rodape']


def test_rodape_documento_gerado_quando_nao_previa(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert 'Documento gerado' in resultado['rodape']


def test_rodape_previa_gerada_quando_previa(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=True,
        usuario='',
    )
    assert 'Prévia gerada' in resultado['rodape']


def test_rodape_contem_sig_escola(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert 'SIG_ESCOLA' in resultado['rodape']


def test_rodape_contem_nome_usuario_quando_informado(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='joao.silva',
    )
    assert 'joao.silva' in resultado['rodape']


def test_rodape_sem_usuario_quando_string_vazia(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert 'pelo usuário' not in resultado['rodape']


def test_dados_relatorio_retorna_todas_as_chaves(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    chaves_esperadas = [
        'categoria_devolucao',
        'info_cabecalho',
        'dados_associacao',
        'dados_extratos_bancarios',
        'dados_lancamentos',
        'dados_despesas_periodos_anteriores',
        'dados_documentos',
        'blocos',
        'rodape',
        'previa',
    ]
    for chave in chaves_esperadas:
        assert chave in resultado, f"Chave '{chave}' ausente no resultado"


def test_dados_relatorio_campo_previa_falso(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert resultado['previa'] is False


def test_dados_relatorio_campo_previa_verdadeiro(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=True,
        usuario='',
    )
    assert resultado['previa'] is True


def test_dados_relatorio_categoria_devolucao(analise_prestacao_conta_2020_1):
    from sme_ptrf_apps.core.models import TipoAcertoLancamento
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert resultado['categoria_devolucao'] == TipoAcertoLancamento.CATEGORIA_DEVOLUCAO


def test_dados_lancamentos_e_lista(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert isinstance(resultado['dados_lancamentos'], list)


def test_dados_extratos_bancarios_e_lista(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert isinstance(resultado['dados_extratos_bancarios'], list)


def test_blocos_e_dicionario(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert isinstance(resultado['blocos'], dict)
