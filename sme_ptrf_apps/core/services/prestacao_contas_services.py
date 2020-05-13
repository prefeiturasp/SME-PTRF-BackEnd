from ..models import PrestacaoConta, ContaAssociacao, Periodo


def iniciar_prestacao_de_contas(conta_associacao_uuid, periodo_uuid):
    conta_associacao = ContaAssociacao.objects.get(uuid=conta_associacao_uuid)
    periodo = Periodo.objects.get(uuid=periodo_uuid)

    return PrestacaoConta.iniciar(conta_associacao=conta_associacao, periodo=periodo)

def concluir_prestacao_de_contas(prestacao_contas_uuid, observacoes):
    return PrestacaoConta.concluir(uuid=prestacao_contas_uuid, observacoes=observacoes)

def salvar_prestacao_de_contas(prestacao_contas_uuid):
    ...
