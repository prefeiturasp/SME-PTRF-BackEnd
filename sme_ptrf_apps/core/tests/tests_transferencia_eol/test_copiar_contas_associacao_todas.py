import pytest

pytestmark = pytest.mark.django_db


def test_deve_copiar_todas_contas_associacao_quando_comportamento_contas_for_esse(
    transferencia_eol_copiar_todas_contas,
    transf_eol_unidade_eol_transferido,
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

    transferencia_eol_copiar_todas_contas.copiar_contas_associacao(
        transf_eol_associacao_eol_transferido,
        transf_eol_associacao_nova
    )

    # A associação nova deve ter a mesma quantidade de contas da original
    assert transf_eol_associacao_nova.contas.count() == 2, "Deve ter a mesma quantidade de contas da associação original"
    assert transf_eol_associacao_eol_transferido.contas.count() == 2, "Deve continuar com as contas originais"

