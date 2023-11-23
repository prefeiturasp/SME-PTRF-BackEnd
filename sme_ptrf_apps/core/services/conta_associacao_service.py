from sme_ptrf_apps.core.models import ContaAssociacao

def checa_se_tem_conta_encerrada_com_saldo_no_periodo(associacao, periodo, data):
    tem_conta_encerrada_com_saldo = False
    tipos_das_contas_encerradas_com_saldo = []

    contas = ContaAssociacao.objects.filter(status=ContaAssociacao.STATUS_INATIVA,
                                             associacao=associacao).all()

    for conta in contas:
        if conta.get_saldo_atual_conta(data) != 0 and \
           (conta.periodo_encerramento and conta.periodo_encerramento.referencia == periodo.referencia):
            tem_conta_encerrada_com_saldo = True
            tipos_das_contas_encerradas_com_saldo.append(conta.tipo_conta.nome)

    return tem_conta_encerrada_com_saldo, tipos_das_contas_encerradas_com_saldo
