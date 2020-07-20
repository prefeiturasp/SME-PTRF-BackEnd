import csv
import datetime
import enum

import logging

from datetime import datetime

from sme_ptrf_apps.core.models import Acao, AcaoAssociacao, Associacao, ContaAssociacao, Periodo, TipoConta
from ..tipos_aplicacao_recurso_receitas import APLICACAO_CAPITAL, APLICACAO_CUSTEIO, APLICACAO_LIVRE

from ..models import Receita, Repasse, TipoReceita

logger = logging.getLogger(__name__)

CODIGO_EOL = 0
VALOR_CAPITAL = 1
VALOR_CUSTEIO = 2
VALOR_LIVRE = 3
ACAO = 4
DATA = 5
PERIODO = 6


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

    return Acao.objects.create(nome=nome)


def get_tipo_conta(nome):
    if TipoConta.objects.filter(nome=nome).exists():
        return TipoConta.objects.filter(nome=nome).get()

    return TipoConta.objects.create(nome=nome)


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
    logger.info("Criando receita.")
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


def processa_repasse(reader, conta):
    for index, row in enumerate(reader):
        if index != 0:
            logger.info('Linha %s: %s', index, row)
            associacao = get_associacao(row[CODIGO_EOL])
            if not associacao:
                logger.info('Associação com código eol: %s não encontrado.', row[CODIGO_EOL])
                continue
            try:
                periodo = get_periodo(str(row[PERIODO]).strip())
                valor_capital = get_valor(row[VALOR_CAPITAL])
                valor_custeio = get_valor(row[VALOR_CUSTEIO])
                valor_livre = get_valor(row[VALOR_LIVRE])
                acao = get_acao(str(row[ACAO]).strip(" "))
                tipo_conta = get_tipo_conta(conta)
                acao_associacao = get_acao_associacao(acao, associacao)
                conta_associacao = get_conta_associacao(tipo_conta, associacao)

                if valor_capital > 0 or valor_custeio > 0 or valor_livre > 0:
                    logger.info("Criando repasse.")
                    repasse = Repasse.objects.create(
                        associacao=associacao,
                        valor_capital=valor_capital,
                        valor_custeio=valor_custeio,
                        valor_livre=valor_livre,
                        conta_associacao=conta_associacao,
                        acao_associacao=acao_associacao,
                        periodo=periodo,
                        status=StatusRepasse.REALIZADO.name
                    )

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
            except Exception as e:
                logger.info("Error %s", str(e))


def carrega_repasses_realizados(arquivo):
    logger.info("Processando arquivo %s", arquivo.identificador)
    tipo_conta = TipoContaEnum.CARTAO.value if 'cartao' in arquivo.identificador else TipoContaEnum.CHEQUE.value

    with open(arquivo.conteudo.path, 'r', encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=',')
        processa_repasse(reader, tipo_conta)
