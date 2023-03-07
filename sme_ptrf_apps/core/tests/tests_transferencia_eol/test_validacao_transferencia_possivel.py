import pytest


pytestmark = pytest.mark.django_db


def test_transferencia_eol_codigo_eol_transferido_deve_existir(transferencia_eol):
    # O código EOL transferido deve existir
    possivel, motivo = transferencia_eol.transferencia_possivel()
    assert not possivel
    assert motivo == f'Código EOL transferido {transferencia_eol.eol_transferido} não existe.'

