import csv
import datetime
import logging

from sme_ptrf_apps.core.models import Associacao, Periodo
from sme_ptrf_apps.core.models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    ERRO,
    PROCESSADO_COM_ERRO,
    SUCESSO,
)

logger = logging.getLogger(__name__)
CODIGO_EOL = 0
PERIODO = 1
__DELIMITADORES = {',': DELIMITADOR_VIRGULA, ';': DELIMITADOR_PONTO_VIRGULA}


def processa_periodo_inicial(reader, arquivo):
    logs = ""
    importados = 0
    erros = 0
    for index, row in enumerate(reader):
        if index != 0:
            logger.info('Linha %s: %s', index, row)

            try:
                associacao = get_associacao(str(row[CODIGO_EOL]).strip())
                if not associacao:
                    msg_erro = f"Associação ({str(row[CODIGO_EOL])}) não encontrado. Linha: {index}"
                    raise Exception(msg_erro)

                periodo = get_periodo(str(row[PERIODO]).strip())
                if not periodo:
                    msg_erro = f"Período ({str(row[PERIODO])}) não encontrado. Linha: {index}"
                    raise Exception(msg_erro)

                data_referencia = periodo.data_fim_realizacao_despesas if periodo.data_fim_realizacao_despesas else periodo.data_inicio_realizacao_despesas

                if associacao.encerrada and (data_referencia >= associacao.data_de_encerramento):
                    msg_erro = f'A associação foi encerrada em {associacao.data_de_encerramento.strftime("%d/%m/%Y")}. Linha ID:{index}'
                    raise Exception(msg_erro)

                if associacao.periodo_inicial and (data_referencia <= associacao.periodo_inicial.data_fim_realizacao_despesas):
                    msg_erro = f'O período informado é anterior ao período inicial da associação. Linha ID:{index}'
                    raise Exception(msg_erro)

                associacao.periodo_inicial = periodo
                associacao.save()
                logger.info("Periodo inicial da associação %s importado com sucesso.", associacao)
                importados += 1

            except Exception as e:
                msg = f"Erro na linha {index}: {str(e)}"
                logger.info(msg)

                logs = f'{logs}\n{msg}'
                erros += 1

    if importados > 0 and erros > 0:
        arquivo.status = PROCESSADO_COM_ERRO
    elif importados == 0:
        arquivo.status = ERRO
    else:
        arquivo.status = SUCESSO

    logs = f"{logs}\nImportados {importados} períodos iniciais. Erro na importação de {erros} períodos iniciais."
    logger.info(f'Importados {importados} períodos iniciais. Erro na importação de {erros} períodos iniciais.')

    arquivo.log = logs
    arquivo.save()

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
    arquivo.ultima_execucao = datetime.datetime.now()

    try:
        with open(arquivo.conteudo.path, 'r', encoding="utf-8") as f:
            sniffer = csv.Sniffer().sniff(f.readline())
            f.seek(0)
            if  __DELIMITADORES[sniffer.delimiter] != arquivo.tipo_delimitador:
                msg_erro = f"Formato definido ({arquivo.tipo_delimitador}) é diferente do formato do arquivo csv ({__DELIMITADORES[sniffer.delimiter]})"
                logger.info(msg_erro)
                arquivo.status = ERRO
                arquivo.log = msg_erro
                arquivo.save()
                return

            reader = csv.reader(f, delimiter=sniffer.delimiter)
            processa_periodo_inicial(reader, arquivo)

        logger.info("Carga de Períodos efetuada com sucesso.")
    except Exception as err:
        logger.info("Erro ao processar períodos: %s", str(err))
        arquivo.log = "Erro ao processar períodos."
        arquivo.save()
