import pytest

from sme_ptrf_apps.paa.models import AtaPaa, Paa

pytestmark = pytest.mark.django_db


def test_instance_model(ata_paa):
    model = ata_paa
    assert isinstance(model, AtaPaa)
    assert isinstance(model.paa, Paa)
    assert model.tipo_ata
    assert model.tipo_reuniao
    assert model.convocacao
    assert model.status_geracao_pdf
    assert model.data_reuniao
    assert model.local_reuniao
    assert model.comentarios
    assert model.parecer_conselho
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.preenchida_em is None
    assert model.justificativa_repasses_pendentes == ""
    assert model.hora_reuniao
    assert model.previa is False
    assert model.pdf_gerado_previamente is False

