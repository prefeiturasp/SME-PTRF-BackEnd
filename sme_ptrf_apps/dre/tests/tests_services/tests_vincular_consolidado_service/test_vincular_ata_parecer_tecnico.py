import pytest

from sme_ptrf_apps.dre.models import AtaParecerTecnico
from sme_ptrf_apps.dre.services.vincular_consolidado_service import VincularConsolidadoService

pytestmark = pytest.mark.django_db


def test_vincular_consolidado_service_vincular_ata_gravando_ultima_sequencia_de_consolidados_existentes(
    vcs_periodo_2022_1,
    vcs_dre_ipiranga,
    vcs_consolidado_dre_ipiranga_2022_1_parcial_1,
    vcs_consolidado_dre_ipiranga_2022_1_parcial_2,
    vcs_ata_parecer_tecnico_desvinculada
):
    VincularConsolidadoService.vincular_artefato(vcs_ata_parecer_tecnico_desvinculada)

    ata = AtaParecerTecnico.by_id(vcs_ata_parecer_tecnico_desvinculada.id)

    assert ata.consolidado_dre == vcs_consolidado_dre_ipiranga_2022_1_parcial_2
    assert ata.sequencia_de_publicacao == 2


def test_vincular_consolidado_service_vincular_ata_gravando_sequencia_de_consolidado_criado(
    vcs_periodo_2022_1,
    vcs_dre_ipiranga,
    vcs_ata_parecer_tecnico_desvinculada
):
    VincularConsolidadoService.vincular_artefato(vcs_ata_parecer_tecnico_desvinculada)

    ata = AtaParecerTecnico.by_id(vcs_ata_parecer_tecnico_desvinculada.id)

    assert ata.consolidado_dre is not None
    assert ata.sequencia_de_publicacao == 0
