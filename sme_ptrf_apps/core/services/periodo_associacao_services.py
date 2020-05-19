from ..models import Associacao, Periodo, PrestacaoConta
from ..status_periodo_associacao import (STATUS_PERIODO_ASSOCIACAO_EM_ANDAMENTO, STATUS_PERIODO_ASSOCIACAO_PENDENTE,
                                         STATUS_PERIODO_ASSOCIACAO_CONCILIADO)


def status_periodo_associacao(periodo_uuid, associacao_uuid):
    periodo = Periodo.by_uuid(periodo_uuid)
    associacao = Associacao.by_uuid(associacao_uuid)

    if periodo.encerrado:
        status = STATUS_PERIODO_ASSOCIACAO_PENDENTE
    else:
        status = STATUS_PERIODO_ASSOCIACAO_EM_ANDAMENTO

    prestacoes_de_conta = PrestacaoConta.objects.filter(associacao=associacao, periodo=periodo)
    if prestacoes_de_conta.exists() and not prestacoes_de_conta.filter(conciliado=False).exists():
        status = STATUS_PERIODO_ASSOCIACAO_CONCILIADO

    return status
