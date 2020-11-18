"""Gerador da planilha de relatórios consolidados

Esse serviço gera uma planilha no formato .xlsx com base na planilha modelo (modelo_relatorio_dre_sme.xlsx)
que foi fornecida pela PO e está nos statics da aplicação.

Esse script tem as seguintes funções:
    * gera_relatorio_dre - Cria o modelo RelatorioConsolidadoDRE que armazenará a planilha.
    * gerar - Função inicial para gerar a planilha.
    * cabecalho - Preenche o cabeçalho da planilha.
    * identificacao_dre -Preenche a parte de identificação da DRE da planilha.
"""

import logging
import os
from tempfile import NamedTemporaryFile

from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files import File
from openpyxl import load_workbook, styles

from sme_ptrf_apps.core.models import ContaAssociacao, Periodo, Unidade
from sme_ptrf_apps.core.services.xlsx_copy_row import copy_row
from sme_ptrf_apps.dre.models import JustificativaRelatorioConsolidadoDRE, RelatorioConsolidadoDRE

from .relatorio_consolidado_service import informacoes_execucao_financeira

LOGGER = logging.getLogger(__name__)

# Cabeçalho
COL_CABECALHO = 9
COL_TEXTO_CABECALHO = 6
LINHA_TEXTO_CABECALHO = 2
LINHA_PERIODO_CABECALHO = 4
LINHA_TIPO_CONTA_CABECALHO = 5

# Identificação
LINHA_IDENTIFICACAO = 9
COL_IDENTIFICACAO_DRE = 0
COL_IDENTIFICACAO_CNPJ = 7

# Execução Financeira
LINHA_CUSTEIO = 13
LINHA_CAPITAL = 14
LINHA_RLA = 15
LINHA_TOTAL = 16
COL_SALDO_REPROGRAMADO_ANTERIOR = 1
COL_REPASSES_PREVISTOS = 2
COL_REPASSES_NO_PERIODO = 3
COL_RENDIMENTO = 4
COL_RECEITAS_DEVOLUCAO = 5
COL_DEMAIS_CREDITOS = 6
COL_VALOR_TOTAL = 7
COL_DESPESA_NO_PERIODO = 8
COL_SALDO_REPROGRAMADO_PROXIMO = 9
COL_DEVOLUCAO_TESOURO = 11


def gera_relatorio_dre(dre, periodo, tipo_conta):

    filename = 'relatorio_consolidade_dre_%s.xlsx'

    xlsx = gerar(dre, periodo, tipo_conta)

    with NamedTemporaryFile() as tmp:
        xlsx.save(tmp.name)

        relatorio_consolidado, _ = RelatorioConsolidadoDRE.objects.update_or_create(
            dre=dre,
            periodo=periodo,
            tipo_conta=tipo_conta
        )
        relatorio_consolidado.arquivo.save(name=filename % relatorio_consolidado.pk, content=File(tmp))


def gerar(dre, periodo, tipo_conta):
    LOGGER.info("GERANDO RELATÓRIO CONSOLIDADO...")
    path = os.path.join(os.path.basename(staticfiles_storage.location), 'cargas')
    nome_arquivo = os.path.join(path, 'modelo_relatorio_dre_sme.xlsx')
    workbook = load_workbook(nome_arquivo)
    worksheet = workbook.active
    try:
        cabecalho(worksheet, periodo, tipo_conta)
        identificacao_dre(worksheet, dre)
        execucao_financeira(worksheet, dre, periodo, tipo_conta)
    except Exception as err:
        LOGGER.info("Erro %s", str(err))

    return workbook


def cabecalho(worksheet, periodo, tipo_conta):
    rows = list(worksheet.rows)
    # if previa else "Demonstrativo Financeiro - FINAL"
    texto = "Demonstrativo financeiro e do acompanhamento das prestações de conta das Associações - FINAL"
    rows[LINHA_TEXTO_CABECALHO][COL_TEXTO_CABECALHO].value = texto
    rows[LINHA_PERIODO_CABECALHO][COL_CABECALHO].value = str(periodo)
    rows[LINHA_TIPO_CONTA_CABECALHO][COL_CABECALHO].value = tipo_conta.nome


