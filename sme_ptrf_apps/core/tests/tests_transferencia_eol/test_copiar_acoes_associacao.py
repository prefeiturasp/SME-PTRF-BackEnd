import pytest

pytestmark = pytest.mark.django_db


def test_copiar_acoes_associacao_da_original_para_a_nova(
    transf_eol_unidade_eol_transferido,
    transferencia_eol,
    transf_eol_associacao_eol_transferido,
    transf_eol_acao_associacao_ptrf,
    transf_eol_acao_associacao_role,
    transf_eol_associacao_nova,
    transf_eol_acao_ptrf,
    transf_eol_acao_role,
):
    assert transf_eol_associacao_eol_transferido.acoes.count() == 2
    assert transf_eol_associacao_nova.acoes.count() == 0

    transferencia_eol.copiar_acoes_associacao(transf_eol_associacao_eol_transferido, transf_eol_associacao_nova)

    assert transf_eol_associacao_nova.acoes.count() == 2, "Deve ter a mesma quantidade de ações originais"
    assert transf_eol_associacao_eol_transferido.acoes.count() == 2, "Deve continuar com as ações originais"

    assert any(obj.acao == transf_eol_acao_ptrf for obj in transf_eol_associacao_nova.acoes.all()), "Deve copiar a ação ptrf"
    assert any(obj.acao == transf_eol_acao_role for obj in transf_eol_associacao_nova.acoes.all()), "Deve copiar a ação role"
