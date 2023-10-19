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


def test_transferencia_eol_codigo_eol_historico_nao_deve_existir_fechamentos_associacao_eol_transferido_periodo_inicio_atividades(
    transferencia_eol,
    transf_eol_unidade_eol_transferido,
    transf_eol_periodo_2022_2,
    transf_eol_associacao_eol_transferido,
    transf_eol_fechamento_periodo,
):
    # Não devem existir fechamentos para a associação do eol de tranferência no período da data de início das atividades da nova associação
    possivel, motivo = transferencia_eol.transferencia_possivel()
    assert not possivel
    assert motivo == f'Já existem fechamentos para a associação original {transf_eol_associacao_eol_transferido} no período {transf_eol_periodo_2022_2}.'


def test_transferencia_eol_deve_existir_conta_associacao_tipo_conta_transferido(
    transferencia_eol,
    transf_eol_unidade_eol_transferido,
    transf_eol_periodo_2022_2,
    transf_eol_associacao_eol_transferido,
):
    # Deve existir uma conta_associacao do tipo tipo_conta_transferido para a associação do código eol transferido
    possivel, motivo = transferencia_eol.transferencia_possivel()
    assert not possivel
    assert motivo == f'Não existe conta_associacao do tipo {transferencia_eol.tipo_conta_transferido} para a associação original {transf_eol_associacao_eol_transferido}.'


def test_transferencia_eol_nao_devem_existir_despesas_associacao_original_com_rateios_tipo_conta_transferido_e_outro_tipo_conta(
    transferencia_eol,
    transf_eol_unidade_eol_transferido,
    transf_eol_periodo_2022_2,
    transf_eol_associacao_eol_transferido,
    transf_eol_conta_associacao_cheque,
    transf_eol_conta_associacao_cartao,
    transf_eol_despesa,
    transf_eol_rateio_despesa_conta_cheque,
    transf_eol_rateio_despesa_conta_cartao,
):
    # Nao devem existir despesas da associação original que tenham com rateios no tipo_conta_transferido e em outro tipo de conta
    possivel, motivo = transferencia_eol.transferencia_possivel()
    assert not possivel
    assert motivo == f'A associação original {transf_eol_associacao_eol_transferido} possui despesas com rateios no tipo de conta {transferencia_eol.tipo_conta_transferido} e em outro tipo de conta.'


def test_transferencia_eol_nao_devem_existir_despesas_associacao_original_a_partir_data_inicio_atividades_caso_comportamento_copiar_todas_contas(
    transferencia_eol_copiar_todas_contas,
    transf_eol_unidade_eol_transferido,
    transf_eol_periodo_2022_2,
    transf_eol_associacao_eol_transferido,
    transf_eol_conta_associacao_cheque,
    transf_eol_conta_associacao_cartao,
    transf_eol_despesa,
    transf_eol_rateio_despesa_conta_cheque,
    transf_eol_rateio_despesa_conta_cartao,
):
    # Nao devem existir despesas da associação original que tenham com rateios no tipo_conta_transferido e em outro tipo de conta
    possivel, motivo = transferencia_eol_copiar_todas_contas.transferencia_possivel()
    assert not possivel
    assert motivo == f'A associação original {transf_eol_associacao_eol_transferido} possui despesas com data de transação a partir da data de início das atividades da nova associação {transferencia_eol_copiar_todas_contas.data_inicio_atividades}.'

