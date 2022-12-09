
import pytest

from sme_ptrf_apps.dre.services.consolidado_dre_service import retornar_ja_publicadas, retificar_consolidado_dre

pytestmark = pytest.mark.django_db


def test_retificar_consolidado_dre(
    jwt_authenticated_client_dre,
    consolidado_dre_publicado_no_diario_oficial,
    prestacao_conta_pc1
):
    retificar_consolidado_dre(consolidado_dre_publicado_no_diario_oficial, [prestacao_conta_pc1])

    consolidado_dre_publicado_no_diario_oficial.refresh_from_db()
    assert consolidado_dre_publicado_no_diario_oficial.retificacoes.count() == 1

    retificacao = consolidado_dre_publicado_no_diario_oficial.retificacoes.first()
    assert retificacao.prestacoes_de_conta_do_consolidado_dre.count() == 1
    assert retificacao.prestacoes_de_conta_do_consolidado_dre.first() == prestacao_conta_pc1

    prestacao_conta_pc1.refresh_from_db()
    assert prestacao_conta_pc1.consolidado_dre == retificacao
    assert prestacao_conta_pc1.publicada is False
