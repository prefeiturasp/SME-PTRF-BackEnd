"""
Módulo responsável pela montagem do arquivo de demonstrativo financeiro.

Autor: Anderson Marques Morais
update: 11/05/2020
"""

import logging
from copy import copy

from openpyxl import load_workbook

from sme_ptrf_apps.despesas.models import RateioDespesa

LOGGER = logging.getLogger(__name__)
CELL_STYLE = {
    'font': '',
    'border': '',
    'fill': '',
    'number_format': '',
    'protection': '',
    'alignment':'',
}
STYLES = []

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

COL_CABECALHO = 9
LINHA_PERIODO_CABECALHO = 4
LINHA_ACAO_CABECALHO = 5
LINHA_CONTA_CABECALHO = 6


def gerar(periodo, acao_associacao, conta_associacao, prestacao_conta):
    print("GERAR DEMONSTRATIVO")
    print(periodo)
    #/home/anderson/workspace/amcom_workspace/teste_biblioteca_planilha/planilha_result.xlsx
    workbook = load_workbook('sme_ptrf_apps/core/tests/tests_demonstrativo_financeiro/files/modelo_demonstrativo_financeiro.xlsx')  
    # Aqui precisarei adicionar o filtro para depesa que esteja CONFERIDA
    rateios = RateioDespesa.rateios_da_acao_associacao_no_periodo(acao_associacao=acao_associacao, periodo=periodo)
    
    worksheet = workbook.active
    # Aqui em vez de passar o worksheet passar as linhas e assim evito de chamar list toda vez 
    cabecalho(worksheet, periodo, acao_associacao, conta_associacao)
    identificacao_apm(worksheet, prestacao_conta)
    estilo_pagamentos_efetuados(worksheet)
    pagamentos_efetuados(worksheet, rateios)
    workbook.save('sme_ptrf_apps/core/tests/tests_demonstrativo_financeiro/files/modelo_demonstrativo_financeiro_result2.xlsx')
    return True


def cabecalho(worksheet, periodo, acao_associacao, conta_associacao):
    rows = list(worksheet.rows)
    rows[LINHA_PERIODO_CABECALHO][COL_CABECALHO].value = str(periodo)
    rows[LINHA_ACAO_CABECALHO][COL_CABECALHO].value = acao_associacao.acao.nome
    rows[LINHA_CONTA_CABECALHO][COL_CABECALHO].value = conta_associacao.tipo_conta.nome


def identificacao_apm(worksheet, prestacao_conta):
    """BLOCO 1 - IDENTIFICAÇÃO DA APM/APMSUAC DA UNIDADE EDUCACIONAL"""
    rows = list(worksheet.rows)
    rows[10][0].value = prestacao_conta.associacao.nome
    rows[10][6].value = prestacao_conta.associacao.cnpj
    rows[10][7].value = prestacao_conta.associacao.unidade.codigo_eol
    rows[10][8].value = prestacao_conta.associacao.unidade.dre.nome


def estilo_pagamentos_efetuados(worksheet):
    row = list(worksheet.rows)[LINHA_MODELO_PAGAMENTOS_EFETUADOS]
    for cell in row[:VALOR+1]:
        estilo = copy(CELL_STYLE)
        estilo['font'] = copy(cell.font)
        estilo['border'] = copy(cell.border)
        estilo['fill'] = copy(cell.fill)
        estilo['number_format'] = copy(cell.number_format)
        estilo['protection'] = copy(cell.protection)
        estilo['alignment'] = copy(cell.alignment)
        STYLES.append(estilo)


def atualiza_estilo(celula, coluna):
    celula.font = STYLES[coluna]['font']
    celula.fill = STYLES[coluna]['fill']
    celula.number_format = STYLES[coluna]['number_format']
    celula.protection = STYLES[coluna]['protection']
    celula.alignment = STYLES[coluna]['alignment']


def pagamentos_efetuados(worksheet, rateios):
    """BLOCO 3 - Pagamentos Efetuados e Demonstrados"""
    
    # Para o Primeiro Rateio adiciono os dados do rateio
    for linha, rateio in enumerate(rateios):
        ind = LINHA_MODELO_PAGAMENTOS_EFETUADOS + linha
        worksheet.insert_rows(idx=ind)
        row = list(worksheet.rows)[ind-1]
        atualiza_estilo(row[ITEM], ITEM)
        row[ITEM].value = linha + 1
        
        atualiza_estilo(row[RAZAO_SOCIAL], RAZAO_SOCIAL)
        row[RAZAO_SOCIAL].value = rateio.despesa.nome_fornecedor
        
        atualiza_estilo(row[CNPJ_CPF], CNPJ_CPF)
        row[CNPJ_CPF].value = rateio.despesa.cpf_cnpj_fornecedor
        
        atualiza_estilo(row[TIPO_DOCUMENTO], TIPO_DOCUMENTO)
        row[TIPO_DOCUMENTO].value = rateio.despesa.tipo_documento.nome
        
        atualiza_estilo(row[NUMERO_DOCUMENTO], NUMERO_DOCUMENTO)
        row[NUMERO_DOCUMENTO].value = rateio.despesa.numero_documento
        
        atualiza_estilo(row[DATA], DATA)
        row[DATA].value = rateio.despesa.data_documento
        
        atualiza_estilo(row[ESPECIFICACAO_MATERIAL], ESPECIFICACAO_MATERIAL)
        row[ESPECIFICACAO_MATERIAL].value = rateio.especificacao_material_servico.descricao
        
        atualiza_estilo(row[TIPO_DESPESA], TIPO_DESPESA)
        row[TIPO_DESPESA].value = rateio.aplicacao_recurso
        
        atualiza_estilo(row[TIPO_TRANSACAO], TIPO_TRANSACAO)
        row[TIPO_TRANSACAO].value = rateio.despesa.tipo_transacao.nome
        
        atualiza_estilo(row[DATA_2], DATA_2)
        row[DATA_2].value = rateio.despesa.data_documento
        
        atualiza_estilo(row[VALOR], VALOR)
        row[VALOR].value = rateio.valor_rateio
