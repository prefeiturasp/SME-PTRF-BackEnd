"""
Módulo responsável pela montagem do arquivo de demonstrativo financeiro.

Autor: Anderson Marques Morais
update: 11/05/2020
"""

import logging
import os
import re
from copy import copy
from tempfile import NamedTemporaryFile

from django.contrib.staticfiles.storage import staticfiles_storage
from openpyxl import load_workbook
from openpyxl.cell.cell import Cell, MergedCell
from openpyxl.utils import column_index_from_string, get_column_letter, range_boundaries
from openpyxl.utils.cell import coordinate_from_string

from sme_ptrf_apps.core.models import Associacao, FechamentoPeriodo
from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CUSTEIO
from sme_ptrf_apps.receitas.models import Receita

LOGGER = logging.getLogger(__name__)

COL_CABECALHO = 9
LINHA_PERIODO_CABECALHO = 4
LINHA_ACAO_CABECALHO = 5
LINHA_CONTA_CABECALHO = 6
LAST_LINE = 42

# Coluna 2 da planilha 
SALDO_ANTERIOR = 0
REPASSE = 2
RENDIMENTO = 3
OUTRAS_RECEITAS = 4
VALOR_TOTAL = 6
DESPESA_REALIZADA = 7
SALDO_REPROGRAMADO = 8
TOTAL_REPROGRAMADO = 10

# Colunas dos blocos 3 e 4 da planilha
LINHA_MODELO_PAGAMENTOS_EFETUADOS = 21
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
    rateios_conferidos = RateioDespesa.rateios_da_acao_associacao_no_periodo(acao_associacao=acao_associacao, periodo=periodo, conferido=True)
    rateios_nao_conferidos = RateioDespesa.rateios_da_acao_associacao_no_periodo(acao_associacao=acao_associacao, periodo=periodo, conferido=False)
    receitas_nao_demonstradas = Receita.receitas_da_acao_associacao_no_periodo(acao_associacao=acao_associacao, periodo=periodo, conferido=False)
    fechamento_periodo = FechamentoPeriodo.objects.filter(acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo).first()
    path = os.path.join(os.path.basename(staticfiles_storage.location), 'cargas')
    nome_arquivo = os.path.join(path, 'modelo_demonstrativo_financeiro.xlsx')
    workbook = load_workbook(nome_arquivo)
    worksheet = workbook.active

    cabecalho(worksheet, periodo, acao_associacao, conta_associacao)
    identificacao_apm(worksheet, acao_associacao)
    sintese_receita_despesa(worksheet, fechamento_periodo, rateios_conferidos)
    pagamentos(worksheet, rateios_conferidos)
    pagamentos(worksheet, rateios_nao_conferidos, acc=len(rateios_conferidos), start_line=26)
    creditos_nao_demonstrados(worksheet, receitas_nao_demonstradas, acc=len(rateios_conferidos)+len(rateios_nao_conferidos))
    
    stream = None
    with NamedTemporaryFile() as tmp:
        workbook.save(tmp.name)
        tmp.seek(0)
        stream = tmp.read()

    return stream


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


