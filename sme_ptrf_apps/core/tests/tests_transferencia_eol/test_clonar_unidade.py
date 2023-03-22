import pytest

pytestmark = pytest.mark.django_db


def test_clonar_unidade(
    transf_eol_unidade_eol_transferido,
    transferencia_eol,
):
    # Deve clonar a unidade com o EOL de histórico
    unidade_clonada = transferencia_eol.clonar_unidade()
    assert unidade_clonada.nome == transf_eol_unidade_eol_transferido.nome
    assert unidade_clonada.codigo_eol == transferencia_eol.eol_historico
    assert unidade_clonada.tipo_unidade == transf_eol_unidade_eol_transferido.tipo_unidade
    assert unidade_clonada.uuid is not None
    assert unidade_clonada.uuid != transf_eol_unidade_eol_transferido.uuid

