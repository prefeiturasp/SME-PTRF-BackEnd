import csv
import logging

from sme_ptrf_apps.core.models import Associacao, Periodo

logger = logging.getLogger(__name__)
CODIGO_EOL = 0
PERIODO = 1


def processa_periodo_inicial(reader):
    for index, row in enumerate(reader):
        if index != 0:
            logger.info('Linha %s: %s', index, row)
            associacao = get_associacao(str(row[CODIGO_EOL]).strip())
            if not associacao:
                logger.info("Associação não encontrado.")
                continue

            periodo = get_periodo(str(row[PERIODO]).strip())
            if not periodo:
                logger.info("Período não encontrado.")
                continue
            associacao.periodo_inicial = periodo
            associacao.save()
            logger.info("Periodo inicial da associação %s importado com sucesso.", associacao)


def get_associacao(eol):
    if Associacao.objects.filter(unidade__codigo_eol=eol).exists():
        return  Associacao.objects.filter(unidade__codigo_eol=eol).get()
    return None


def get_periodo(referencia):
    if Periodo.objects.filter(referencia=referencia).exists():
        return Periodo.objects.filter(referencia=referencia).get()
    return None


def carrega_periodo_inicial(arquivo):
    logger.info("Executando Carga de Período inicial para associações.")

    with open(arquivo.conteudo.path, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        processa_periodo_inicial(reader)

    logger.info("Carga de Períodos efetuada com sucesso.")
