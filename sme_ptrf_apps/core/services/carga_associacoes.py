import csv
import logging
import os
from brazilnum.cnpj import validate_cnpj, format_cnpj

from django.contrib.staticfiles.storage import staticfiles_storage

from ..models import Associacao, Unidade

logger = logging.getLogger(__name__)

__EOL_UE = 0
__NOME_UE = 1
__EOL_DRE = 2
__NOME_DRE = 3
__SIGLA_DRE = 4
__NOME_ASSOCIACAO = 5
__CNPJ_ASSOCIACAO = 6
__RF_PRESIDENTE_DIRETORIA = 7
__NOME_PRESIDENTE_DIRETORIA = 8
__RF_PRESIDENTE_CONSELHO = 9
__NOME_PRESIDENTE_CONSELHO = 10

def carrega_associacoes():
    def cria_ou_atualiza_dre_from_row(row):
        eol_dre = row[__EOL_DRE]
        dre, created = Unidade.objects.update_or_create(
            codigo_eol=eol_dre,
            defaults={
                'tipo_unidade': 'DRE',
                'dre': None,
                'sigla': row[__SIGLA_DRE],
                'nome': row[__NOME_DRE]
            },
        )
        if created:
            logger.debug(f'Criada DRE {dre.nome}')

        return dre

    def cria_ou_atualiza_unidade_from_row(row, dre, lin):
        eol_unidade = row[__EOL_UE]
        tipo_unidade, _, nome_unidade = row[__NOME_UE].partition(" ")

        if (tipo_unidade, tipo_unidade) not in Unidade.TIPOS_CHOICE:
            logger.error(f'Tipo de unidade inválido ({tipo_unidade}) na linha {lin}. Trocado para EMEF.')
            tipo_unidade = 'EMEF'

        unidade, created = Unidade.objects.update_or_create(
            codigo_eol=eol_unidade,
            defaults={
                'tipo_unidade': tipo_unidade,
                'dre': dre,
                'sigla': '',
                'nome': nome_unidade
            },
        )
        if created:
            logger.debug(f'Criada Unidade {unidade.nome}')

        return unidade

    def cria_ou_atualiza_associacao_from_row(row, unidade):

        cnpj = row[__CNPJ_ASSOCIACAO]
        if not validate_cnpj(cnpj):
            logger.error(f'CNPJ inválido ({cnpj}) na linha {lin}. Associação não criada.')
            return None

        cnpj = format_cnpj(cnpj)

        associacao, created = Associacao.objects.update_or_create(
            cnpj=cnpj,
            defaults={
                'unidade': unidade,
                'nome': row[__NOME_ASSOCIACAO],
                'presidente_associacao_nome': row[__NOME_PRESIDENTE_DIRETORIA],
                'presidente_associacao_rf': row[__RF_PRESIDENTE_DIRETORIA],
                'presidente_conselho_fiscal_nome': row[__NOME_PRESIDENTE_CONSELHO],
                'presidente_conselho_fiscal_rf': row[__RF_PRESIDENTE_CONSELHO],
            },
        )

        if created:
            logger.debug(f'Criada Associacao {associacao.nome}')

        return associacao

    logger.info(f'Carregando arquivo de associações...')

    f = staticfiles_storage.open(os.path.join('cargas', 'associacoes.csv'), 'r')

    reader = csv.reader(f, delimiter=',')

    lin = 0
    importadas = 0
    erros = 0
    for row in reader:
        if lin == 0:
            lin += 1
            continue  # Pula cabeçalho.
        lin += 1
        logger.debug(f'Linha {lin}: {row}')

        dre = cria_ou_atualiza_dre_from_row(row)
        unidade = cria_ou_atualiza_unidade_from_row(row, dre, lin)
        associacao = cria_ou_atualiza_associacao_from_row(row, unidade)

        if associacao:
            importadas += 1
        else:
            erros += 1

    f.close()

    logger.info(f'Importadas {importadas} associações. Erro na importação de {erros} associações.')
