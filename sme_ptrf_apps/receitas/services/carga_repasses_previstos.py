import csv
import datetime
import enum
import logging
from uuid import UUID

from sme_ptrf_apps.core.models import Acao, AcaoAssociacao, Associacao, ContaAssociacao, Periodo, TipoConta
from sme_ptrf_apps.core.models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    ERRO,
    SUCESSO,
    PROCESSADO_COM_ERRO,
)

from ..models import Repasse

__DELIMITADORES = {',': DELIMITADOR_VIRGULA, ';': DELIMITADOR_PONTO_VIRGULA}

logger = logging.getLogger(__name__)


class CargaRepassePrevistoException(Exception):
    pass


class StatusRepasse(enum.Enum):
    PENDENTE = 'Previsto'
    REALIZADO = 'Realizado'


def get_valor(val):
    if not val:
        return 0
    try:
        return float(str(val).replace(',', '.'))
    except ValueError:
        raise ValueError(f"Não foi possível converter '{val}' em um valor númerico.")


def get_associacao(eol):
    try:
        return Associacao.objects.get(unidade__codigo_eol=eol)
    except Associacao.DoesNotExist:
        return None


def get_acao(nome):
    try:
        return Acao.objects.get(nome=nome)
    except Acao.DoesNotExist:
        raise CargaRepassePrevistoException(f"Ação {nome} não encontrada.")


def verifica_tipo_aplicacao(acao, valor_capital, valor_custeio, valor_livre):
    if valor_capital and not acao.aceita_capital:
        raise CargaRepassePrevistoException(f"Ação {acao.nome} não permite capital.")

    if valor_custeio and not acao.aceita_custeio:
        raise CargaRepassePrevistoException(f"Ação {acao.nome} não permite custeio.")

    if valor_livre and not acao.aceita_livre:
        raise CargaRepassePrevistoException(f"Ação {acao.nome} não permite livre aplicação.")


def get_tipo_conta(uuid):
    try:
        return TipoConta.objects.get(uuid=uuid)
    except TipoConta.DoesNotExist:
        raise CargaRepassePrevistoException(f"Tipo de conta de uuid {uuid} não encontrado.")


def get_acao_associacao(acao, associacao):
    try:
        return AcaoAssociacao.objects.get(acao=acao, associacao=associacao)
    except AcaoAssociacao.DoesNotExist:
        logger.info(f"Ação Associação {acao.nome} não encontrada. Registro será criado.")
        return AcaoAssociacao.objects.create(acao=acao, associacao=associacao)


def get_conta_associacao(tipo_conta, associacao, periodo):
    try:
        tipo_conta_obj = TipoConta.objects.get(uuid=tipo_conta) if isinstance(tipo_conta, UUID) else tipo_conta
    except TipoConta.DoesNotExist:
        logger.error(f"TipoConta com id {tipo_conta} não existe.")
        return None

    try:
        conta_associacao = ContaAssociacao.objects.filter(tipo_conta=tipo_conta_obj, associacao=associacao).first()
        if conta_associacao:
            logger.info(f"Encontrou ContaAssociacao: {conta_associacao}")
            return conta_associacao
        else:
            logger.info("Não encontrou ContaAssociacao.")
            if periodo:
                return ContaAssociacao.objects.create(
                    tipo_conta=tipo_conta_obj,
                    associacao=associacao,
                    data_inicio=periodo.data_inicio_realizacao_despesas)
            else:
                return ContaAssociacao.objects.create(tipo_conta=tipo_conta_obj, associacao=associacao)
    except Exception as e:
        logger.error(f"Error resgate ContaAssociacao: {e}")
        return None


def get_datas_periodo(periodo):
    start = periodo.data_inicio_realizacao_despesas
    end = periodo.data_fim_realizacao_despesas

    return (start, end)


def get_periodo(uuid):
    try:
        return Periodo.objects.get(uuid=uuid)
    except Periodo.DoesNotExist:
        raise CargaRepassePrevistoException(f"Periodo de uuid {uuid} não encontrado.")


def get_id_linha(str_id_linha):
    str_id = str_id_linha.strip()
    if not str_id:
        return 0
    try:
        return int(str_id)
    except ValueError:
        raise ValueError(f"Não foi possível converter '{str_id}' em um valor inteiro.")


def associacao_periodo_tem_pc(associacao, periodo):
    return associacao.prestacoes_de_conta_da_associacao.filter(periodo=periodo).exists()


