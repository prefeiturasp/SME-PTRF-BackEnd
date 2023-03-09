import pytest

from sme_ptrf_apps.despesas.models import Despesa

pytestmark = pytest.mark.django_db


def test_deve_inativar_as_despesas_e_rateios_da_associacao_origem_que_tenham_o_tipo_de_conta_transferido(
    transf_eol_unidade_eol_transferido,
    transferencia_eol,
    transf_eol_associacao_eol_transferido,
    transf_eol_acao_associacao_ptrf,
    transf_eol_acao_associacao_role,
    transf_eol_associacao_nova,
    transf_eol_acao_ptrf,
    transf_eol_acao_role,
    transf_eol_conta_associacao_cheque,
    transf_eol_conta_associacao_cartao,
    transf_eol_despesa,
    transf_eol_rateio_despesa_conta_cartao,
    transf_eol_rateio_despesa_conta_cartao_rateio_2,
    transf_eol_despesa_2_conta_cheque,  # Não deve ser copiada, por ter rateios da conta cheque
    transf_eol_rateio_despesa_2_conta_cheque  # Não deve ser copiada, por ser da conta cheque
):
    transferencia_eol.inativar_despesas_associacao_do_tipo_transferido(transf_eol_associacao_eol_transferido)

    # Todos as despesas do tipo de conta transferido devem ser inativadas
    despesa_transferida = Despesa.objects.get(uuid=transf_eol_despesa.uuid)
    assert despesa_transferida.status == 'INATIVO', "Deve ter inativado a despesa transferida"

    # Todos os rateios da despesa do tipo de conta transferido devem ser inativados
    for rateio in despesa_transferida.rateios.all():
        assert rateio.status == 'INATIVO', "Deve ter inativado o rateio da despesa transferida"

    # Todas as despesas que não são do tipo de conta transferido devem permanecer ativas
    despesa_nao_transferida = Despesa.objects.get(uuid=transf_eol_despesa_2_conta_cheque.uuid)
    assert despesa_nao_transferida.status != 'INATIVO', "Não deve ter inativado a despesa não transferida"

    # Todos os rateios da despesa que não são do tipo de conta transferido devem permanecer ativos
    for rateio in despesa_nao_transferida.rateios.all():
        assert rateio.status != 'INATIVO', "Não deve ter inativado o rateio da despesa não transferida"
