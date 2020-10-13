from ..models import ProcessoAssociacao

def get_processo_sei_da_prestacao(prestacao_contas):
    return ProcessoAssociacao.by_associacao_periodo(associacao=prestacao_contas.associacao,
                                                    periodo=prestacao_contas.periodo)
