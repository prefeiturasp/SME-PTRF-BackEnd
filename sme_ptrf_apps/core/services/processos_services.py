from ..models import ProcessoAssociacao


def get_processo_sei_da_prestacao(prestacao_contas):
    return ProcessoAssociacao.by_associacao_periodo(associacao=prestacao_contas.associacao,
                                                    periodo=prestacao_contas.periodo)


def get_processo_sei_da_associacao_no_periodo(associacao, periodo):
    return ProcessoAssociacao.by_associacao_periodo(associacao=associacao,
                                                    periodo=periodo)
    
def trata_processo_sei_ao_receber_pc(prestacao_conta, processo_sei, acao_processo_sei):
    ano = prestacao_conta.periodo.referencia[0:4]
    if acao_processo_sei == 'editar':
        processo_associacao = ProcessoAssociacao.ultimo_processo_do_ano_por_associacao(associacao=prestacao_conta.associacao, ano=ano)
        processo_associacao.numero_processo = processo_sei
        processo_associacao.save()
    elif acao_processo_sei == 'incluir':
        ProcessoAssociacao.objects.create(associacao=prestacao_conta.associacao, ano=ano, numero_processo=processo_sei)

    
