import pytest

from sme_ptrf_apps.core.models import PrestacaoConta
from sme_ptrf_apps.dre.services.vincular_consolidado_service import VincularConsolidadoService

pytestmark = pytest.mark.django_db


def test_vincular_consolidado_service_vincular_artefato_prestacao_conta_usando_consolidado_existente(
    vcs_periodo_2022_1,
    vcs_dre_ipiranga,
    vcs_consolidado_dre_ipiranga_2022_1,
    vcs_prestacao_conta_desvinculada
):
    VincularConsolidadoService.vincular_artefato(vcs_prestacao_conta_desvinculada)

    prestacao_conta = PrestacaoConta.by_id(vcs_prestacao_conta_desvinculada.id)

    assert prestacao_conta.consolidado_dre == vcs_consolidado_dre_ipiranga_2022_1
    assert prestacao_conta.publicada is True


def test_vincular_consolidado_service_vincular_artefato_prestacao_conta_criando_consolidado_inexistente(
    vcs_periodo_2022_1,
    vcs_dre_ipiranga,
    vcs_prestacao_conta_desvinculada
):
    from sme_ptrf_apps.dre.models import ConsolidadoDRE

    VincularConsolidadoService.vincular_artefato(vcs_prestacao_conta_desvinculada)

    prestacao_conta = PrestacaoConta.by_id(vcs_prestacao_conta_desvinculada.id)

    assert prestacao_conta.consolidado_dre is not None
    assert prestacao_conta.publicada is True

    assert prestacao_conta.consolidado_dre.periodo == vcs_periodo_2022_1
    assert prestacao_conta.consolidado_dre.dre == vcs_dre_ipiranga
    assert prestacao_conta.consolidado_dre.eh_parcial is False
    assert prestacao_conta.consolidado_dre.status == ConsolidadoDRE.STATUS_GERADOS_TOTAIS
