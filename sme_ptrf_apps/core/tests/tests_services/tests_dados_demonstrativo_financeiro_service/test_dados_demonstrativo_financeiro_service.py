import pytest
from sme_ptrf_apps.core.models import DadosDemonstrativoFinanceiro
from sme_ptrf_apps.core.fixtures.factories.demonstrativo_financeiro_factory import (
    DemonstrativoFinanceiroFactory,
    DadosDemonstrativoFinanceiroFactory,
    ItemResumoPorAcaoFactory,
    ItemCreditoFactory,
    ItemDespesaFactory,
    CategoriaDespesaChoices
)
from sme_ptrf_apps.core.services.persistencia_dados_demo_financeiro_service import PersistenciaDadosDemoFinanceiro
from sme_ptrf_apps.core.services.recuperacao_dados_persistindos_demo_financeiro_service import RecuperaDadosDemoFinanceiro

pytestmark = pytest.mark.django_db


dados_demonstrativo = {
    "cabecalho": {
        "titulo": 'Demonstrativo Financeiro - PRÉVIA',
        "periodo": '2022.3 - 2022-09-01 a 2022-12-31',
        "periodo_referencia": '2022.3',
        "periodo_data_inicio": '01/09/2022',
        "periodo_data_fim": '31/12/2022',
        "conta": 'Cheque',
    },
    "identificacao_apm": {
        "nome_associacao": 'escol teste',
        "cnpj_associacao": '71.372.816/0001-94',
        "codigo_eol_associacao": '083710',
        "nome_dre_associacao": 'ITAQUERA',
        "tipo_unidade": 'EMEF',
        "nome_unidade": 'escol teste.',
        "presidente_diretoria_executiva": 'PRESIDENTE',
        "presidente_conselho_fiscal": 'CONSELHO FISCAL',
        "cargo_substituto_presidente_ausente": 'SUBSTITUTO',
    },
    "identificacao_conta": {
        "banco": 'Banco de Brasil',
        "agencia": '0000',
        "conta": '00.000.0',
        "data_extrato": '31/12/2022',
        "saldo_extrato": 18017.52,
        "encerrada_em": '',
    },
    "resumo_por_acao": {
        "resumo_acoes": [],
        "total_valores": {
            "saldo_anterior": {
                "C": 0,
                "L": 0,
                "K": 0,
            },
            "credito": {
                "C": 0,
                "L": 0,
                "K": 0,
            },
            "despesa_realizada": {
                "C": 0,
                "K": 0,
            },
            "despesa_nao_realizada": {
                "C": 0,
                "K": 0,
            },
            "saldo_reprogramado_proximo": {
                "C": 0,
                "L": 0,
                "K": 0,
            },
            "despesa_nao_demostrada_outros_periodos": {
                "C": 0,
                "K": 0,
            },
            "valor_saldo_bancario": {
                "C": 0,
                "K": 0,
            },
            "total_valores": 0,
            "saldo_bancario": 0
        }
    },
    "creditos_demonstrados": {
        "linhas": [],
        "valor_total": 0
    },
    "despesas_demonstradas": {
        "linhas": [],
        "valor_total": 0
    },
    "despesas_nao_demonstradas": {
        "linhas": [],
        "valor_total": 0
    },
    "despesas_anteriores_nao_demonstradas": {
        "linhas": [],
        "valor_total": 0
    },
    "justificativas": "JUSTIFICATIVA",
    "data_geracao_documento": "texto rodape",
    "data_geracao": "31/12/2022"
}


def test_persistir_relatorio_demonstrativo_financeiro():
    demonstrativo = DemonstrativoFinanceiroFactory()

    PersistenciaDadosDemoFinanceiro(dados=dados_demonstrativo, demonstrativo=demonstrativo)
    relatorio = DadosDemonstrativoFinanceiro.objects.get(demonstrativo=demonstrativo)

    assert relatorio


def test_deve_substituir_dados_de_relatorio_anterior_existente():
    demonstrativo = DemonstrativoFinanceiroFactory()
    DadosDemonstrativoFinanceiroFactory(demonstrativo=demonstrativo)

    assert DadosDemonstrativoFinanceiro.objects.all().count() == 1

    PersistenciaDadosDemoFinanceiro(dados=dados_demonstrativo, demonstrativo=demonstrativo)

    assert DadosDemonstrativoFinanceiro.objects.all().count() == 1


def test_retorna_dados_formatados_cabecalho():
    demonstrativo = DemonstrativoFinanceiroFactory()
    dados_demonstrativo_financeiro = DadosDemonstrativoFinanceiroFactory(demonstrativo=demonstrativo)
    ItemResumoPorAcaoFactory(dados_demonstrativo=dados_demonstrativo_financeiro, total_geral=True)

    resultado = RecuperaDadosDemoFinanceiro(demonstrativo=demonstrativo).dados_formatados

    assert 'cabecalho' in resultado
    assert 'periodo_referencia' in resultado['cabecalho']
    assert 'periodo_data_inicio' in resultado['cabecalho']
    assert 'periodo_data_fim' in resultado['cabecalho']
    assert 'conta' in resultado['cabecalho']


