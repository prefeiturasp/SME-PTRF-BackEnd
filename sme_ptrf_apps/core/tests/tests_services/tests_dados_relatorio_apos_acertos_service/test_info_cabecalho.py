import datetime

import pytest

from sme_ptrf_apps.core.services.dados_relatorio_apos_acertos_service import DadosRelatorioAposAcertosService

pytestmark = pytest.mark.django_db


def test_info_cabecalho_contem_chaves_esperadas(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    cabecalho = resultado['info_cabecalho']
    assert 'recurso' in cabecalho
    assert 'periodo_referencia' in cabecalho
    assert 'data_inicio_periodo' in cabecalho
    assert 'data_fim_periodo' in cabecalho


def test_info_cabecalho_periodo_referencia(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert resultado['info_cabecalho']['periodo_referencia'] == '2020.1'


def test_info_cabecalho_datas_do_periodo(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    cabecalho = resultado['info_cabecalho']
    assert cabecalho['data_inicio_periodo'] == datetime.date(2020, 1, 1)
    assert cabecalho['data_fim_periodo'] == datetime.date(2020, 6, 30)


def test_info_cabecalho_recurso_nome(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert resultado['info_cabecalho']['recurso'] is not None
    assert isinstance(resultado['info_cabecalho']['recurso'], str)


# --- dados_associacao ---

def test_dados_associacao_contem_chaves_esperadas(analise_prestacao_conta_2020_1):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    dados = resultado['dados_associacao']
    assert 'nome_associacao' in dados
    assert 'cnpj_associacao' in dados
    assert 'codigo_eol_associacao' in dados
    assert 'nome_dre' in dados
    assert 'data_devolucao_dre' in dados
    assert 'prazo_devolucao_associacao' in dados


def test_dados_associacao_nome(analise_prestacao_conta_2020_1, associacao):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert resultado['dados_associacao']['nome_associacao'] == associacao.nome


def test_dados_associacao_cnpj(analise_prestacao_conta_2020_1, associacao):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert resultado['dados_associacao']['cnpj_associacao'] == associacao.cnpj


def test_dados_associacao_codigo_eol(analise_prestacao_conta_2020_1, unidade):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert resultado['dados_associacao']['codigo_eol_associacao'] == unidade.codigo_eol


def test_dados_associacao_nome_dre_com_dre_padrao(analise_prestacao_conta_2020_1, dre):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    # O nome da DRE é retornado em maiúsculas
    assert resultado['dados_associacao']['nome_dre'] == dre.nome.upper()


def test_dados_associacao_nome_dre_remove_prefixo_diretoria_regional(
    analise_prestacao_conta_2020_1, unidade
):
    # Atualiza o nome da DRE com o prefixo que deve ser removido
    unidade.dre.nome = 'Diretoria Regional de Educacao Ipiranga'
    unidade.dre.save()

    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert resultado['dados_associacao']['nome_dre'] == 'IPIRANGA'


def test_dados_associacao_data_devolucao_dre_com_devolucao(
    analise_prestacao_conta_2020_1, devolucao_prestacao_conta_2020_1
):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert resultado['dados_associacao']['data_devolucao_dre'] == devolucao_prestacao_conta_2020_1.data


def test_dados_associacao_prazo_devolucao_associacao_com_devolucao(
    analise_prestacao_conta_2020_1, devolucao_prestacao_conta_2020_1
):
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        previa=False,
        usuario='',
    )
    assert resultado['dados_associacao']['prazo_devolucao_associacao'] == devolucao_prestacao_conta_2020_1.data_limite_ue  # noqa


def test_dados_associacao_data_devolucao_dre_sem_devolucao(
    prestacao_conta_2020_1_conciliada
):
    from model_bakery import baker
    analise_sem_devolucao = baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        devolucao_prestacao_conta=None,
    )
    resultado = DadosRelatorioAposAcertosService.dados_relatorio_apos_acerto(
        analise_prestacao_conta=analise_sem_devolucao,
        previa=False,
        usuario='',
    )
    assert resultado['dados_associacao']['data_devolucao_dre'] == '-'
    assert resultado['dados_associacao']['prazo_devolucao_associacao'] == '-'
