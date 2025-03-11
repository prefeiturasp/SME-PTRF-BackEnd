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

def agrupar_por_eol_conta_e_periodo(reader):
    grouped_data= {}
    for lin, row in enumerate(reader):
        try:
            if lin != 0:
                try:
                    cod_eol = row[CODIGO_EOL]
                    conta = row[CONTA]
                    acao = row[ACAO]
                    periodo = row[PERIODO]
                    valor_capital = get_valor(row[VALOR_CAPITAL])
                    valor_custeio = get_valor(row[VALOR_CUSTEIO])
                    valor_livre = get_valor(row[VALOR_LIVRE])

                    chave = (cod_eol, conta, periodo)

                    if chave not in grouped_data:
                        grouped_data[chave] = {
                            'Custeio': 0.0,
                            'Capital': 0.0,
                            'Livre Aplicacao': 0.0,
                            'Linhas': [],
                            'Cod_eol': cod_eol,
                            'Conta': conta,
                            'Acao': acao,
                            'Periodo': periodo
                        }

                    grouped_data[chave]['Custeio'] += valor_custeio
                    grouped_data[chave]['Capital'] += valor_capital
                    grouped_data[chave]['Livre Aplicacao'] += valor_livre
                    grouped_data[chave]['Linhas'].append(lin)
                except Exception as e:
                    msg_erro = f'Erro no agrupamento dos dados. {str(e)}'
                    raise Exception(msg_erro)

        except Exception as e:
            msg_erro = f"Erro na linha {lin}: {str(e)}"
            logger.info(msg_erro)

    return grouped_data

def processa_previsoes_repasse(reader, arquivo):
    logs = []
    importados = 0
    atualizados = 0
    erros = 0

    agrupados = agrupar_por_eol_conta_e_periodo(reader)

    for chave, valores in agrupados.items():
        try:
            logger.info('Linha %s: %s', str(valores['Linhas']), valores)

            cod_eol, conta, periodo = chave
            valor_capital = valores['Capital']
            valor_custeio = valores['Custeio']
            valor_livre = valores['Livre Aplicacao']
            acao = valores['Acao']

            associacao = get_associacao(str(cod_eol).strip())
            if not associacao:
                msg_erro = f'Associação com código eol: {cod_eol} não encontrado.'
                raise Exception(msg_erro)

            conta_associacao = get_conta_associacao(associacao, str(conta).strip())
            if not conta_associacao:
                msg_erro = f'Conta associação com nome: {conta} não encontrado.'
                raise Exception(msg_erro)

            acao_associacao = get_acao_associacao(associacao, str(acao).strip())
            if not acao_associacao:
                msg_erro = f'Ação associação com nome: {acao} não encontrado.'
                raise Exception(msg_erro)

            periodo = get_periodo(str(periodo).strip())
            if not periodo:
                msg_erro = f"Período ({str(periodo)}) não encontrado."
                raise Exception(msg_erro)

            data_referencia = periodo.data_fim_realizacao_despesas if periodo.data_fim_realizacao_despesas else periodo.data_inicio_realizacao_despesas

            if associacao.encerrada and (data_referencia >= associacao.data_de_encerramento):
                msg_erro = f'A associação foi encerrada em {associacao.data_de_encerramento.strftime("%d/%m/%Y")}'
                raise Exception(msg_erro)

            if associacao.periodo_inicial and (data_referencia <= associacao.periodo_inicial.data_fim_realizacao_despesas):
                msg_erro = f'O período informado é anterior ao período inicial da associação'
                raise Exception(msg_erro) 

            if valor_capital > 0 or valor_custeio > 0 or valor_livre > 0:
                previsao_repasse, created = PrevisaoRepasseSme.objects.update_or_create(
                    associacao=associacao,
                    conta_associacao=conta_associacao,
                    periodo=periodo,
                    carga=arquivo,
                    defaults={
                        'valor_capital': valor_capital,
                        'valor_custeio': valor_custeio,
                        'valor_livre': valor_livre,
                    }
                )

                if created:
                    importados += 1
                    logger.info("Previsão repasse criada com sucesso: %s", previsao_repasse)
                else:
                    atualizados +=1
                    logger.info("Previsão repasse atualizada com sucesso: %s", previsao_repasse)
            else:
                msg_erro = "Valores não estão de acordo com o esperado. Valor capital: {valor_capital}, Valor custeio: {valor_custeio}, Valor livre: {valor_livre}"
                raise Exception(msg_erro)
        except Exception as e:
            msg_erro = f"Erro na linha {str(valores['Linhas'])}: {str(e)}"
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