def test_retorna_dados_formatados_identificacao_apm():
    demonstrativo = DemonstrativoFinanceiroFactory()
    dados_demonstrativo_financeiro = DadosDemonstrativoFinanceiroFactory(demonstrativo=demonstrativo)
    ItemResumoPorAcaoFactory(dados_demonstrativo=dados_demonstrativo_financeiro, total_geral=True)

    resultado = RecuperaDadosDemoFinanceiro(demonstrativo=demonstrativo).dados_formatados

    assert 'identificacao_apm' in resultado
    assert 'nome_associacao' in resultado['identificacao_apm']
    assert 'cnpj_associacao' in resultado['identificacao_apm']
    assert 'codigo_eol_associacao' in resultado['identificacao_apm']
    assert 'nome_dre_associacao' in resultado['identificacao_apm']
    assert 'cargo_substituto_presidente_ausente' in resultado['identificacao_apm']
    assert 'presidente_diretoria_executiva' in resultado['identificacao_apm']
    assert 'presidente_conselho_fiscal' in resultado['identificacao_apm']
    assert 'tipo_unidade' in resultado['identificacao_apm']
    assert 'nome_unidade' in resultado['identificacao_apm']


def test_retorna_dados_formatados_identificacao_conta():
    demonstrativo = DemonstrativoFinanceiroFactory()
    dados_demonstrativo_financeiro = DadosDemonstrativoFinanceiroFactory(demonstrativo=demonstrativo)
    ItemResumoPorAcaoFactory(dados_demonstrativo=dados_demonstrativo_financeiro, total_geral=True)

    resultado = RecuperaDadosDemoFinanceiro(demonstrativo=demonstrativo).dados_formatados

    assert 'identificacao_conta' in resultado
    assert 'banco' in resultado['identificacao_conta']
    assert 'agencia' in resultado['identificacao_conta']
    assert 'conta' in resultado['identificacao_conta']
    assert 'data_extrato' in resultado['identificacao_conta']
    assert 'saldo_extrato' in resultado['identificacao_conta']
    assert 'encerrada_em' in resultado['identificacao_conta']


def test_retorna_dados_formatados_resumo_por_acao():
    demonstrativo = DemonstrativoFinanceiroFactory()
    dados_demonstrativo_financeiro = DadosDemonstrativoFinanceiroFactory(demonstrativo=demonstrativo)

    ItemResumoPorAcaoFactory(dados_demonstrativo=dados_demonstrativo_financeiro)
    ItemResumoPorAcaoFactory(dados_demonstrativo=dados_demonstrativo_financeiro, total_geral=True)

    resultado = RecuperaDadosDemoFinanceiro(demonstrativo=demonstrativo).dados_formatados

    assert 'resumo_por_acao' in resultado
    assert 'total_valores' in resultado['resumo_por_acao']
    assert 'resumo_acoes' in resultado['resumo_por_acao']
    assert len(resultado["resumo_por_acao"]["resumo_acoes"]) == 1


def test_retorna_dados_formatados_creditos_demonstrados():
    demonstrativo = DemonstrativoFinanceiroFactory()
    dados_demonstrativo_financeiro = DadosDemonstrativoFinanceiroFactory(demonstrativo=demonstrativo)

    ItemResumoPorAcaoFactory(dados_demonstrativo=dados_demonstrativo_financeiro, total_geral=True)
    ItemCreditoFactory(dados_demonstrativo=dados_demonstrativo_financeiro)

    resultado = RecuperaDadosDemoFinanceiro(demonstrativo=demonstrativo).dados_formatados

    assert 'creditos_demonstrados' in resultado
    assert 'valor_total' in resultado['creditos_demonstrados']
    assert 'linhas' in resultado['creditos_demonstrados']
    assert len(resultado["creditos_demonstrados"]["linhas"]) == 1


def test_retorna_dados_formatados_creditos_demonstrados_com_estorno():
    demonstrativo = DemonstrativoFinanceiroFactory()
    dados_demonstrativo_financeiro = DadosDemonstrativoFinanceiroFactory(demonstrativo=demonstrativo)

    ItemResumoPorAcaoFactory(dados_demonstrativo=dados_demonstrativo_financeiro, total_geral=True)
    ItemCreditoFactory(dados_demonstrativo=dados_demonstrativo_financeiro, receita_estornada=True)

    resultado = RecuperaDadosDemoFinanceiro(demonstrativo=demonstrativo).dados_formatados

    assert 'creditos_demonstrados' in resultado
    assert 'valor_total' in resultado['creditos_demonstrados']
    assert 'linhas' in resultado['creditos_demonstrados']
    assert len(resultado["creditos_demonstrados"]["linhas"]) == 1
    assert 'estorno' in resultado["creditos_demonstrados"]["linhas"][0]


