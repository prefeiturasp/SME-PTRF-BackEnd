"""Gerador da planilha de relatórios consolidados

Esse serviço gera uma planilha no formato .xlsx com base na planilha modelo (modelo_relatorio_dre_sme.xlsx)
que foi fornecida pela PO e está nos statics da aplicação.

Esse script tem as seguintes funções:
    * gera_relatorio_dre - Cria o modelo RelatorioConsolidadoDRE que armazenará a planilha.
    * gerar - Função inicial para gerar a planilha.
    * cabecalho - Preenche o cabeçalho da planilha.
    * identificacao_dre - Preenche o bloco de identificação da DRE da planilha.
    * data_geracao_documento - Preenche a data de geração do documento.
    * execucao_financeira - Preenche o bloco de execuções financeiras. 
    * execucao_fisica - Preenche o bloco de execuções fisicas.
    * associacoes_nao_regularizadas - Preenche as associações não regularizadas do bloco de execuções físicas.
"""

import logging
import os
from datetime import date
from tempfile import NamedTemporaryFile

from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files import File
from openpyxl import load_workbook, styles

from sme_ptrf_apps.core.models import Associacao, ContaAssociacao, Periodo, PrestacaoConta, Unidade
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

# Execução Financeira - Justificativa
LINHA_JUSTIFICATIVA = 19

# Execução Física
LINHA_EXECUCAO_FISICA = 25

LAST_LINE = 56


def gera_relatorio_dre(dre, periodo, tipo_conta, parcial=False):

    filename = 'relatorio_consolidade_dre_%s.xlsx'

    xlsx = gerar(dre, periodo, tipo_conta, parcial=parcial)

    with NamedTemporaryFile() as tmp:
        xlsx.save(tmp.name)

        relatorio_consolidado, _ = RelatorioConsolidadoDRE.objects.update_or_create(
            dre=dre,
            periodo=periodo,
            tipo_conta=tipo_conta,
            status=RelatorioConsolidadoDRE.STATUS_GERADO_PARCIAL if parcial else RelatorioConsolidadoDRE.STATUS_GERADO_TOTAL
        )
        relatorio_consolidado.arquivo.save(name=filename % relatorio_consolidado.pk, content=File(tmp))
        LOGGER.info("Relatório Consolidado Gerado: uuid: %s, status: %s",
                    relatorio_consolidado.uuid, relatorio_consolidado.status)


def gerar(dre, periodo, tipo_conta, parcial=False):
    LOGGER.info("GERANDO RELATÓRIO CONSOLIDADO...")
    
    path = os.path.join(os.path.basename(staticfiles_storage.location), 'cargas')
    nome_arquivo = os.path.join(path, 'modelo_relatorio_dre_sme.xlsx')
    workbook = load_workbook(nome_arquivo)
    worksheet = workbook.active
    try:
        cabecalho(worksheet, periodo, tipo_conta, parcial)
        identificacao_dre(worksheet, dre)
        data_geracao_documento(worksheet, parcial)
        execucao_financeira(worksheet, dre, periodo, tipo_conta)
        execucao_fisica(worksheet, dre, periodo)
    except Exception as err:
        LOGGER.info("Erro %s", str(err))
        raise err

    return workbook


def cabecalho(worksheet, periodo, tipo_conta, parcial):
    rows = list(worksheet.rows)
    status = "PARCIAL" if parcial else "FINAL"
    texto = f"Demonstrativo financeiro e do acompanhamento das prestações de conta das Associações - {status}"
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

    # Justificativa
    justificativa = JustificativaRelatorioConsolidadoDRE.objects.first()
    rows[LINHA_JUSTIFICATIVA][0].value = justificativa.texto if justificativa else ''


def execucao_fisica(worksheet, dre, periodo):
    rows = list(worksheet.rows)

    rows[LINHA_EXECUCAO_FISICA][0].value = dre.unidades_da_dre.count()
    quantidade_ues_cnpj = Associacao.objects.filter(unidade__dre=dre).exclude(cnpj__exact='').count()
    rows[LINHA_EXECUCAO_FISICA][2].value = quantidade_ues_cnpj
    quantidade_regular = Associacao.objects.filter(
        unidade__dre=dre, status_regularidade=Associacao.STATUS_REGULARIDADE_REGULAR).exclude(cnpj__exact='').count()
    rows[LINHA_EXECUCAO_FISICA][4].value = quantidade_regular

    cards = PrestacaoConta.dashboard(periodo.uuid, dre.uuid, add_aprovado_ressalva=True)

    quantidade_aprovada = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'APROVADA'][0]
    quantidade_aprovada_ressalva = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'APROVADA_RESSALVA'][0]
    quantidade_nao_aprovada = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'REPROVADA'][0]
    quantidade_nao_recebida = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'NAO_RECEBIDA'][0]
    quantidade_recebida = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'RECEBIDA'][0]
    quantidade_em_analise = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'RECEBIDA'][0]

    rows[LINHA_EXECUCAO_FISICA][6].value = quantidade_aprovada
    rows[LINHA_EXECUCAO_FISICA][7].value = quantidade_aprovada_ressalva
    quantidade_nao_apresentada = quantidade_ues_cnpj - quantidade_aprovada - quantidade_aprovada_ressalva -\
        quantidade_nao_aprovada - quantidade_nao_recebida - quantidade_recebida - quantidade_em_analise
    rows[LINHA_EXECUCAO_FISICA][8].value = quantidade_nao_apresentada
    rows[LINHA_EXECUCAO_FISICA][9].value = quantidade_nao_aprovada
    quantidade_devida = quantidade_nao_apresentada + quantidade_nao_aprovada
    rows[LINHA_EXECUCAO_FISICA][10].value = quantidade_devida
    rows[LINHA_EXECUCAO_FISICA][11].value = quantidade_aprovada + quantidade_devida

    associacoes_pendentes = Associacao.objects.filter(
        unidade__dre=dre, status_regularidade=Associacao.STATUS_REGULARIDADE_PENDENTE).exclude(cnpj__exact='')
    associacoes_nao_regularizadas(worksheet, associacoes_pendentes)


def associacoes_nao_regularizadas(worksheet, associacoes_pendetes, acc=0, start_line=29):
    quantidade = acc
    last_line = LAST_LINE + quantidade
    ind = start_line

    for linha, associacao in enumerate(associacoes_pendetes):
        # Movendo as linhas para baixo antes de inserir os dados novos
        ind = start_line + quantidade + linha
        if linha > 0:
            for row_idx in range(last_line + linha, ind - 2, -1):
                copy_row(worksheet, row_idx, 1, copy_data=True)

        rows = list(worksheet.rows)
        row = rows[ind - 1]
        row[0].value = linha + 1
        row[1].value = associacao.nome


def data_geracao_documento(worksheet, parcial=False):
    rows = list(worksheet.rows)
    data_geracao = date.today().strftime("%d/%m/%Y")
    texto = f"Documento parcial gerado em: {data_geracao}" if parcial else f"Documento final gerado em: {data_geracao}"
    rows[LAST_LINE][0].value = texto


def formata_valor(valor):
    from babel.numbers import format_currency
    sinal, valor_formatado = format_currency(valor, 'BRL', locale='pt_BR').split('\xa0')
    sinal = '-' if '-' in sinal else ''
    return f'{sinal}{valor_formatado}'
