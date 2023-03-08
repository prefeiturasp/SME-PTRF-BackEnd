import pytest

pytestmark = pytest.mark.django_db


def test_clonar_unidade(
    transf_eol_unidade_eol_transferido,
    transferencia_eol,
    transf_eol_associacao_eol_transferido
):
    # Deve clonar associacao da unidade de código transferido para uma nova associação
    associacao_clonada = transferencia_eol.clonar_associacao()
    assert associacao_clonada.unidade == transf_eol_unidade_eol_transferido
    assert associacao_clonada.uuid is not None
    assert associacao_clonada.uuid != transf_eol_associacao_eol_transferido.uuid
    assert associacao_clonada.nome == transf_eol_associacao_eol_transferido.nome
    assert associacao_clonada.cnpj == transferencia_eol.cnpj_nova_associacao



