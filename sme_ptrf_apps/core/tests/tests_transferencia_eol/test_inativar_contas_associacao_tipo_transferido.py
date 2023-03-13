import pytest

pytestmark = pytest.mark.django_db


def test_deve_inativar_contas_associacao_do_tipo_transferido_na_associacao_original(
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
    transferencia_eol.inativar_contas_associacao_do_tipo_transferido(
        transf_eol_associacao_eol_transferido,
    )

    # A conta_associacao de tipo conta transferido da associação original deve ter sido desativada
    conta_associacao_original_tipo_transferido = transf_eol_associacao_eol_transferido.contas.filter(
        tipo_conta=transferencia_eol.tipo_conta_transferido).first()
    assert conta_associacao_original_tipo_transferido.status == 'INATIVA', "Deve ter desativado a conta_associacao original do tipo_conta_transferido"
