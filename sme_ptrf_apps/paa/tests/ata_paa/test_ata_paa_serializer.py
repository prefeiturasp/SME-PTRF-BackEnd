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
    assert 'precisa_professor_gremio' in serializer.data
    assert isinstance(serializer.data['precisa_professor_gremio'], bool)


def test_serializer_precisa_professor_gremio_true(ata_paa, parametros):
    """Testa se serializer retorna precisa_professor_gremio=True quando unidade precisa"""
    parametros.tipos_unidades_professor_gremio = ['EMEF']
    parametros.save()
    
    ata_paa.paa.associacao.unidade.tipo_unidade = 'EMEF'
    ata_paa.paa.associacao.unidade.save()
    
    serializer = AtaPaaSerializer(ata_paa)
    assert serializer.data['precisa_professor_gremio'] is True


def test_serializer_precisa_professor_gremio_false(ata_paa, parametros):
    """Testa se serializer retorna precisa_professor_gremio=False quando unidade não precisa"""
    parametros.tipos_unidades_professor_gremio = []
    parametros.save()
    
    serializer = AtaPaaSerializer(ata_paa)
    assert serializer.data['precisa_professor_gremio'] is False

