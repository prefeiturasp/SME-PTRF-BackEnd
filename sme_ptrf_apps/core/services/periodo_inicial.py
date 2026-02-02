import csv
import datetime
import logging
from waffle import get_waffle_flag_model
from django.db.models import Q
from sme_ptrf_apps.core.models import Associacao, Periodo, Recurso, PeriodoInicialAssociacao
from sme_ptrf_apps.core.models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    ERRO,
    PROCESSADO_COM_ERRO,
    SUCESSO,
)
flags = get_waffle_flag_model()
logger = logging.getLogger(__name__)
CODIGO_EOL = 0
PERIODO = 1
RECURSO = 2
__DELIMITADORES = {',': DELIMITADOR_VIRGULA, ';': DELIMITADOR_PONTO_VIRGULA}


def processa_periodo_inicial(reader, arquivo):
    logs = ""
    importados = 0
    erros = 0
    flag_premio_ativa = flags.objects.filter(name='premio-excelencia', everyone=True).exists()

    for index, row in enumerate(reader):
        if index != 0:
            logger.info('Linha %s: %s', index, row)

            try:
                codigo_associacao = str(row[CODIGO_EOL]).strip()
                periodo_codigo = str(row[PERIODO]).strip()
                recurso_codigo = str(row[RECURSO]).strip() if flag_premio_ativa else None

                def raise_erro(msg):
                    raise Exception(f"{msg}. Linha ID:{index}")

                associacao = get_associacao(codigo_associacao)
                if not associacao:
                    raise_erro(f"Associação ({codigo_associacao}) não encontrado")

                recurso = None
                if flag_premio_ativa:
                    recurso = get_recurso(recurso_codigo)
                    if not recurso:
                        raise_erro(f"Recurso ({recurso_codigo}) não encontrado")

                    periodo = get_periodo_por_recurso(periodo_codigo, recurso)
                    if not periodo:
                        raise_erro(f"Período ({periodo_codigo}) não encontrado para o recurso {recurso}")
                else:
                    periodo = get_periodo(periodo_codigo)
                    if not periodo:
                        raise_erro(f"Período ({periodo_codigo}) não encontrado")

                data_referencia = (
                    periodo.data_fim_realizacao_despesas or
                    periodo.data_inicio_realizacao_despesas
                )

                if associacao.encerrada and data_referencia >= associacao.data_de_encerramento:
                    raise_erro(
                        f'A associação foi encerrada em '
                        f'{associacao.data_de_encerramento.strftime("%d/%m/%Y")}'
                    )

                deve_validar_periodo_inicial = (
                    not flag_premio_ativa or (recurso and recurso.legado)
                )

                if deve_validar_periodo_inicial:
                    if associacao.periodo_inicial and data_referencia <= associacao.periodo_inicial.data_fim_realizacao_despesas:
                        raise_erro("O período informado é anterior ao período inicial da associação")

                    response = associacao.pode_editar_periodo_inicial
                    if not response["pode_editar_periodo_inicial"]:
                        mensagem = " ".join(response["mensagem_pode_editar_periodo_inicial"])
                        raise_erro(mensagem)

                    associacao.periodo_inicial = periodo
                    associacao.save()

                    logger.info("Periodo inicial da associação %s importado com sucesso.", associacao)
                    importados += 1

                if flag_premio_ativa and recurso:
                    periodo_inicial = associacao.periodos_iniciais.filter(recurso=recurso)

                    if periodo_inicial.exists() and associacao.prestacoes_de_conta_da_associacao.filter(
                        periodo__recurso=recurso
                    ).exists():
                        raise Exception(
                            "Não é permitido alterar o período inicial da Associação. "
                            "Há cadastros já realizados pela Associação no primeiro período de uso do sistema."
                        )

                    vincular_periodo_inicial_associacao(associacao, periodo, recurso)

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
        return Associacao.objects.filter(unidade__codigo_eol=eol).get()
    return None


def get_periodo(referencia):
    if Periodo.objects.filter(referencia=referencia).exists():
        return Periodo.objects.filter(referencia=referencia).get()
    return None


def get_periodo_por_recurso(referencia, recurso):
    return Periodo.objects.filter(referencia=referencia, recurso=recurso).first()


def get_recurso(recurso):
    return Recurso.objects.filter(Q(nome=recurso) | Q(nome_exibicao=recurso)).first()


def vincular_periodo_inicial_associacao(associacao, periodo_inicial, recurso):
    PeriodoInicialAssociacao.objects.update_or_create(
        associacao=associacao,
        periodo_inicial=periodo_inicial,
        recurso=recurso
    )


def carrega_periodo_inicial(arquivo):
    logger.info("Executando Carga de Período inicial para associações.")
    arquivo.ultima_execucao = datetime.datetime.now()

    try:
        with open(arquivo.conteudo.path, 'r', encoding="utf-8") as f:
            sniffer = csv.Sniffer().sniff(f.readline())
            f.seek(0)
            if __DELIMITADORES[sniffer.delimiter] != arquivo.tipo_delimitador:
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