def processa_repasse(reader, tipo_conta_uuid, instance_tipo_conta, arquivo, periodo):
    __ID_LINHA = 0
    __CODIGO_EOL = 1
    __VR_CAPITAL = 2
    __VR_CUSTEIO = 3
    __VR_LIVRE = 4
    __ACAO = 5

    logs = []
    importados = 0

    for index, row in enumerate(reader):
        try:
            if len(row) != 6:
                msg_erro = 'Linha deveria ter seis colunas: id_linha, eol, capital, custeio, livre e ação.'
                raise CargaRepassePrevistoException(msg_erro)

            if index == 0:
                continue  # Cabeçalho

            logger.info('Linha %s: %s', index, row)

            associacao = get_associacao(row[__CODIGO_EOL])
            if not associacao:
                msg_erro = f'Associação com código eol: {row[__CODIGO_EOL]} não encontrado.'
                raise CargaRepassePrevistoException(msg_erro)

            valor_capital = get_valor(row[__VR_CAPITAL])
            valor_custeio = get_valor(row[__VR_CUSTEIO])
            valor_livre = get_valor(row[__VR_LIVRE])

            acao = get_acao(row[__ACAO])

            verifica_tipo_aplicacao(acao, valor_capital, valor_custeio, valor_livre)

            acao_associacao = get_acao_associacao(acao, associacao)
            conta_associacao = get_conta_associacao(tipo_conta_uuid, associacao, periodo)

            if not conta_associacao:
                msg_erro = (
                    f'A associação não possui a conta do tipo {instance_tipo_conta} ativa no período selecionado.')
                raise CargaRepassePrevistoException(msg_erro)

            id_linha = get_id_linha(row[__ID_LINHA])

            repasse_anterior = Repasse.objects.filter(
                carga_origem=arquivo,
                carga_origem_linha_id=id_linha,
            ).first()

            if repasse_anterior and repasse_anterior.valor_realizado:
                msg_erro = (
                    f'O repasse da linha de id {id_linha} já foi importado anteriormente e já teve '
                    'realização. Linha ignorada.')
                raise CargaRepassePrevistoException(msg_erro)

            if repasse_anterior and not repasse_anterior.valor_realizado:
                repasse_anterior.delete()
                logger.info(f'O repasse da linha de id {id_linha} já foi importado anteriormente. Anterior apagado.'
                            f'{id_linha if id_linha else ""}')

            if associacao.encerrada:
                msg_erro = (
                    f'A associação foi encerrada em {associacao.data_de_encerramento.strftime("%d/%m/%Y")}. '
                    f'Linha ID:{index}')
                raise CargaRepassePrevistoException(msg_erro)

            if conta_associacao and conta_associacao.data_inicio:
                start, _ = get_datas_periodo(periodo)

                if start < conta_associacao.data_inicio:
                    msg_erro = "O período informado de repasse é anterior ao período de criação da conta."
                    raise CargaRepassePrevistoException(msg_erro)

                if hasattr(conta_associacao, 'solicitacao_encerramento') \
                    and conta_associacao.solicitacao_encerramento \
                    and conta_associacao.solicitacao_encerramento.aprovada:  # noqa
                    msg_erro = "A conta possui pedido de encerramento aprovado pela DRE."
                    raise CargaRepassePrevistoException(msg_erro)

            if associacao_periodo_tem_pc(associacao, periodo):
                msg_erro = (
                    f"A associação {associacao.unidade.codigo_eol} já possui PC gerada no "
                    f"período {periodo.referencia}.")
                raise CargaRepassePrevistoException(msg_erro)

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
                logger.info(
                    (
                        f"Repasse referente a linha de id {id_linha} criado. Capital={valor_capital} "
                        f"Custeio={valor_custeio} RLA={valor_livre}"))
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

    arquivo.ultima_execucao = datetime.datetime.now()

    try:
        if arquivo.tipo_de_conta:
            tipo_conta = get_tipo_conta(arquivo.tipo_de_conta.uuid)
            logger.info(f"Tipo de conta do arquivo: {tipo_conta}.")
        else:
            msg_erro = "É necessário fornecer um tipo de conta válido."
            raise Exception(msg_erro)

        if arquivo.periodo:
            periodo = get_periodo(arquivo.periodo.uuid)
            logger.info(f"Periodo do arquivo: {periodo}.")
        else:
            msg_erro = "É necessário fornecer um periodo válido."
            raise Exception(msg_erro)

        with open(arquivo.conteudo.path, 'r', encoding="utf-8") as f:
            sniffer = csv.Sniffer().sniff(f.readline())
            f.seek(0)

            if __DELIMITADORES[sniffer.delimiter] != arquivo.tipo_delimitador:
                msg_erro = (
                    f"Formato definido ({arquivo.tipo_delimitador}) é diferente do formato do "
                    f"arquivo csv ({__DELIMITADORES[sniffer.delimiter]})")
                logger.info(msg_erro)
                raise Exception(msg_erro)

            reader = csv.reader(f, delimiter=sniffer.delimiter)
            processa_repasse(reader, arquivo.tipo_de_conta.uuid, tipo_conta, arquivo, periodo)

    except Exception as err:
        msg_erro = f"Erro ao processar repasses previstos: {str(err)}"
        logger.info(msg_erro)
        arquivo.log = msg_erro
        arquivo.status = ERRO
        arquivo.save()
