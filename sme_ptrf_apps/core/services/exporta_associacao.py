
import logging
import os

from django.contrib.staticfiles.storage import staticfiles_storage
from openpyxl import load_workbook

LOGGER = logging.getLogger(__name__)

# Dados Básicos
NOME = 0
EOL = 1
DRE = 2
CNPJ = 3
CCM = 4
EMAIL = 5


def gerar_planilha(associacao):
    LOGGER.info(f'EXPORTANDO DADOS DA ASSOCIACAO {associacao.nome}...')

    path = os.path.join(os.path.basename(staticfiles_storage.location), 'modelos')
    nome_arquivo = os.path.join(path, 'modelo_exportacao_associacao.xlsx')
    workbook = load_workbook(nome_arquivo)
    worksheet = workbook.active

    dados_basicos(worksheet, associacao)

    return workbook


def dados_basicos(worksheet, associacao):
    rows = list(worksheet.rows)
    rows[NOME][1].value = associacao.nome
    rows[EOL][1].value = associacao.unidade.codigo_eol
    rows[DRE][1].value = associacao.unidade.dre.nome if associacao.unidade.dre else ''
    rows[CNPJ][1].value = associacao.cnpj
    rows[CCM][1].value = associacao.ccm
    rows[EMAIL][1].value = associacao.email
