import pytest


pytestmark = pytest.mark.django_db


def test_transferencia_eol_codigo_eol_transferido_deve_existir(transferencia_eol):
    # O código EOL transferido deve existir
    possivel, motivo = transferencia_eol.transferencia_possivel()
    assert not possivel
    assert motivo == f'Código EOL transferido {transferencia_eol.eol_transferido} não existe.'


def test_transferencia_eol_codigo_eol_historico_nao_deve_existir(
    transferencia_eol,
    transf_eol_unidade_eol_transferido,
    transf_eol_unidade_eol_historico_ja_existente,
):
    # O código EOL de histórico não deve existir
    possivel, motivo = transferencia_eol.transferencia_possivel()
    assert not possivel
    assert motivo == f'Código EOL de histórico {transferencia_eol.eol_historico} já existe.'