def identificacao_dre(worksheet, dre):
    """BLOCO 1 - IDENTIFICAÇÃO"""
    rows = list(worksheet.rows)
    rows[LINHA_IDENTIFICACAO][COL_IDENTIFICACAO_DRE].value = dre.nome
    rows[LINHA_IDENTIFICACAO][COL_IDENTIFICACAO_CNPJ].value = dre.dre_cnpj


def execucao_financeira(worksheet, dre, periodo, tipo_conta):
    rows = list(worksheet.rows)
    info = informacoes_execucao_financeira(dre, periodo, tipo_conta)

    # LINHA CUSTEIO
    rows[LINHA_CUSTEIO][COL_SALDO_REPROGRAMADO_ANTERIOR].value = formata_valor(
        info['saldo_reprogramado_periodo_anterior_custeio'])
    rows[LINHA_CUSTEIO][COL_REPASSES_PREVISTOS].value = formata_valor(info['repasses_previstos_sme_custeio'])
    rows[LINHA_CUSTEIO][COL_REPASSES_NO_PERIODO].value = formata_valor(info['repasses_no_periodo_custeio'])
    rows[LINHA_CUSTEIO][COL_RECEITAS_DEVOLUCAO].value = formata_valor(info['receitas_devolucao_no_periodo_custeio'])
    rows[LINHA_CUSTEIO][COL_DEMAIS_CREDITOS].value = formata_valor(info['demais_creditos_no_periodo_custeio'])
    valor_total_custeio = info['saldo_reprogramado_periodo_anterior_custeio'] + info['repasses_no_periodo_custeio'] +\
         info['receitas_devolucao_no_periodo_custeio'] + info['demais_creditos_no_periodo_custeio']
    rows[LINHA_CUSTEIO][COL_VALOR_TOTAL].value = formata_valor(valor_total_custeio)
    rows[LINHA_CUSTEIO][COL_DESPESA_NO_PERIODO].value = formata_valor(info['despesas_no_periodo_custeio'])
    rows[LINHA_CUSTEIO][COL_SALDO_REPROGRAMADO_PROXIMO].value = formata_valor(valor_total_custeio)

    # LINHA CAPITAL
    rows[LINHA_CAPITAL][COL_SALDO_REPROGRAMADO_ANTERIOR].value = formata_valor(
        info['saldo_reprogramado_periodo_anterior_capital'])
    rows[LINHA_CAPITAL][COL_REPASSES_PREVISTOS].value = formata_valor(info['repasses_previstos_sme_capital'])
    rows[LINHA_CAPITAL][COL_REPASSES_NO_PERIODO].value = formata_valor(info['repasses_no_periodo_capital'])
    rows[LINHA_CAPITAL][COL_RECEITAS_DEVOLUCAO].value = formata_valor(info['receitas_devolucao_no_periodo_capital'])
    rows[LINHA_CAPITAL][COL_DEMAIS_CREDITOS].value = formata_valor(info['demais_creditos_no_periodo_capital'])
    valor_total_capital = info['saldo_reprogramado_periodo_anterior_capital'] + info['repasses_no_periodo_capital'] +\
        info['receitas_devolucao_no_periodo_capital'] + info['demais_creditos_no_periodo_capital']
    rows[LINHA_CAPITAL][COL_VALOR_TOTAL].value = formata_valor(valor_total_capital)
    rows[LINHA_CAPITAL][COL_DESPESA_NO_PERIODO].value = formata_valor(info['despesas_no_periodo_capital'])
    rows[LINHA_CAPITAL][COL_SALDO_REPROGRAMADO_PROXIMO].value = formata_valor(valor_total_capital)

    # LINHA RLA
    rows[LINHA_RLA][COL_SALDO_REPROGRAMADO_ANTERIOR].value = formata_valor(
        info['saldo_reprogramado_periodo_anterior_livre'])
    rows[LINHA_RLA][COL_REPASSES_PREVISTOS].value = formata_valor(info['repasses_previstos_sme_livre'])
    rows[LINHA_RLA][COL_REPASSES_NO_PERIODO].value = formata_valor(info['repasses_no_periodo_livre'])
    rows[LINHA_RLA][COL_RENDIMENTO].value = formata_valor(info['receitas_rendimento_no_periodo_livre'])
    rows[LINHA_RLA][COL_RECEITAS_DEVOLUCAO].value = formata_valor(info['receitas_devolucao_no_periodo_livre'])
    rows[LINHA_RLA][COL_DEMAIS_CREDITOS].value = formata_valor(info['demais_creditos_no_periodo_livre'])
    valor_total_livre = info['saldo_reprogramado_periodo_anterior_livre'] + info['receitas_rendimento_no_periodo_livre'] +\
        info['repasses_no_periodo_livre'] + info['receitas_devolucao_no_periodo_livre'] + \
        info['demais_creditos_no_periodo_livre']
    rows[LINHA_RLA][COL_VALOR_TOTAL].value = formata_valor(valor_total_livre)
    rows[LINHA_RLA][COL_SALDO_REPROGRAMADO_PROXIMO].value = formata_valor(valor_total_livre)

    # LINHA TOTAIS
    rows[LINHA_TOTAL][COL_SALDO_REPROGRAMADO_ANTERIOR].value = formata_valor(
        info['saldo_reprogramado_periodo_anterior_total'])
    rows[LINHA_TOTAL][COL_REPASSES_PREVISTOS].value = formata_valor(info['repasses_previstos_sme_total'])
    rows[LINHA_TOTAL][COL_REPASSES_NO_PERIODO].value = formata_valor(info['repasses_no_periodo_total'])
    rows[LINHA_TOTAL][COL_RENDIMENTO].value = formata_valor(info['receitas_rendimento_no_periodo_livre'])
    rows[LINHA_TOTAL][COL_RECEITAS_DEVOLUCAO].value = formata_valor(info['receitas_devolucao_no_periodo_total'])
    rows[LINHA_TOTAL][COL_DEMAIS_CREDITOS].value = formata_valor(info['demais_creditos_no_periodo_total'])
    valor_total = info['saldo_reprogramado_periodo_anterior_total'] + info['receitas_rendimento_no_periodo_livre'] +\
        info['repasses_no_periodo_total'] + info['receitas_devolucao_no_periodo_total'] + \
        info['demais_creditos_no_periodo_total']
    rows[LINHA_TOTAL][COL_VALOR_TOTAL].value = formata_valor(valor_total)
    rows[LINHA_TOTAL][COL_DESPESA_NO_PERIODO].value = formata_valor(info['despesas_no_periodo_total'])
    rows[LINHA_TOTAL][COL_SALDO_REPROGRAMADO_PROXIMO].value = formata_valor(valor_total)

    rows[LINHA_TOTAL][COL_DEVOLUCAO_TESOURO].value = formata_valor(info['devolucoes_ao_tesouro_no_periodo_total'])

    LINHA_JUSTIFICATIVA = 19
    # Justificativa
    justificativa = JustificativaRelatorioConsolidadoDRE.objects.first()
    rows[LINHA_JUSTIFICATIVA][0].value = justificativa.texto if justificativa else ''


def formata_valor(valor):
    from babel.numbers import format_currency
    sinal, valor_formatado = format_currency(valor, 'BRL', locale='pt_BR').split('\xa0')
    sinal = '-' if '-' in sinal else ''
    return f'{sinal}{valor_formatado}'
