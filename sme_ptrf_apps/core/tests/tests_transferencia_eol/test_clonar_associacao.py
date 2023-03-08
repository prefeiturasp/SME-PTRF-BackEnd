import pytest

from sme_ptrf_apps.core.models import Associacao

pytestmark = pytest.mark.django_db


def test_clonar_associacao(
    transf_eol_unidade_eol_transferido,  # Eol 400232
    transf_eol_unidade_eol_historico,    # Eol 900232
    transferencia_eol,
    transf_eol_associacao_eol_transferido,  # -> unidade_eol_transferido
):
    assert transf_eol_associacao_eol_transferido.unidade == transf_eol_unidade_eol_transferido

    # Deve clonar associacao da unidade de código transferido para uma nova associação
    associacao_clonada = transferencia_eol.clonar_associacao(transf_eol_unidade_eol_historico)
    assert associacao_clonada.unidade == transf_eol_unidade_eol_transferido, "Deve apontar para a unidade original."
    assert associacao_clonada.uuid is not None
    assert associacao_clonada.uuid != transf_eol_associacao_eol_transferido.uuid
    assert associacao_clonada.nome == transf_eol_associacao_eol_transferido.nome
    assert associacao_clonada.cnpj == transferencia_eol.cnpj_nova_associacao

    associacao_original = Associacao.by_uuid(transf_eol_associacao_eol_transferido.uuid)
    assert associacao_original.unidade == transf_eol_unidade_eol_historico, "Deve apontar para a unidade de histórico."




