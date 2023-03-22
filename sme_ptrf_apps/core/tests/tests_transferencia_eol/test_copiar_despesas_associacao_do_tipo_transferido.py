import pytest

pytestmark = pytest.mark.django_db


def test_deve_copiar_as_despesas_e_reateios_da_associacao_origem_que_tenham_o_tipo_de_conta_transferido(
    transf_eol_unidade_eol_transferido,
    transferencia_eol,
    transf_eol_associacao_eol_transferido,
    transf_eol_acao_associacao_ptrf,
    transf_eol_acao_associacao_role,
    transf_eol_associacao_nova,
    transf_eol_acao_ptrf,
    transf_eol_acao_role,
    transf_eol_conta_associacao_cheque,
    transf_eol_conta_associacao_cartao,
    transf_eol_despesa,
    transf_eol_rateio_despesa_conta_cartao,
    transf_eol_rateio_despesa_conta_cartao_rateio_2,
    transf_eol_despesa_2_conta_cheque,  # Não deve ser copiada, por ter rateios da conta cheque
    transf_eol_rateio_despesa_2_conta_cheque  # Não deve ser copiada, por ser da conta cheque
):
    transferencia_eol.copiar_despesas_associacao_do_tipo_transferido(transf_eol_associacao_eol_transferido, transf_eol_associacao_nova)

    # Todos os gastos e rateios vinculados à conta_associacao de tipo_conta_transferido da associação original devem ser copiados para a nova associação
    despesas_original = transf_eol_associacao_eol_transferido.despesas.all()
    despesas_nova = transf_eol_associacao_nova.despesas.all()

    assert despesas_nova.count() == 1, "Deve ter copiado apenas as despesas que possuem rateios em contas_associacao de tipo_conta transferido"
    assert despesas_nova.first().numero_documento == transf_eol_despesa.numero_documento, "Deve ter copiado a despesa correta"
    assert despesas_nova.first().rateios.count() == 2, "Deve ter copiado os rateios corretos"
    assert despesas_original.count() == 2, "A associação original deve manter as despesas originais"

