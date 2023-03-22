import pytest

from sme_ptrf_apps.core.models import Unidade, Associacao

pytestmark = pytest.mark.django_db


def test_integracao_transferencia_eol(
    transf_eol_periodo_2022_2,
    transf_eol_unidade_eol_transferido,
    transf_eol_associacao_eol_transferido,
    transf_eol_acao_associacao_ptrf,
    transf_eol_acao_associacao_role,
    transf_eol_conta_associacao_cheque,
    transf_eol_conta_associacao_cartao,
    transferencia_eol,
    transf_eol_despesa,
    transf_eol_rateio_despesa_conta_cartao,
    transf_eol_rateio_despesa_conta_cartao_rateio_2,
    transf_eol_despesa_2_conta_cheque,         # Não deve ser copiada, por ter rateios da conta cheque
    transf_eol_rateio_despesa_2_conta_cheque,  # Não deve ser copiada, por ser da conta cheque
    transf_eol_receita_conta_cartao,
    transf_eol_receita_conta_cheque,           # Não deve ser copiada, por ser da conta cheque

):
    assert transf_eol_associacao_eol_transferido.acoes.count() == 2

    transferencia_eol.transferir()

    nova_unidade = Unidade.objects.get(codigo_eol=transferencia_eol.eol_historico)
    assert nova_unidade is not None, "Deve criar uma nova unidade com o código de histórico"
    assert nova_unidade.tipo_unidade == transf_eol_unidade_eol_transferido.tipo_unidade, "O tipo deve ser alterado para o novo."

    # Existe uma nova associação com o código eol transferido
    nova_associacao = Associacao.objects.get(unidade__codigo_eol=transferencia_eol.eol_transferido)
    assert nova_associacao is not None
    assert nova_associacao.unidade == transf_eol_unidade_eol_transferido, "Deve apontar para a unidade original."
    assert nova_associacao.acoes.count() == 2, "Deve ter a mesma quantidade de ações que a associação original"

    # A associação original deve apontar para a unidade de histórico (nova unidade criada) e manter os atributos originais
    associacao_original = Associacao.by_uuid(transf_eol_associacao_eol_transferido.uuid)
    assert associacao_original.unidade == nova_unidade, "Deve apontar para a unidade de histórico."
    assert associacao_original.acoes.count() == 2, "Deve ter a mesma quantidade de ações originais"

    # A conta_associacao de tipo_conta_transferido da associação original deve ter sido copiado para a nova associação
    contas_associacao_original = transf_eol_associacao_eol_transferido.contas.filter(tipo_conta=transferencia_eol.tipo_conta_transferido).all()
    contas_associacao_nova = nova_associacao.contas.filter(tipo_conta=transferencia_eol.tipo_conta_transferido).all()
    assert contas_associacao_nova.count() == contas_associacao_original.count(), "Deve ter a mesma quantidade de contas_associacao do tipo_conta_transferido"

    # Todas as contas_associacao de tipo_conta_transferido da associação original deve ter sido inativada
    assert contas_associacao_original.filter(status='INATIVA').count() == contas_associacao_original.count(), "Deve ter inativado todas as contas_associacao do tipo_conta_transferido"

    # Todos os gastos e rateios vinculados à conta_associacao de tipo_conta_transferido da associação original devem ser copiados para a nova associação
    despesas_original = transf_eol_associacao_eol_transferido.despesas.all()
    despesas_nova = nova_associacao.despesas.all()
    assert despesas_nova.count() == 1, "Deve ter copiado apenas as despesas que possuem rateios em contas_associacao de tipo_conta transferido"
    assert despesas_nova.first().rateios.count() == 2, "Deve ter copiado os rateios corretos"
    assert despesas_original.count() == 2, "A associação original deve manter as despesas originais"

    # Todos os gastos e rateios vinculados à conta_associacao de tipo_conta_transferido da associação original devem ser inativados
    assert despesas_original.filter(status='INATIVO').count() == despesas_original.filter(rateios__conta_associacao__tipo_conta=transferencia_eol.tipo_conta_transferido).distinct().count(), "Deve ter inativado todas as despesas originais"

    # Todas as receitas vinculadas à conta_associacao de tipo_conta_transferido da associação original devem ser copiadas para a nova associação
    receitas_original = transf_eol_associacao_eol_transferido.receitas.all()
    receitas_nova = nova_associacao.receitas.all()
    assert receitas_nova.count() == 1, "Deve ter copiado apenas as receitas que possuem rateios em contas_associacao de tipo_conta transferido"
    assert receitas_original.count() == 2, "A associação original deve manter as receitas originais"

    # Todas as receitas vinculadas à conta_associacao de tipo_conta_transferido da associação original devem ser inativadas
    assert receitas_original.filter(status='INATIVO').count() == receitas_original.filter(conta_associacao__tipo_conta=transferencia_eol.tipo_conta_transferido).distinct().count(), "Deve ter inativado todas as receitas originais"

    # Transferencia deve finalizar com sucesso
    assert transferencia_eol.status_processamento == 'SUCESSO'

