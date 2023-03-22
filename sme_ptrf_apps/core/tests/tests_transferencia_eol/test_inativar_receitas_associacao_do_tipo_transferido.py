import pytest

from sme_ptrf_apps.despesas.models import Despesa

pytestmark = pytest.mark.django_db


def test_deve_inativar_as_receitas_da_associacao_origem_que_tenham_o_tipo_de_conta_transferido(
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
    transferencia_eol.inativar_receitas_associacao_do_tipo_transferido(transf_eol_associacao_eol_transferido)

    # Todas as receitas vinculadas à conta_associacao de tipo_conta_transferido da associação original devem ser inativadas
    receitas_original = transf_eol_associacao_eol_transferido.receitas.all()
    receitas_nova = transf_eol_associacao_nova.receitas.all()
    assert receitas_original.filter(status='INATIVO').count() == receitas_original.filter(conta_associacao__tipo_conta=transferencia_eol.tipo_conta_transferido).distinct().count(), "Deve ter inativado todas as receitas originais"
    assert receitas_nova.filter(status='INATIVO').count() == 0, "A associação nova não deve ter receitas inativas"



