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


def test_transferencia_eol_codigo_eol_historico_deve_existir_periodo_para_data_inicio_atividade(
    transferencia_eol,
    transf_eol_unidade_eol_transferido,
):
    # Deve existir um período para a data de início das atividades
    possivel, motivo = transferencia_eol.transferencia_possivel()
    assert not possivel
    assert motivo == f'Não existe período para a data de início das atividades {transferencia_eol.data_inicio_atividades}.'


def test_transferencia_eol_codigo_eol_historico_deve_existir_associacao_eol_transferido(
    transferencia_eol,
    transf_eol_unidade_eol_transferido,
    transf_eol_periodo_2022_2,
):
    # Deve existir uma associação para o código EOL transferido
    possivel, motivo = transferencia_eol.transferencia_possivel()
    assert not possivel
    assert motivo == f'Não existe associação para o código EOL transferido {transferencia_eol.eol_transferido}.'
