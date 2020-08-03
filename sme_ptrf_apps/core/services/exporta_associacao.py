import logging
import os

from django.contrib.staticfiles.storage import staticfiles_storage
from openpyxl import load_workbook

from ..choices.membro_associacao import RepresentacaoCargo

LOGGER = logging.getLogger(__name__)

# Worksheets
ASSOCIACAO = 0
MEMBROS = 1
CONTAS = 2

# Linhas Dados Básicos
NOME_ASSOCIACAO = 0
EOL = 1
DRE = 2
CNPJ = 3
CCM = 4
EMAIL_ASSOCIACAO = 5

# Colunas Membros
CARGO = 0
NOME_MEMBRO = 1
REPRESENTACAO = 2
RF_EOL = 3
CARGO_EDUCACAO = 4
EMAIL_MEMBRO = 5

# Linhas Membros
CARGOS = {
    'PRESIDENTE_DIRETORIA_EXECUTIVA': 1,
    'VICE_PRESIDENTE_DIRETORIA_EXECUTIVA': 2,
    'SECRETARIO': 3,
    'TESOUREIRO': 4,
    'VOGAL_1': 5,
    'VOGAL_2': 6,
    'VOGAL_3': 7,
    'VOGAL_4': 8,
    'VOGAL_5': 9,
    'PRESIDENTE_CONSELHO_FISCAL': 10,
    'CONSELHEIRO_1': 11,
    'CONSELHEIRO_2': 12,
    'CONSELHEIRO_3': 13,
    'CONSELHEIRO_4': 14,
}

# Colunas Contas da Associação
BANCO = 0
TIPO = 1
AGENCIA = 2
NUMERO = 3


def gerar_planilha(associacao):
    LOGGER.info(f'EXPORTANDO DADOS DA ASSOCIACAO {associacao.nome}...')

    path = os.path.join(os.path.basename(staticfiles_storage.location), 'modelos')
    nome_arquivo = os.path.join(path, 'modelo_exportacao_associacao.xlsx')
    workbook = load_workbook(nome_arquivo)

    dados_basicos(workbook, associacao)
    membros(workbook, associacao)
    contas(workbook, associacao)

    return workbook


def dados_basicos(workbook, associacao):
    worksheet = workbook.worksheets[ASSOCIACAO]
    rows = list(worksheet.rows)
    rows[NOME_ASSOCIACAO][1].value = associacao.nome
    rows[EOL][1].value = associacao.unidade.codigo_eol
    rows[DRE][1].value = associacao.unidade.dre.nome if associacao.unidade.dre else ''
    rows[CNPJ][1].value = associacao.cnpj
    rows[CCM][1].value = associacao.ccm
    rows[EMAIL_ASSOCIACAO][1].value = associacao.email


def membros(workbook, associacao):
    membros = associacao.cargos.all()
    worksheet = workbook.worksheets[MEMBROS]
    rows = list(worksheet.rows)
    for membro in membros:
        linha = CARGOS[membro.cargo_associacao]
        rows[linha][NOME_MEMBRO].value = membro.nome
        rows[linha][REPRESENTACAO].value =  RepresentacaoCargo[membro.representacao].value
        rows[linha][RF_EOL].value = membro.codigo_identificacao
        rows[linha][CARGO_EDUCACAO].value = membro.cargo_educacao
        rows[linha][EMAIL_MEMBRO].value = membro.email


def contas(workbook, associacao):
    contas = associacao.contas.all()
    worksheet = workbook.worksheets[CONTAS]
    rows = list(worksheet.rows)
    linha = 1
    for conta in contas:
        rows[linha][BANCO].value = conta.banco_nome
        rows[linha][TIPO].value = conta.tipo_conta.nome if conta.tipo_conta else ' '
        rows[linha][AGENCIA].value = conta.agencia
        rows[linha][NUMERO].value = conta.numero_conta
        linha += 1
