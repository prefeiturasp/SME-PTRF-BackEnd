from ..models import Associacao, Periodo
from ..status_periodo_associacao import (STATUS_PERIODO_ASSOCIACAO_EM_ANDAMENTO, STATUS_PERIODO_ASSOCIACAO_PENDENTE)


def status_periodo_associacao(periodo_uuid, associacao_uuid):
    periodo = Periodo.by_uuid(periodo_uuid)
    #TODO Rever o calculo do Status do Período
    associacao = Associacao.by_uuid(associacao_uuid)

    if periodo.encerrado:
        status = STATUS_PERIODO_ASSOCIACAO_PENDENTE
    else:
        status = STATUS_PERIODO_ASSOCIACAO_EM_ANDAMENTO

    return status


def status_aceita_alteracoes_em_transacoes(status):
    # TODO Rever o calculo do Status Aceitação de edição de transações
    return status in (
        STATUS_PERIODO_ASSOCIACAO_EM_ANDAMENTO,
        STATUS_PERIODO_ASSOCIACAO_PENDENTE,
    )
