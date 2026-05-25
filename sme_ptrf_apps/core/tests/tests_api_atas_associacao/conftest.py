import pytest

from sme_ptrf_apps.core.models import Ata


@pytest.fixture
def ata_apresentacao(ata_factory, prestacao_conta_factory, associacao):
    prestacao_conta = prestacao_conta_factory(associacao=associacao)
    return ata_factory(
        prestacao_conta=prestacao_conta,
        associacao=associacao,
        periodo=prestacao_conta.periodo,
        tipo_ata=Ata.ATA_APRESENTACAO,
        status_geracao_pdf=Ata.STATUS_NAO_GERADO,
        pdf_gerado_previamente=False,
        presidente_reuniao='José',
        secretario_reuniao='Ana',
    )
