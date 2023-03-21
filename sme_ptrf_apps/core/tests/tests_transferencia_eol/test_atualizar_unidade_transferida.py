import pytest

pytestmark = pytest.mark.django_db


def test_atualizar_unidade_transferida(
    transf_eol_unidade_eol_transferido,
    transferencia_eol,
):
    # Deve atualizar a unidade de código transferido para o tipo_nova_unidade
    unidade_atualizada = transferencia_eol.atualizar_unidade_transferida()
    assert unidade_atualizada.tipo_unidade == transferencia_eol.tipo_nova_unidade

