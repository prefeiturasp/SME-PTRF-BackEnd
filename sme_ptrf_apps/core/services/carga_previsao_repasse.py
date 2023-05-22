import csv
import datetime
import enum
import logging
import os

from sme_ptrf_apps.core.models import (
    Acao,
    AcaoAssociacao,
    Associacao,
    ContaAssociacao,
    Periodo,
    PrevisaoRepasseSme,
    TipoConta,
)
from sme_ptrf_apps.core.models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    ERRO,
    PROCESSADO_COM_ERRO,
    SUCESSO,
)

CODIGO_EOL = 0
CONTA = 1
ACAO = 2
PERIODO = 3
VALOR_CUSTEIO = 4
VALOR_CAPITAL = 5
VALOR_LIVRE = 6

__DELIMITADORES = {',': DELIMITADOR_VIRGULA, ';': DELIMITADOR_PONTO_VIRGULA}

logger = logging.getLogger(__name__)


def get_valor(val):
    if not val:
        return 0

    return float(str(val).replace(',', '.'))


def get_associacao(eol):
    return Associacao.objects.filter(unidade__codigo_eol=eol).first()


def get_acao(nome):
    if Acao.objects.filter(nome=nome).exists():
        return Acao.objects.filter(nome=nome).get()

    logger.info(f"Ação {nome} não encontrada. Registro será criado.")
    return Acao.objects.create(nome=nome)


def get_tipo_conta(nome):
    if TipoConta.objects.filter(nome=nome).exists():
        return TipoConta.objects.filter(nome=nome).get()

    logger.info(f"Tipo de conta {nome} não encontrado. Registro será criado.")
    return TipoConta.objects.create(nome=nome)


def get_acao_associacao(associacao, nome_acao):
    return AcaoAssociacao.objects.filter(associacao=associacao, acao__nome=nome_acao).first()


def get_conta_associacao(associacao, nome_tipo_conta):
    return ContaAssociacao.objects.filter(associacao=associacao, tipo_conta__nome=nome_tipo_conta).first()


def get_periodo(referencia):
    if Periodo.objects.filter(referencia=referencia).exists():
        return Periodo.objects.filter(referencia=referencia).get()
    return None


def processa_previsoes_repasse(reader, arquivo):
    logs = []
    importados = 0
    erros = 0
    for lin, row in enumerate(reader):
        try:
            if lin != 0:
                logger.info('Linha %s: %s', lin, row)
                if not any(row):
                    logger.info("Pulando linha %s que está vazia.", lin)
                    continue

                associacao = get_associacao(str(row[CODIGO_EOL]).strip())
                if not associacao:
                    msg_erro = f'Associação com código eol: {row[CODIGO_EOL]} não encontrado.'
                    raise Exception(msg_erro)

                conta_associacao = get_conta_associacao(associacao, str(row[CONTA]).strip())
                if not conta_associacao:
                    msg_erro = f'Conta associação com nome: {row[CONTA]} não encontrado.'
                    raise Exception(msg_erro)

                acao_associacao = get_acao_associacao(associacao, str(row[ACAO]).strip())
                if not acao_associacao:
                    msg_erro = f'Ação associação com nome: {row[ACAO]} não encontrado.'
                    raise Exception(msg_erro)

                periodo = get_periodo(str(row[PERIODO]).strip())
                if not periodo:
                    msg_erro = f"Período ({str(row[PERIODO])}) não encontrado."
                    raise Exception(msg_erro)

                data_referencia = periodo.data_fim_realizacao_despesas if periodo.data_fim_realizacao_despesas else periodo.data_inicio_realizacao_despesas

                if associacao.encerrada and (data_referencia >= associacao.data_de_encerramento):
                    msg_erro = f'A associação foi encerrada em {associacao.data_de_encerramento.strftime("%d/%m/%Y")}'
                    raise Exception(msg_erro)

                if associacao.periodo_inicial and (data_referencia <= associacao.periodo_inicial.data_fim_realizacao_despesas):
                    msg_erro = f'O período informado é anterior ao período inicial da associação'
                    raise Exception(msg_erro)

                valor_capital = get_valor(row[VALOR_CAPITAL])
                valor_custeio = get_valor(row[VALOR_CUSTEIO])
                valor_livre = get_valor(row[VALOR_LIVRE])

                if valor_capital > 0 or valor_custeio > 0 or valor_livre > 0:
                    previsao_repasse = PrevisaoRepasseSme.objects.filter(associacao=associacao, conta_associacao=conta_associacao, periodo=periodo).first()
                    if not previsao_repasse:
                        previsao_repasse = PrevisaoRepasseSme.objects.create(
                            associacao=associacao,
                            conta_associacao=conta_associacao,
                            periodo=periodo,
                            valor_capital=valor_capital,
                            valor_custeio=valor_custeio,
                            valor_livre=valor_livre
                        )
                        importados += 1
                        logger.info("Previsão repasse criada com sucesso: %s", previsao_repasse)
                    else:
                        previsao_repasse.valor_capital = float(previsao_repasse.valor_capital) + valor_capital
                        previsao_repasse.valor_custeio = float(previsao_repasse.valor_custeio) + valor_custeio
                        previsao_repasse.valor_livre = float(previsao_repasse.valor_livre) + valor_livre
                        previsao_repasse.save()
                        logger.info("Previsão repasse atualizada com sucesso: %s", previsao_repasse)
                else:
                    msg_erro = "Valores não estão de acordo com o esperado. Valor capital: {valor_capital}, Valor custeio: {valor_custeio}, Valor livre: {valor_livre}"
                    raise Exception(msg_erro)
        except Exception as e:
            msg_erro = f"Erro na linha {lin}: {str(e)}"
            logger.info(msg_erro)
            logs.append(msg_erro)
            erros += 1

    if importados > 0 and erros > 0:
        arquivo.status = PROCESSADO_COM_ERRO
    elif erros > 0:
        arquivo.status = ERRO
    else:
        arquivo.status = SUCESSO

    msg = f"Importados {importados} previsões de repasse. Erro na importação de {erros} previsões."
    logs.append(msg)
    logger.info(msg)

    arquivo.log = "\n".join(logs)
    arquivo.save()


def carrega_previsoes_repasses(arquivo):
    logger.info("Processando arquivo de previsoes de repasse %s", arquivo.identificador)
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
            processa_previsoes_repasse(reader, arquivo)
    except Exception as err:
        msg_erro = f"Erro ao processar previsões de repasses sme: {str(err)}"
        logger.info(msg_erro)
        arquivo.log = msg_erro
        arquivo.status = ERRO
        arquivo.save()
