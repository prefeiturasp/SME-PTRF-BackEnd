import csv
import datetime
import enum
import logging
import os

from sme_ptrf_apps.core.models import Acao, AcaoAssociacao, Associacao, ContaAssociacao, Periodo, TipoConta
from sme_ptrf_apps.core.models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    ERRO,
    PROCESSADO_COM_ERRO,
    SUCESSO,
)

from ..models import Repasse

__DELIMITADORES = {',': DELIMITADOR_VIRGULA, ';': DELIMITADOR_PONTO_VIRGULA}

logger = logging.getLogger(__name__)


class CargaRepassePrevistoException(Exception):
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
    try:
        return float(str(val).replace(',', '.'))
    except ValueError:
        raise ValueError(f"Não foi possível converter '{val}' em um valor númerico.")


def get_associacao(eol):
    if Associacao.objects.filter(unidade__codigo_eol=eol).exists():
        return Associacao.objects.filter(unidade__codigo_eol=eol).get()

    return None


def get_acao(nome):
    if Acao.objects.filter(nome=nome).exists():
        return Acao.objects.filter(nome=nome).get()
    else:
        raise CargaRepassePrevistoException(f"Ação {nome} não encontrada.")


def get_tipo_conta(nome):
    if TipoConta.objects.filter(nome=nome).exists():
        return TipoConta.objects.filter(nome=nome).get()
    else:
        raise CargaRepassePrevistoException(f"Tipo de conta {nome} não encontrado.")


def get_acao_associacao(acao, associacao):
    if AcaoAssociacao.objects.filter(acao=acao, associacao=associacao).exists():
        return AcaoAssociacao.objects.filter(acao=acao, associacao=associacao).get()

    logger.info(f"Ação Associação {acao.nome} não encontrada. Registro será criado.")
    return AcaoAssociacao.objects.create(acao=acao, associacao=associacao)


def get_conta_associacao(tipo_conta, associacao):
    if ContaAssociacao.objects.filter(tipo_conta=tipo_conta, associacao=associacao).exists():
        return ContaAssociacao.objects.filter(tipo_conta=tipo_conta, associacao=associacao).get()

    logger.info(f"Conta Associação {tipo_conta.nome} não encontrada. Registro será criado.")
    return ContaAssociacao.objects.create(tipo_conta=tipo_conta, associacao=associacao)


def get_datas_periodo(nome_arquivo):
    base_name = os.path.basename(nome_arquivo)
    start_str_date, end_str_date = base_name[:10], base_name[13:23]
    start = datetime.datetime.strptime(start_str_date, '%Y_%m_%d')
    end = datetime.datetime.strptime(end_str_date, '%Y_%m_%d')

    return (start, end)


def get_periodo(nome_arquivo):
    start, end = get_datas_periodo(nome_arquivo)

    if Periodo.objects.filter(data_inicio_realizacao_despesas=start, data_fim_realizacao_despesas=end).exists():
        return Periodo.objects.filter(data_inicio_realizacao_despesas=start, data_fim_realizacao_despesas=end).get()

    logger.info(f"Período {start}-{end} não encontrado. Registro será criado.")
    return Periodo.objects.create(
        data_inicio_realizacao_despesas=start,
        data_fim_realizacao_despesas=end,
        referencia=f'{start.year}'
    )


def get_id_linha(str_id_linha):
    str_id = str_id_linha.strip()
    if not str_id:
        return 0
    try:
        return int(str_id)
    except ValueError:
        raise ValueError(f"Não foi possível converter '{str_id}' em um valor inteiro.")


