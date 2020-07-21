"""
Módulo responsável pela montagem do arquivo de demonstrativo financeiro.

Autor: Anderson Marques Morais
update: 11/05/2020
"""

import logging
import os
import re
import locale
from copy import copy
from tempfile import NamedTemporaryFile

from django.contrib.staticfiles.storage import staticfiles_storage
from openpyxl import load_workbook
from openpyxl.cell.cell import Cell, MergedCell
from openpyxl.utils import column_index_from_string, get_column_letter, range_boundaries
from openpyxl.utils.cell import coordinate_from_string

from sme_ptrf_apps.core.models import Associacao, FechamentoPeriodo, PrestacaoConta, MembroAssociacao, Observacao
from sme_ptrf_apps.core.choices import MembroEnum
from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CUSTEIO
from sme_ptrf_apps.receitas.models import Receita

LOGGER = logging.getLogger(__name__)

COL_CABECALHO = 9
LINHA_PERIODO_CABECALHO = 4
LINHA_ACAO_CABECALHO = 5
LINHA_CONTA_CABECALHO = 6
LAST_LINE = 46

# Coluna 2 da planilha
SALDO_ANTERIOR = 0
CREDITO = 2
DESPESA_REALIZADA = 3
SALDO_REPROGRAMADO_PROXIMO = 4
TOTAL_REPROGRAMADO_PROXIMO = 5
DESPESA_NAO_DEMONSTRADA = 6
SALDO_BANCARIO = 8
TOTAL_SALDO_BANCARIO = 10

# Colunas dos blocos 4 e 5 da planilha
ITEM = 0
RAZAO_SOCIAL = 1
CNPJ_CPF = 2
TIPO_DOCUMENTO = 3
NUMERO_DOCUMENTO = 4
DATA = 5
ESPECIFICACAO_MATERIAL = 6
TIPO_DESPESA = 7
TIPO_TRANSACAO = 8
DATA_2 = 9
VALOR = 10


def gerar(periodo, acao_associacao, conta_associacao):
    LOGGER.info("GERANDO DEMONSTRATIVO...")
    rateios_conferidos = RateioDespesa.rateios_da_acao_associacao_no_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=True)
    rateios_nao_conferidos = RateioDespesa.rateios_da_acao_associacao_em_qualquer_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, conferido=False)
    receitas_demonstradas = Receita.receitas_da_acao_associacao_no_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=True)
    fechamento_periodo = FechamentoPeriodo.objects.filter(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo).first()
    path = os.path.join(os.path.basename(staticfiles_storage.location), 'cargas')
    nome_arquivo = os.path.join(path, 'modelo_demonstrativo_financeiro.xlsx')
    workbook = load_workbook(nome_arquivo)
    worksheet = workbook.active

    cabecalho(worksheet, periodo, acao_associacao, conta_associacao)
    identificacao_apm(worksheet, acao_associacao)
    observacoes(worksheet, acao_associacao)
    sintese_receita_despesa(worksheet, acao_associacao, conta_associacao, periodo, fechamento_periodo)
    creditos_demonstrados(worksheet, receitas_demonstradas)
    acc = len(receitas_demonstradas)-1 if len(receitas_demonstradas) > 1 else 0
    pagamentos(worksheet, rateios_conferidos, acc=acc, start_line=27)
    acc += len(rateios_conferidos)-1 if len(rateios_conferidos) > 1 else 0
    pagamentos(worksheet, rateios_nao_conferidos, acc=acc, start_line=33)

    return workbook


def cabecalho(worksheet, periodo, acao_associacao, conta_associacao):
    rows = list(worksheet.rows)
    rows[LINHA_PERIODO_CABECALHO][COL_CABECALHO].value = str(periodo)
    rows[LINHA_ACAO_CABECALHO][COL_CABECALHO].value = acao_associacao.acao.nome
    rows[LINHA_CONTA_CABECALHO][COL_CABECALHO].value = conta_associacao.tipo_conta.nome