def test_retorna_dados_formatados_despesas_demonstradas():
    demonstrativo = DemonstrativoFinanceiroFactory()
    dados_demonstrativo_financeiro = DadosDemonstrativoFinanceiroFactory(demonstrativo=demonstrativo)

    ItemResumoPorAcaoFactory(dados_demonstrativo=dados_demonstrativo_financeiro, total_geral=True)
    ItemDespesaFactory(dados_demonstrativo=dados_demonstrativo_financeiro)

    resultado = RecuperaDadosDemoFinanceiro(demonstrativo=demonstrativo).dados_formatados

    assert 'despesas_demonstradas' in resultado
    assert 'valor_total' in resultado['despesas_demonstradas']
    assert 'linhas' in resultado['despesas_demonstradas']
    assert len(resultado["despesas_demonstradas"]["linhas"]) == 1


def test_retorna_dados_formatados_despesas_nao_demonstradas():
    demonstrativo = DemonstrativoFinanceiroFactory()
    dados_demonstrativo_financeiro = DadosDemonstrativoFinanceiroFactory(demonstrativo=demonstrativo)

    ItemResumoPorAcaoFactory(dados_demonstrativo=dados_demonstrativo_financeiro, total_geral=True)
    ItemDespesaFactory(
        dados_demonstrativo=dados_demonstrativo_financeiro, categoria_despesa=CategoriaDespesaChoices.NAO_DEMONSTRADA)

    resultado = RecuperaDadosDemoFinanceiro(demonstrativo=demonstrativo).dados_formatados

    assert 'despesas_nao_demonstradas' in resultado
    assert 'valor_total' in resultado['despesas_nao_demonstradas']
    assert 'linhas' in resultado['despesas_nao_demonstradas']
    assert len(resultado["despesas_nao_demonstradas"]["linhas"]) == 1


def test_retorna_dados_formatados_despesas_anteriores_nao_demonstradas():
    demonstrativo = DemonstrativoFinanceiroFactory()
    dados_demonstrativo_financeiro = DadosDemonstrativoFinanceiroFactory(demonstrativo=demonstrativo)

    ItemResumoPorAcaoFactory(dados_demonstrativo=dados_demonstrativo_financeiro, total_geral=True)
    ItemDespesaFactory(
        dados_demonstrativo=dados_demonstrativo_financeiro,
        categoria_despesa=CategoriaDespesaChoices.NAO_DEMONSTRADA_PERIODO_ANTERIOR
    )

    resultado = RecuperaDadosDemoFinanceiro(demonstrativo=demonstrativo).dados_formatados

    assert 'despesas_anteriores_nao_demonstradas' in resultado
    assert 'valor_total' in resultado['despesas_anteriores_nao_demonstradas']
    assert 'linhas' in resultado['despesas_anteriores_nao_demonstradas']
    assert len(resultado["despesas_anteriores_nao_demonstradas"]["linhas"]) == 1


def test_retorna_dados_formatados_justificativas():
    demonstrativo = DemonstrativoFinanceiroFactory()
    dados_demonstrativo_financeiro = DadosDemonstrativoFinanceiroFactory(demonstrativo=demonstrativo)

    ItemResumoPorAcaoFactory(dados_demonstrativo=dados_demonstrativo_financeiro, total_geral=True)
    resultado = RecuperaDadosDemoFinanceiro(demonstrativo=demonstrativo).dados_formatados

    assert 'justificativas' in resultado


def test_retorna_dados_formatados_data_geracao_documento():
    demonstrativo = DemonstrativoFinanceiroFactory()
    dados_demonstrativo_financeiro = DadosDemonstrativoFinanceiroFactory(demonstrativo=demonstrativo)

    ItemResumoPorAcaoFactory(dados_demonstrativo=dados_demonstrativo_financeiro, total_geral=True)
    resultado = RecuperaDadosDemoFinanceiro(demonstrativo=demonstrativo).dados_formatados

    assert 'data_geracao_documento' in resultado


def test_retorna_dados_formatados_data_geracao():
    demonstrativo = DemonstrativoFinanceiroFactory()
    dados_demonstrativo_financeiro = DadosDemonstrativoFinanceiroFactory(demonstrativo=demonstrativo)

    ItemResumoPorAcaoFactory(dados_demonstrativo=dados_demonstrativo_financeiro, total_geral=True)
    resultado = RecuperaDadosDemoFinanceiro(demonstrativo=demonstrativo).dados_formatados

    assert 'data_geracao' in resultado


def test_retorna_dados_formatados_previa():
    demonstrativo = DemonstrativoFinanceiroFactory()
    dados_demonstrativo_financeiro = DadosDemonstrativoFinanceiroFactory(demonstrativo=demonstrativo)

    ItemResumoPorAcaoFactory(dados_demonstrativo=dados_demonstrativo_financeiro, total_geral=True)
    resultado = RecuperaDadosDemoFinanceiro(demonstrativo=demonstrativo).dados_formatados

    assert 'previa' in resultado

