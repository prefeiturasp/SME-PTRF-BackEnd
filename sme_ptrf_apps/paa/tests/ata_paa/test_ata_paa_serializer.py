import pytest

from sme_ptrf_apps.paa.api.serializers.ata_paa_serializer import AtaPaaLookUpSerializer, AtaPaaSerializer

pytestmark = pytest.mark.django_db


def test_lookup_serializer(ata_paa):
    serializer = AtaPaaLookUpSerializer(ata_paa)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['nome']
    assert serializer.data['alterado_em'] is None


def test_serializer(ata_paa):
    serializer = AtaPaaSerializer(ata_paa)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['paa']
    assert serializer.data['associacao']
    assert serializer.data['tipo_ata']
    assert serializer.data['tipo_reuniao']
    assert serializer.data['convocacao']
    assert serializer.data['data_reuniao']
    assert serializer.data['local_reuniao']
    assert serializer.data['comentarios']
    assert serializer.data['parecer_conselho']
    assert serializer.data['nome']
    assert serializer.data['hora_reuniao'] == "00:00"
    assert serializer.data['justificativa'] == ""

