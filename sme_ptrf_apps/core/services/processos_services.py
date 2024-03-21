from ..models import ProcessoAssociacao


def get_processo_sei_da_prestacao(prestacao_contas, periodos_processo_sei=False):
    """Retorna o número do processo SEI vinculado a uma prestação de contas.
    Se a feature flag periodos-processo-sei estiver ativa usa versão v2 do método."""
    if periodos_processo_sei:
        return ProcessoAssociacao.by_associacao_periodo_v2(associacao=prestacao_contas.associacao,
                                                           periodo=prestacao_contas.periodo)
    else:
        return ProcessoAssociacao.by_associacao_periodo(associacao=prestacao_contas.associacao,
                                                        periodo=prestacao_contas.periodo)


def get_processo_sei_da_associacao_no_periodo(associacao, periodo, periodos_processo_sei=False):
    """Retorna o número do processo SEI vinculado a uma associação e um período.
    Se a feature flag periodos-processo-sei estiver ativa usa versão v2 do método."""
    if periodos_processo_sei:
        return ProcessoAssociacao.by_associacao_periodo_v2(associacao=associacao,
                                                           periodo=periodo)
    else:
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


