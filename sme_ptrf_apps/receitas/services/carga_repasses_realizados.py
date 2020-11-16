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

from ..models import Receita, Repasse, TipoReceita
from ..tipos_aplicacao_recurso_receitas import APLICACAO_CAPITAL, APLICACAO_CUSTEIO, APLICACAO_LIVRE

logger = logging.getLogger(__name__)

CODIGO_EOL = 0
VALOR_CAPITAL = 1
VALOR_CUSTEIO = 2
VALOR_LIVRE = 3
ACAO = 4
DATA = 5
PERIODO = 6
__DELIMITADORES = {',': DELIMITADOR_VIRGULA, ';': DELIMITADOR_PONTO_VIRGULA}


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


def processa_repasse(reader, conta, arquivo):
    logs = ""
    importados = 0
    erros = 0
    for index, row in enumerate(reader):
        if index != 0:
            logger.info('Linha %s: %s', index, row)
            associacao = get_associacao(row[CODIGO_EOL])
            if not associacao:
                msg_erro = f'Associação com código eol: {row[CODIGO_EOL]} não encontrado. Linha {index}'
                logger.info(msg_erro)
                logs = f"{logs}\n{msg_erro}"
                erros += 1
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
                    importados += 1    
            except Exception as e:
                logger.info("Error %s", str(e))
                arquivo.log = f'{logs}\nError: {str(e)}'
                arquivo.status = ERRO
                erros += 1
                arquivo.save()

    if importados > 0 and erros > 0:
        arquivo.status = PROCESSADO_COM_ERRO
    elif importados == 0:
        arquivo.status = ERRO
    else:
        arquivo.status = SUCESSO
    
    logs = f"{logs}\nForam criados {importados} repasses. Erro na importação de {erros} repasses."
    logger.info(f'Foram criados {importados} repasses. Erro na importação de {erros} repasses.')
    
    arquivo.log = logs
    arquivo.save()


def carrega_repasses_realizados(arquivo):
    logger.info("Processando arquivo %s", arquivo.identificador)
    tipo_conta = TipoContaEnum.CARTAO.value if 'cartao' in arquivo.identificador else TipoContaEnum.CHEQUE.value
    arquivo.ultima_execucao = datetime.now()

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
            processa_repasse(reader, tipo_conta, arquivo)
    except Exception as err:
        logger.info("Erro ao processar repasses realizados: %s", str(err))
        arquivo.log = "Erro ao processar repasses realizados."
        arquivo.save()
