import pytest

from sme_ptrf_apps.dre.models import Lauda
from sme_ptrf_apps.dre.services.vincular_consolidado_service import VincularConsolidadoService

pytestmark = pytest.mark.django_db


def test_vincular_consolidado_service_vincular_artefato_lauda_usando_consolidado_existente(
    vcs_periodo_2022_1,
    vcs_dre_ipiranga,
    vcs_consolidado_dre_ipiranga_2022_1,
    vcs_lauda_desvinculada
):
    VincularConsolidadoService.vincular_artefato(vcs_lauda_desvinculada)

    relatorio = Lauda.by_id(vcs_lauda_desvinculada.id)

    assert relatorio.consolidado_dre == vcs_consolidado_dre_ipiranga_2022_1


def test_vincular_consolidado_service_vincular_artefato_lauda_criando_consolidado_inexistente(
    vcs_periodo_2022_1,
    vcs_dre_ipiranga,
    vcs_lauda_desvinculada
):
    from sme_ptrf_apps.dre.models import ConsolidadoDRE

    VincularConsolidadoService.vincular_artefato(vcs_lauda_desvinculada)

    lauda = Lauda.by_id(vcs_lauda_desvinculada.id)

    assert lauda.consolidado_dre is not None

    assert lauda.consolidado_dre.periodo == vcs_periodo_2022_1
    assert lauda.consolidado_dre.dre == vcs_dre_ipiranga
    assert lauda.consolidado_dre.eh_parcial is False
    assert lauda.consolidado_dre.status == ConsolidadoDRE.STATUS_GERADOS_TOTAIS