def identificacao_apm(worksheet, acao_associacao):
    """BLOCO 1 - IDENTIFICAÇÃO DA APM/APMSUAC DA UNIDADE EDUCACIONAL"""
    associacao = acao_associacao.associacao
    rows = list(worksheet.rows)
    rows[10][0].value = associacao.nome
    rows[10][6].value = associacao.cnpj
    rows[10][7].value = associacao.unidade.codigo_eol
    rows[10][8].value = associacao.unidade.dre.nome

    presidente_diretoria_executiva = MembroAssociacao.objects.filter(associacao=associacao,
                                                                     cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.name).first()

    presidente_conselho_fiscal = MembroAssociacao.objects.filter(associacao=associacao,
                                                                 cargo_associacao=MembroEnum.PRESIDENTE_CONSELHO_FISCAL.name).first()

    rows[LAST_LINE-1][0].value = presidente_diretoria_executiva.nome if presidente_diretoria_executiva else ''
    rows[LAST_LINE-1][6].value = presidente_conselho_fiscal.nome if presidente_conselho_fiscal else ''


def sintese_receita_despesa(worksheet, acao_associacao, conta_associacao, periodo, fechamento_periodo):
    saldo_reprogramado_anterior_capital = fechamento_periodo.fechamento_anterior.saldo_reprogramado_capital if fechamento_periodo.fechamento_anterior else 0
    saldo_reprogramado_anterior_custeio = fechamento_periodo.fechamento_anterior.saldo_reprogramado_custeio if fechamento_periodo.fechamento_anterior else 0

    receitas_demonstradas_capital = Receita.receitas_da_acao_associacao_no_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=True, categoria_receita=APLICACAO_CAPITAL).values_list('valor')
    receitas_demonstradas_custeio = Receita.receitas_da_acao_associacao_no_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=True, categoria_receita=APLICACAO_CUSTEIO).values_list('valor')

    valor_capital_receitas_demonstradas = sum(
        rrc[0] for rrc in receitas_demonstradas_capital) if receitas_demonstradas_capital else 0
    valor_custeio_receitas_demonstradas = sum(
        rrk[0] for rrk in receitas_demonstradas_custeio) if receitas_demonstradas_custeio else 0

    rateios_demonstrados_capital = RateioDespesa.rateios_da_acao_associacao_no_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=True, aplicacao_recurso=APLICACAO_CAPITAL).values_list('valor_rateio')
    rateios_demonstrados_custeio = RateioDespesa.rateios_da_acao_associacao_no_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=True, aplicacao_recurso=APLICACAO_CUSTEIO).values_list('valor_rateio')

    valor_capital_rateios_demonstrados = sum(
        rrc[0] for rrc in rateios_demonstrados_capital) if rateios_demonstrados_capital else 0
    valor_custeio_rateios_demonstrados = sum(
        rrk[0] for rrk in rateios_demonstrados_custeio) if rateios_demonstrados_custeio else 0

    rateios_nao_conferidos_capital = RateioDespesa.rateios_da_acao_associacao_em_qualquer_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, conferido=False, aplicacao_recurso=APLICACAO_CAPITAL).values_list('valor_rateio')
    rateios_nao_conferidos_custeio = RateioDespesa.rateios_da_acao_associacao_em_qualquer_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, conferido=False, aplicacao_recurso=APLICACAO_CUSTEIO).values_list('valor_rateio')

    valor_capital_rateios_nao_demonstrados = sum(
        rrc[0] for rrc in rateios_nao_conferidos_capital) if rateios_nao_conferidos_capital else 0
    valor_custeio_rateios_nao_demonstrados = sum(
        rrk[0] for rrk in rateios_nao_conferidos_custeio) if rateios_nao_conferidos_custeio else 0

    row_custeio = list(worksheet.rows)[15]
    row_capital = list(worksheet.rows)[16]

    row_capital[SALDO_ANTERIOR].value = f'K {formata_valor(saldo_reprogramado_anterior_capital)}' 
    row_capital[CREDITO].value = f'K {formata_valor(valor_capital_receitas_demonstradas)}'
    row_capital[DESPESA_REALIZADA].value = f'K {formata_valor(valor_capital_rateios_demonstrados)}'
    valor_saldo_reprogramado_proximo_periodo_capital = saldo_reprogramado_anterior_capital + valor_capital_receitas_demonstradas - valor_capital_rateios_demonstrados
    row_capital[SALDO_REPROGRAMADO_PROXIMO].value = f'K {formata_valor(valor_saldo_reprogramado_proximo_periodo_capital)}'
    row_capital[DESPESA_NAO_DEMONSTRADA].value = f'K {formata_valor(valor_capital_rateios_nao_demonstrados)}'
    valor_saldo_bancario_capital = valor_saldo_reprogramado_proximo_periodo_capital + valor_capital_rateios_nao_demonstrados
    row_capital[SALDO_BANCARIO].value = f'K {formata_valor(valor_saldo_bancario_capital)}'

    row_custeio[SALDO_ANTERIOR].value = f'C {formata_valor(saldo_reprogramado_anterior_custeio)}'
    row_custeio[CREDITO].value = f'C {formata_valor(valor_custeio_receitas_demonstradas)}'
    row_custeio[DESPESA_REALIZADA].value = f'C {formata_valor(valor_custeio_rateios_demonstrados)}'
    valor_saldo_reprogramado_proximo_periodo_custeio = saldo_reprogramado_anterior_custeio + valor_custeio_receitas_demonstradas - valor_custeio_rateios_demonstrados
    row_custeio[SALDO_REPROGRAMADO_PROXIMO].value = f'C {formata_valor(valor_saldo_reprogramado_proximo_periodo_custeio)}'

    row_custeio[TOTAL_REPROGRAMADO_PROXIMO].value = formata_valor(valor_saldo_reprogramado_proximo_periodo_capital + \
        valor_saldo_reprogramado_proximo_periodo_custeio)

    row_custeio[DESPESA_NAO_DEMONSTRADA].value = f'C {formata_valor(valor_custeio_rateios_nao_demonstrados)}'
    valor_saldo_bancario_custeio = valor_saldo_reprogramado_proximo_periodo_custeio + valor_custeio_rateios_nao_demonstrados
    row_custeio[SALDO_BANCARIO].value = f'C {formata_valor(valor_saldo_bancario_custeio)}'

    row_custeio[TOTAL_SALDO_BANCARIO].value = formata_valor(valor_saldo_bancario_capital + valor_saldo_bancario_custeio)


