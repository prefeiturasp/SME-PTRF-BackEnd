import pytest

pytestmark = pytest.mark.django_db


def test_vincular_pcs_ao_consolidado(
    consolidado_dre_teste_model_consolidado_dre,
    prestacao_conta_do_consolidado
):
    assert not consolidado_dre_teste_model_consolidado_dre.pcs_do_consolidado.exists()
    consolidado_dre_teste_model_consolidado_dre.vincular_pc_ao_consolidado(prestacao_conta_do_consolidado)
    assert consolidado_dre_teste_model_consolidado_dre.pcs_do_consolidado.exists()
    assert consolidado_dre_teste_model_consolidado_dre.pcs_do_consolidado.first() == prestacao_conta_do_consolidado

