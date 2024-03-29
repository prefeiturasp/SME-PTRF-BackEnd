
import pytest

pytestmark = pytest.mark.django_db


def test_retorna_pcs_do_consolidado_com_retificacao(
    jwt_authenticated_client_dre,
    consolidado_dre_publicado_no_diario_oficial_com_pcs_vinculadas,
    retificacao_dre,
    prestacao_conta_pc1,
    prestacao_conta_pc2,
    prestacao_conta_pc3
):
    result = consolidado_dre_publicado_no_diario_oficial_com_pcs_vinculadas.pcs_vinculadas_ao_consolidado()

    # Pcs vinculadas ao consolidado original
    assert len(consolidado_dre_publicado_no_diario_oficial_com_pcs_vinculadas.prestacoes_de_conta_do_consolidado_dre.all()) == 1

    # Pcs vinculadas a retificação
    assert len(retificacao_dre.prestacoes_de_conta_do_consolidado_dre.all()) == 2

    # Total de Pcs (consolidado original + retificacao)
    assert len(result) == 3


def test_retorna_pcs_do_consolidado_sem_retificacao(
    jwt_authenticated_client_dre,
    consolidado_dre_publicado_no_diario_oficial_com_uma_pc_vinculada,
    retificacao_dre,
    prestacao_conta_pc1,
):
    result = consolidado_dre_publicado_no_diario_oficial_com_uma_pc_vinculada.pcs_vinculadas_ao_consolidado()

    # Pcs vinculadas ao consolidado original
    assert len(consolidado_dre_publicado_no_diario_oficial_com_uma_pc_vinculada.prestacoes_de_conta_do_consolidado_dre.all()) == 1

    # Pcs vinculadas a retificação
    assert len(retificacao_dre.prestacoes_de_conta_do_consolidado_dre.all()) == 0

    # Total de Pcs (consolidado original + retificacao)
    assert len(result) == 1