def creditos_demonstrados(worksheet, receitas, acc=0, start_line=21):
    quantidade = acc
    last_line = LAST_LINE + quantidade
    valor_total = sum(r.valor for r in receitas)
    ind = start_line

    for linha, receita in enumerate(receitas):
        # Movendo as linhas para baixo antes de inserir os dados novos
        ind = start_line + quantidade + linha
        if linha > 0:
            for row_idx in range(last_line + linha, ind-2, -1):
                copy_row(worksheet, row_idx, 1, copy_data=True)

        row = list(worksheet.rows)[ind-1]
        row[ITEM].value = linha + 1
        row[1].value = receita.tipo_receita.nome
        row[4].value = receita.detalhamento
        row[7].value = receita.data.strftime("%d/%m/%Y")
        row[9].value = formata_valor(receita.valor)

    row = list(worksheet.rows)[(ind-1) + 1]
    row[9].value = formata_valor(valor_total)


def pagamentos(worksheet, rateios, acc=0, start_line=26):
    """
    BLOCO 4 - DESPESAS EFETUADAS NO PERÍODO
    BLOCO 5 - DESPESAS EFETUADAS E NÃO DEMONSTRADAS NO EXTRATO DO PERÍODO (ATUAL E ANTERIORES)
    """

    quantidade = acc if acc else 0
    last_line = LAST_LINE + quantidade
    valor_total = sum(r.valor_rateio for r in rateios)
    ind = start_line + quantidade
    for linha, rateio in enumerate(rateios):
        # Movendo as linhas para baixo antes de inserir os dados novos
        ind = start_line + quantidade + linha
        if linha > 0:
            for row_idx in range(last_line + linha, ind-2, -1):
                copy_row(worksheet, row_idx, 1, copy_data=True)

        row = list(worksheet.rows)[ind-1]
        row[ITEM].value = linha + 1
        row[RAZAO_SOCIAL].value = rateio.despesa.nome_fornecedor
        row[CNPJ_CPF].value = rateio.despesa.cpf_cnpj_fornecedor
        row[TIPO_DOCUMENTO].value = rateio.despesa.tipo_documento.nome if rateio.despesa.tipo_documento else ''
        row[NUMERO_DOCUMENTO].value = rateio.despesa.numero_documento
        row[ESPECIFICACAO_MATERIAL].value = rateio.especificacao_material_servico.descricao if rateio.especificacao_material_servico else ''
        row[TIPO_DESPESA].value = rateio.aplicacao_recurso

        tipo_transacao = ''
        if rateio.conta_associacao.tipo_conta:
            if rateio.conta_associacao.tipo_conta.nome == 'Cheque':
                tipo_transacao = rateio.despesa.documento_transacao
            else:
                tipo_transacao = rateio.despesa.tipo_transacao.nome

        row[TIPO_TRANSACAO].value = tipo_transacao
        row[DATA].value = rateio.despesa.data_documento.strftime("%d/%m/%Y") if rateio.despesa.data_documento else ''
        row[DATA_2].value = rateio.despesa.data_documento.strftime("%d/%m/%Y") if rateio.despesa.data_documento else ''
        row[VALOR].value = formata_valor(rateio.valor_rateio)

    row = list(worksheet.rows)[(ind-1)+1]
    row[9].value = formata_valor(valor_total)


