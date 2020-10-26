import pytest

from ...api.serializers import AtaLookUpSerializer, AtaSerializer

pytestmark = pytest.mark.django_db


def test_lookup_serializer(ata_prestacao_conta_iniciada):

    serializer = AtaLookUpSerializer(ata_prestacao_conta_iniciada)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['nome']
    assert serializer.data['alterado_em'] is None


def test_serializer(ata_prestacao_conta_iniciada):

    serializer = AtaSerializer(ata_prestacao_conta_iniciada)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['prestacao_conta']
    assert serializer.data['periodo']
    assert serializer.data['associacao']
    assert serializer.data['tipo_ata']
    assert serializer.data['tipo_reuniao']
    assert serializer.data['convocacao']
    assert serializer.data['data_reuniao']
    assert serializer.data['local_reuniao']
    assert serializer.data['presidente_reuniao']
    assert serializer.data['cargo_presidente_reuniao']
    assert serializer.data['secretario_reuniao']
    assert serializer.data['cargo_secretaria_reuniao']
    assert serializer.data['comentarios']
    assert serializer.data['parecer_conselho']
    assert serializer.data['nome']
    assert serializer.data['retificacoes'] == ''
