import csv
import datetime
import enum
import logging
from datetime import datetime

from sme_ptrf_apps.core.models import Acao, AcaoAssociacao, Associacao, ContaAssociacao, Periodo, TipoConta
from sme_ptrf_apps.core.models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    ERRO,
    PROCESSADO_COM_ERRO,
    SUCESSO,
)
from sme_ptrf_apps.core.services.periodo_services import periodo_aceita_alteracoes_na_associacao
from ..models import Receita, Repasse, TipoReceita
from ..tipos_aplicacao_recurso_receitas import APLICACAO_CAPITAL, APLICACAO_CUSTEIO, APLICACAO_LIVRE


logger = logging.getLogger(__name__)

ID_LINHA = 0
CODIGO_EOL = 1
VALOR_CAPITAL = 2
VALOR_CUSTEIO = 3
VALOR_LIVRE = 4
ACAO = 5
DATA = 6
PERIODO = 7
__DELIMITADORES = {',': DELIMITADOR_VIRGULA, ';': DELIMITADOR_PONTO_VIRGULA}


class CargaRepasseRealizadoException(Exception):
    pass


class TipoContaEnum(enum.Enum):
    CARTAO = 'Cartão'
    CHEQUE = 'Cheque'


class StatusRepasse(enum.Enum):
    PENDENTE = 'Pendente'
    REALIZADO = 'Realizado'


def get_valor(val):
    if not val:
        return 0

    return float(str(val).replace(',', '.'))


def get_associacao(eol):
    if Associacao.objects.filter(unidade__codigo_eol=eol).exists():
        return Associacao.objects.filter(unidade__codigo_eol=eol).get()

    return None


def get_acao(nome):
    if Acao.objects.filter(nome=nome).exists():
        return Acao.objects.filter(nome=nome).get()
    else:
        raise CargaRepasseRealizadoException(f"Ação {nome} não encontrada.")


def verifica_tipo_aplicacao(nome, valor_capital, valor_custeio, valor_livre):
    if valor_capital:
        if Acao.objects.filter(nome=nome).filter(aceita_capital=False):
            raise CargaRepasseRealizadoException(f"Ação {nome} não permite capital.")

    if valor_custeio:
        if Acao.objects.filter(nome=nome).filter(aceita_custeio=False):
            raise CargaRepasseRealizadoException(f"Ação {nome} não permite custeio.")

    if valor_livre:
        if Acao.objects.filter(nome=nome).filter(aceita_livre=False):
            raise CargaRepasseRealizadoException(f"Ação {nome} não permite livre aplicação.")


def get_tipo_conta(nome):
    if TipoConta.objects.filter(nome=nome).exists():
        return TipoConta.objects.filter(nome=nome).get()
    else:
        raise CargaRepasseRealizadoException(f"Tipo de conta {nome} não encontrado.")


def get_acao_associacao(acao, associacao):
    if AcaoAssociacao.objects.filter(acao=acao, associacao=associacao).exists():
        return AcaoAssociacao.objects.filter(acao=acao, associacao=associacao).get()

    return AcaoAssociacao.objects.create(acao=acao, associacao=associacao)


def get_conta_associacao(tipo_conta, associacao):
    if ContaAssociacao.objects.filter(tipo_conta=tipo_conta, associacao=associacao).exists():
        return ContaAssociacao.objects.filter(tipo_conta=tipo_conta, associacao=associacao).get()

    return ContaAssociacao.objects.create(tipo_conta=tipo_conta, associacao=associacao)


def get_periodo(referencia):
    try:
        periodo = Periodo.objects.filter(referencia=referencia).get()
        return periodo
    except Periodo.DoesNotExist:
        raise Exception("Período não existe")


def criar_receita(associacao, conta_associacao, acao_associacao, valor, data, categoria_receita, tipo_receita, repasse):
    Receita.objects.create(
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        valor=valor,
        data=data,
        tipo_receita=tipo_receita,
        conferido=True,
        categoria_receita=categoria_receita,
        repasse=repasse
    )
    logger.info(f"Crianda receita realização do repasse. Linha_ID:{repasse.carga_origem_linha_id}")


def get_id_linha(str_id_linha):
    str_id = str_id_linha.strip()
    if not str_id:
        return 0
    try:
        return int(str_id)
    except ValueError:
        raise ValueError(f"Não foi possível converter '{str_id}' em um valor inteiro.")