def observacoes(worksheet, acao_associacao):
    """BLOCO 6 - OBSERVAÇÃO"""

    start_line = 36
    row = list(worksheet.rows)[start_line]
    row[ITEM].value = Observacao.objects.filter(acao_associacao=acao_associacao).first().texto if Observacao.objects.filter(acao_associacao=acao_associacao).exists() else ''


def copy_row(ws, source_row, dest_row, copy_data=False, copy_style=True, copy_merged_columns=True):
    """Copia uma linha da planilha para a linha imediatamento abaixo mantendo todos os atributos."""
    CELL_RE = re.compile("(?P<col>\$?[A-Z]+)(?P<row>\$?\d+)")

    def replace(m):
        row = m.group('row')
        prefix = "$" if row.find("$") != -1 else ""
        row = int(row.replace("$", ""))
        row += dest_row if row > source_row else 0
        return m.group('col') + prefix + str(row)

    # Fazendo unmerge das celulas de destino.
    mergedcells = []
    for group in ws.merged_cells.ranges:
        mergedcells.append(group)

    for cr in mergedcells:
        min_col, min_row, max_col, max_row = range_boundaries(str(cr))
        if max_row == min_row == source_row + 1:
            ws.unmerge_cells(str(cr))

    new_row_idx = source_row + 1
    for row in range(new_row_idx, new_row_idx + dest_row):
        new_rd = copy(ws.row_dimensions[row-1])
        new_rd.index = row
        ws.row_dimensions[row] = new_rd

        for col in range(ws.max_column):
            col = get_column_letter(col+1)
            cell = ws['%s%d' % (col, row)]
            source = ws['%s%d' % (col, row-1)]
            if copy_style:
                cell._style = copy(source._style)
            if copy_data and not isinstance(cell, MergedCell):
                cell.data_type = source.data_type
                cell.value = source.value

    for cr_idx, cr in enumerate(ws.merged_cell_ranges):
        ws.merged_cell_ranges[cr_idx] = CELL_RE.sub(
            replace,
            str(cr)
        )

    if copy_merged_columns:
        for cr in ws.merged_cells.ranges:
            min_col, min_row, max_col, max_row = range_boundaries(str(cr))
            if max_row == min_row == source_row:
                for row in range(new_row_idx, new_row_idx + dest_row):
                    newCellRange = get_column_letter(min_col) + str(row) + ":" + get_column_letter(max_col) + str(row)
                    ws.merge_cells(newCellRange)


def formata_valor(valor):
    locale.setlocale(locale.LC_MONETARY, "pt_BR.UTF-8")

    return locale.currency(valor, grouping=True).split(" ")[1]