def processa_repasse(reader, tipo_conta, arquivo):
    __ID_LINHA = 0
    __CODIGO_EOL = 1
    __VR_CAPITAL = 2
    __VR_CUSTEIO = 3
    __VR_LIVRE = 4
    __ACAO = 5

    nome_arquivo = arquivo.identificador

    periodo = get_periodo(nome_arquivo)

    logs = []
    importados = 0

    for index, row in enumerate(reader):
        try:
            if len(row) != 6:
                msg_erro = f'Linha deveria ter seis colunas: id_linha, eol, capital, custeio, livre e ação.'
                raise Exception(msg_erro)

            if index != 0:
                logger.info('Linha %s: %s', index, row)

                associacao = get_associacao(row[__CODIGO_EOL])
                if not associacao:
                    msg_erro = f'Associação com código eol: {row[__CODIGO_EOL]} não encontrado.'
                    raise Exception(msg_erro)

                valor_capital = get_valor(row[__VR_CAPITAL])
                valor_custeio = get_valor(row[__VR_CUSTEIO])
                valor_livre = get_valor(row[__VR_LIVRE])

                acao = get_acao(row[__ACAO])

                acao_associacao = get_acao_associacao(acao, associacao)
                conta_associacao = get_conta_associacao(tipo_conta, associacao)

                id_linha = get_id_linha(row[__ID_LINHA])

                repasse_anterior = Repasse.objects.filter(
                    carga_origem=arquivo,
                    carga_origem_linha_id=id_linha,
                ).first()

                if repasse_anterior and repasse_anterior.valor_realizado:
                    msg_erro = f'O repasse da linha de id {id_linha} já foi importado anteriormente e já teve realização. Linha ignorada.'
                    raise Exception(msg_erro)

                if repasse_anterior and not repasse_anterior.valor_realizado:
                    repasse_anterior.delete()
                    logger.info(f'O repasse da linha de id {id_linha} já foi importado anteriormente. Anterior apagado.'
                                f'{id_linha if id_linha else ""}')

                if valor_capital > 0 or valor_custeio > 0 or valor_livre > 0:
                    Repasse.objects.create(
                        associacao=associacao,
                        valor_capital=valor_capital,
                        valor_custeio=valor_custeio,
                        valor_livre=valor_livre,
                        conta_associacao=conta_associacao,
                        acao_associacao=acao_associacao,
                        periodo=periodo,
                        status=StatusRepasse.PENDENTE.name,
                        carga_origem=arquivo,
                        carga_origem_linha_id=id_linha,
                    )
                    logger.info(f"Repasse referente a linha de id {id_linha} criado. Capital={valor_capital} Custeio={valor_custeio} RLA={valor_livre}")
                    importados += 1
                else:
                    logger.info(f"A linha de id {id_linha} está sem valores. Nenhum repasse criado.")

        except Exception as e:
            msg_erro = f"Erro na linha {index}: {str(e)}"
            logs.append(msg_erro)
            logger.info(msg_erro)

    if importados > 0 and len(logs) > 0:
        arquivo.status = PROCESSADO_COM_ERRO
    elif importados == 0:
        arquivo.status = ERRO
    else:
        arquivo.status = SUCESSO

    msg = f"Foram criados {importados} repasses. Erro na importação de {len(logs)} repasse(s)."
    logs.append(msg)
    logger.info(msg)

    arquivo.log = "\n".join(logs)
    arquivo.save()


def carrega_repasses_previstos(arquivo):
    logger.info("Processando arquivo %s", arquivo.identificador)
    tipo_conta_nome = TipoContaEnum.CARTAO.value if 'cartao' in arquivo.identificador else TipoContaEnum.CHEQUE.value

    arquivo.ultima_execucao = datetime.datetime.now()

    try:
        tipo_conta = get_tipo_conta(tipo_conta_nome)
        logger.info(f"Tipo de conta do arquivo: {tipo_conta}.")

        with open(arquivo.conteudo.path, 'r', encoding="utf-8") as f:
            sniffer = csv.Sniffer().sniff(f.readline())
            f.seek(0)

            if __DELIMITADORES[sniffer.delimiter] != arquivo.tipo_delimitador:
                msg_erro = f"Formato definido ({arquivo.tipo_delimitador}) é diferente do formato do arquivo csv ({__DELIMITADORES[sniffer.delimiter]})"
                logger.info(msg_erro)
                raise Exception(msg_erro)

            reader = csv.reader(f, delimiter=sniffer.delimiter)
            processa_repasse(reader, tipo_conta, arquivo)

    except Exception as err:
        msg_erro = f"Erro ao processar repasses previstos: {str(err)}"
        logger.info(msg_erro)
        arquivo.log = msg_erro
        arquivo.status = ERRO
        arquivo.save()