def sintese_receita_despesa(worksheet, fechamento_periodo, rateios_conferidos):
    saldo_reprogramado_anterior_capital = fechamento_periodo.fechamento_anterior.saldo_reprogramado_capital if fechamento_periodo.fechamento_anterior else 0
    saldo_reprogramado_anterior_custeio = fechamento_periodo.fechamento_anterior.saldo_reprogramado_custeio if fechamento_periodo.fechamento_anterior else 0
    
    valor_despesas_capital = sum(r.valor_rateio for r in rateios_conferidos if r.aplicacao_recurso == APLICACAO_CAPITAL)
    valor_despesas_custeio = sum(r.valor_rateio for r in rateios_conferidos if r.aplicacao_recurso == APLICACAO_CUSTEIO)

    receita_q = Receita.objects.filter(
                acao_associacao=fechamento_periodo.acao_associacao, 
                conta_associacao=fechamento_periodo.conta_associacao,
                conferido=True)

    receitas_repasse_capital = receita_q.filter(tipo_receita__e_repasse=True, categoria_receita=APLICACAO_CAPITAL).values_list('valor')
    receitas_repasse_custeio = receita_q.filter(tipo_receita__e_repasse=True, categoria_receita=APLICACAO_CUSTEIO).values_list('valor')
    receitas_rendimento = receita_q.filter(tipo_receita__e_rendimento=True).values_list('valor')
    outras_receitas_capital = receita_q.filter(tipo_receita__e_repasse=False, tipo_receita__e_rendimento=False, categoria_receita=APLICACAO_CAPITAL).values_list('valor')
    outras_receitas_custeio = receita_q.filter(tipo_receita__e_repasse=False, tipo_receita__e_rendimento=False, categoria_receita=APLICACAO_CUSTEIO).values_list('valor')

    valor_receita_repasse_capital = sum(rrc[0] for rrc in receitas_repasse_capital) if receitas_repasse_capital else 0
    valor_receita_repasse_custeio = sum(rrk[0] for rrk in receitas_repasse_custeio) if receitas_repasse_custeio else 0
    valor_receita_rendimento = sum(ren[0] for ren in receitas_rendimento) if receitas_rendimento else 0
    valor_outras_receitas_capital = sum(orc[0] for orc in outras_receitas_capital) if outras_receitas_capital else 0
    valor_outras_receitas_custeio = sum(ork[0] for ork in outras_receitas_custeio) if outras_receitas_custeio else 0

    row_capital = list(worksheet.rows)[14]
    row_custeio = list(worksheet.rows)[15]

    row_capital[SALDO_ANTERIOR].value = saldo_reprogramado_anterior_capital
    row_capital[REPASSE].value = valor_receita_repasse_capital
    row_capital[RENDIMENTO].value = valor_receita_rendimento
    row_capital[OUTRAS_RECEITAS].value = valor_outras_receitas_capital
    row_capital[VALOR_TOTAL].value = saldo_reprogramado_anterior_capital + valor_receita_repasse_capital + valor_receita_rendimento + valor_outras_receitas_capital
    row_capital[DESPESA_REALIZADA].value = valor_despesas_capital
    row_capital[SALDO_REPROGRAMADO].value = fechamento_periodo.saldo_reprogramado_capital

    row_custeio[SALDO_ANTERIOR].value = saldo_reprogramado_anterior_custeio
    row_custeio[REPASSE].value = valor_receita_repasse_custeio
    row_custeio[OUTRAS_RECEITAS].value = valor_outras_receitas_custeio
    row_custeio[VALOR_TOTAL].value = saldo_reprogramado_anterior_custeio + valor_receita_repasse_custeio + valor_outras_receitas_custeio
    row_custeio[DESPESA_REALIZADA].value = valor_despesas_custeio
    row_custeio[SALDO_REPROGRAMADO].value = fechamento_periodo.saldo_reprogramado_custeio

    row_capital[TOTAL_REPROGRAMADO].value = fechamento_periodo.saldo_reprogramado_custeio + fechamento_periodo.saldo_reprogramado_capital


def pagamentos(worksheet, rateios, acc=0, start_line=21):
    """
    BLOCO 3 - PAGAMENTOS EFETUADOS E DEMONSTRADOS
    BLOCO 4 - DÉBITOS NÃO DEMONSTRADOS NO EXTRATO DO PERÍODO
    """

    quantidade = acc-1 if acc else 0
    last_line = LAST_LINE + quantidade
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
        row[TIPO_TRANSACAO].value = rateio.despesa.tipo_transacao.nome if rateio.despesa.tipo_transacao else ''
        row[DATA].value = rateio.despesa.data_documento.strftime("%d/%m/%Y") if rateio.despesa.data_documento else ''
        row[DATA_2].value = rateio.despesa.data_documento.strftime("%d/%m/%Y") if rateio.despesa.data_documento else ''
        row[VALOR].value = rateio.valor_rateio


def creditos_nao_demonstrados(worksheet, receitas, acc=0):
    """BLOCO 5 - PAGAMENTOS EFETUADOS E DEMONSTRADOS"""

    quantidade = acc-2 if acc > 2 else 0
    last_line = LAST_LINE + quantidade
    start_line = 30
    for linha, receita in enumerate(receitas):
        # Movendo as linhas para baixo antes de inserir os dados novos
        ind = start_line + quantidade + linha
        if linha > 0:
            for row_idx in range(last_line + linha, ind-2, -1):
                copy_row(worksheet, row_idx, 1, copy_data=True)

        row = list(worksheet.rows)[ind-1]
        row[ITEM].value = linha + 1
        row[1].value = receita.tipo_receita.nome
        row[5].value = receita.data.strftime("%d/%m/%Y")
        row[7].value = receita.valor


def copy_row(ws, source_row, dest_row, copy_data=False, copy_style=True, copy_merged_columns=True):
    """Copia uma linha da planilha para a linha imediatamento abaixo mantendo todos os atributos."""
    CELL_RE  = re.compile("(?P<col>\$?[A-Z]+)(?P<row>\$?\d+)")

    def replace(m):
        row = m.group('row')
        prefix = "$" if row.find("$") != -1 else ""
        row = int(row.replace("$", ""))
        row += dest_row if row > source_row else 0
        return m.group('col') + prefix + str(row)

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
                s_coor = source.coordinate
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
