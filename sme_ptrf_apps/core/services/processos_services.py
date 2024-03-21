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


def trata_processo_sei_ao_receber_pc_v2(prestacao_conta, processo_sei, acao_processo_sei):
    """
    Trata o número do processo SEI ao receber uma prestação de contas.
    Versão 2 do método, chamada se feature flag periodos-processo-sei estiver ativa.
    """

    if acao_processo_sei == 'incluir':
        # Verifica se já existe um processo associado a associação com o número do processo SEI informado.
        processo_associacao = ProcessoAssociacao.objects.filter(associacao=prestacao_conta.associacao,
                                                                numero_processo=processo_sei).first()
        if processo_associacao:
            # O processo já existe então basta adicionar o período a ele.
            if prestacao_conta.periodo in processo_associacao.periodos.all():
                # O período não deveria estar vinculado ao processo.
                raise Exception(f"O período {prestacao_conta.periodo.referencia} já está vinculado ao processo {processo_sei}.")
            processo_associacao.periodos.add(prestacao_conta.periodo)
        else:
            # O processo não existe então é criado um novo.
            # Porém é necessário verificar se o período já está vinculado a outro processo.
            processo_associacao = ProcessoAssociacao.objects.filter(associacao=prestacao_conta.associacao,
                                                                    periodos=prestacao_conta.periodo).first()
            if processo_associacao:
                raise Exception(f"O período {prestacao_conta.periodo.referencia} já está vinculado ao processo {processo_associacao.numero_processo}.")

            processo_associacao = ProcessoAssociacao.objects.create(
                associacao=prestacao_conta.associacao,
                numero_processo=processo_sei,
                ano=prestacao_conta.periodo.referencia[0:4]
            )
            processo_associacao.periodos.add(prestacao_conta.periodo)

        return

    if acao_processo_sei == 'editar':
        processo_associacao = ProcessoAssociacao.objects.filter(associacao=prestacao_conta.associacao,
                                                                periodos=prestacao_conta.periodo).first()

        processo_associacao.numero_processo = processo_sei
        processo_associacao.save()

