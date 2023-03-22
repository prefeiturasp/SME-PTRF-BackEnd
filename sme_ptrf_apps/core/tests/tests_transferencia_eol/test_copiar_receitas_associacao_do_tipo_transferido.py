import pytest

pytestmark = pytest.mark.django_db


def test_deve_copiar_as_receitas_da_associacao_origem_que_tenham_o_tipo_de_conta_transferido(
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
    transf_eol_receita_conta_cartao,
    transf_eol_receita_conta_cheque,           # Não deve ser copiada, por ser da conta cheque
):
    transferencia_eol.copiar_receitas_associacao_do_tipo_transferido(transf_eol_associacao_eol_transferido, transf_eol_associacao_nova)

    # Todos as receitas vinculadas à conta_associacao de tipo_conta_transferido da associação original devem ser copiados para a nova associação
    receitas_original = transf_eol_associacao_eol_transferido.receitas.all()
    receitas_nova = transf_eol_associacao_nova.receitas.all()

    assert receitas_nova.count() == 1, "Deve ter copiado apenas as receitas que possuem rateios em contas_associacao de tipo_conta transferido"
    assert receitas_nova.first().detalhe_outros == transf_eol_receita_conta_cartao.detalhe_outros, "Deve ter copiado a receita correta"
    assert receitas_original.count() == 2, "A associação original deve manter as receitas originais"

