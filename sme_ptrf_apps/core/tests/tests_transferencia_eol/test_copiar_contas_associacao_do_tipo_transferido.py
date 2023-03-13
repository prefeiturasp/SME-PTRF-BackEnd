import pytest

pytestmark = pytest.mark.django_db


def test_deve_copiar_contas_associacao_do_tipo_transferido_da_original_para_a_nova(
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
):
    assert transf_eol_associacao_eol_transferido.contas.count() == 2
    assert transf_eol_associacao_nova.contas.count() == 0

    transferencia_eol.copiar_contas_associacao_do_tipo_transferido(
        transf_eol_associacao_eol_transferido,
        transf_eol_associacao_nova
    )

    # A associação nova deve ter a mesma quantidade de contas do tipo transferido da original
    assert transf_eol_associacao_nova.contas.count() == 1, "Deve ter apenas a conta do tipo_conta_transferido"
    assert transf_eol_associacao_nova.contas.first().tipo_conta == transferencia_eol.tipo_conta_transferido, "Deve ter a conta do tipo_conta_transferido"
    assert transf_eol_associacao_eol_transferido.contas.count() == 2, "Deve continuar com as contas originais"
