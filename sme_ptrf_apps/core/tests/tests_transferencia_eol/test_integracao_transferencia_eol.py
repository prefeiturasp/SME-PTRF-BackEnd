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