def processa_repasse(reader, tipo_conta, arquivo):
    logs = ""
    importados = 0
    erros = 0
    for index, row in enumerate(reader):
        if index == 0:
            continue

        logger.info('Linha %s: %s', index, row)

        try:
            if len(row) != 8:
                msg_erro = f'Linha deveria ter seis colunas: id_linha, eol, capital, custeio, livre, ação, data e período.'
                raise Exception(msg_erro)

            id_linha = get_id_linha(row[ID_LINHA])

            associacao = get_associacao(row[CODIGO_EOL])
            if not associacao:
                msg_erro = f'Associação com código eol: {row[CODIGO_EOL]} não encontrado. Linha ID:{id_linha}'
                raise Exception(msg_erro)

            periodo = get_periodo(str(row[PERIODO]).strip())

            if not periodo_aceita_alteracoes_na_associacao(periodo, associacao):
                msg_erro = f'Período {periodo.referencia} fechado para alterações na associação. Linha ID:{id_linha}'
                raise Exception(msg_erro)

            valor_capital = get_valor(row[VALOR_CAPITAL])
            valor_custeio = get_valor(row[VALOR_CUSTEIO])
            valor_livre = get_valor(row[VALOR_LIVRE])

            acao = get_acao(str(row[ACAO]).strip(" "))

            verifica_tipo_aplicacao(str(row[ACAO]).strip(" "), valor_capital, valor_custeio, valor_livre)

            acao_associacao = get_acao_associacao(acao, associacao)
            conta_associacao = get_conta_associacao(tipo_conta, associacao)


            repasse_anterior = Repasse.objects.filter(
                carga_origem=arquivo,
                carga_origem_linha_id=id_linha,
            ).first()

            if repasse_anterior:
                for receita in repasse_anterior.receitas.all():
                    receita.delete()
                repasse_anterior.delete()
                logger.info(f'O repasse da linha de id {id_linha} já foi importado anteriormente. Anterior e suas receitas apagados.'
                            f'{id_linha if id_linha else ""}')

            if valor_capital > 0 or valor_custeio > 0 or valor_livre > 0:
                repasse = Repasse.objects.create(
                    associacao=associacao,
                    valor_capital=valor_capital,
                    valor_custeio=valor_custeio,
                    valor_livre=valor_livre,
                    conta_associacao=conta_associacao,
                    acao_associacao=acao_associacao,
                    periodo=periodo,
                    status=StatusRepasse.REALIZADO.name,
                    carga_origem=arquivo,
                    carga_origem_linha_id=id_linha,
                )
                logger.info(f"Repasse referente a linha de id {id_linha} criado. Capital={valor_capital} Custeio={valor_custeio} RLA={valor_livre}")

                data = datetime.strptime(str(row[DATA]).strip(" "), '%d/%m/%Y')
                tipo_receita = TipoReceita.objects.filter(e_repasse=True).first()
                valor = 0
                categoria_receita = None

                if valor_capital > 0:
                    valor = valor_capital
                    categoria_receita = APLICACAO_CAPITAL

                    criar_receita(
                        associacao,
                        conta_associacao,
                        acao_associacao,
                        valor,
                        data,
                        categoria_receita,
                        tipo_receita,
                        repasse)

                    repasse.realizado_capital = True

                if valor_custeio > 0:
                    valor = valor_custeio
                    categoria_receita = APLICACAO_CUSTEIO

                    criar_receita(
                        associacao,
                        conta_associacao,
                        acao_associacao,
                        valor,
                        data,
                        categoria_receita,
                        tipo_receita,
                        repasse)

                    repasse.realizado_custeio = True

                if valor_livre > 0:
                    valor = valor_livre
                    categoria_receita = APLICACAO_LIVRE

                    criar_receita(
                        associacao,
                        conta_associacao,
                        acao_associacao,
                        valor,
                        data,
                        categoria_receita,
                        tipo_receita,
                        repasse)

                    repasse.realizado_livre = True

                repasse.save()
                importados += 1
            else:
                logger.info(f"A linha de id {id_linha} está sem valores. Nenhum repasse criado.")

        except Exception as e:
            msg = f"Erro na linha {index}: {str(e)}"
            logger.info(msg)

            logs = f'{logs}\n{msg}'
            erros += 1

    if importados > 0 and erros > 0:
        arquivo.status = PROCESSADO_COM_ERRO
    elif erros > 0:
        arquivo.status = ERRO
    else:
        arquivo.status = SUCESSO

    logs = f"{logs}\nForam criados {importados} repasses. Erro na importação de {erros} repasses."
    logger.info(f'Foram criados {importados} repasses. Erro na importação de {erros} repasses.')

    arquivo.log = logs
    arquivo.save()


def carrega_repasses_realizados(arquivo):
    logger.info("Processando arquivo %s", arquivo.identificador)
    tipo_conta_nome = TipoContaEnum.CARTAO.value if 'cartao' in arquivo.identificador else TipoContaEnum.CHEQUE.value
    arquivo.ultima_execucao = datetime.now()

    try:
        tipo_conta = get_tipo_conta(tipo_conta_nome)

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
            processa_repasse(reader, tipo_conta, arquivo)

    except Exception as err:
        msg = f"Erro ao processar repasses realizados: {err}"
        logger.info(msg)
        arquivo.log = msg
        arquivo.status = ERRO
        arquivo.save()
