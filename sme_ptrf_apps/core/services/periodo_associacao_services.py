from ..models import Associacao, Periodo
from ..status_periodo_associacao import (STATUS_PERIODO_ASSOCIACAO_EM_ANDAMENTO, STATUS_PERIODO_ASSOCIACAO_PENDENTE)


def status_periodo_associacao(periodo_uuid, associacao_uuid):
    periodo = Periodo.by_uuid(periodo_uuid)
    #TODO Provavelmente não será mais necessário a Associação. Rever...
    associacao = Associacao.by_uuid(associacao_uuid)

    if periodo.encerrado:
        status = STATUS_PERIODO_ASSOCIACAO_PENDENTE
    else:
        status = STATUS_PERIODO_ASSOCIACAO_EM_ANDAMENTO

    return status


def status_aceita_alteracoes_em_transacoes(status):
    return status in (
        STATUS_PERIODO_ASSOCIACAO_EM_ANDAMENTO,
        STATUS_PERIODO_ASSOCIACAO_PENDENTE,
    )
