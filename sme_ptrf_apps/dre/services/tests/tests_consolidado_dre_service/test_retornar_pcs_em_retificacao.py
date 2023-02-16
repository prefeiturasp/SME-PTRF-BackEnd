
import pytest

pytestmark = pytest.mark.django_db


def test_retorna_pcs_em_retificacao(
    jwt_authenticated_client_dre,
    consolidado_dre_publicado_no_diario_oficial,
    retificacao_dre,
    prestacao_conta_pc1,
    prestacao_conta_pc2,
    prestacao_conta_pc3
):
    result = retificacao_dre.pcs_em_retificacao()

    # Pcs retificaveis
    assert len(consolidado_dre_publicado_no_diario_oficial.prestacoes_de_conta_do_consolidado_dre.all()) == 1

    # Pcs ja retificadas
    assert len(retificacao_dre.prestacoes_de_conta_do_consolidado_dre.all()) == 2

    assert len(result) == 2
