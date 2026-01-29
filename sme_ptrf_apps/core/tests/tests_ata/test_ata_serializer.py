import pytest
from waffle.testutils import override_flag
from model_bakery import baker

from ...api.serializers import AtaLookUpSerializer, AtaSerializer, AtaCreateSerializer
from ...models import Participante

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
    assert serializer.data['hora_reuniao'] == "00:00"
    assert serializer.data['justificativa_repasses_pendentes'] == ""
    assert 'precisa_professor_gremio' in serializer.data


def test_serializer_precisa_professor_gremio_field(ata_prestacao_conta_iniciada):
    serializer = AtaSerializer(ata_prestacao_conta_iniciada)
    assert 'precisa_professor_gremio' in serializer.data
    assert isinstance(serializer.data['precisa_professor_gremio'], bool)


@override_flag('historico-de-membros', active=False)
def test_create_serializer_remove_campos_quando_flag_desativada(ata_prestacao_conta_iniciada):
    """Testa se campos presidente_da_reuniao e secretario_da_reuniao são removidos quando flag está desativada"""
    from unittest.mock import patch
    from datetime import datetime
    
    serializer = AtaCreateSerializer()
    
    presentes_data = [{
        'identificacao': '1234567',
        'nome': 'Teste',
        'cargo': 'Cargo',
        'presidente_da_reuniao': True,
        'secretario_da_reuniao': False,
        'membro': False,
        'professor_gremio': False,
        'presente': True
    }]
    
    validated_data = {
        'associacao': ata_prestacao_conta_iniciada.associacao,
        'periodo': ata_prestacao_conta_iniciada.periodo,
        'tipo_ata': 'APRESENTACAO',
        'tipo_reuniao': 'ORDINARIA',
        'convocacao': 'PRIMEIRA',
        'data_reuniao': datetime(2020, 7, 1).date(),
        'local_reuniao': 'Local',
        'presidente_reuniao': 'Presidente',
        'cargo_presidente_reuniao': 'Cargo',
        'secretario_reuniao': 'Secretário',
        'cargo_secretaria_reuniao': 'Cargo',
        'hora_reuniao': datetime(2020, 7, 1, 10, 0).time(),
        'presentes_na_ata': presentes_data
    }
    
    # Mock do PresentesAtaCreateSerializer para capturar os dados passados
    with patch('sme_ptrf_apps.core.api.serializers.ata_serializer.PresentesAtaCreateSerializer') as mock_serializer_class:
        mock_serializer_instance = mock_serializer_class.return_value
        mock_participante = baker.make('Participante', ata=ata_prestacao_conta_iniciada)
        mock_serializer_instance.create.return_value = mock_participante
        
        ata = serializer.create(validated_data)
        
        # Verifica que o create foi chamado
        assert mock_serializer_instance.create.called
        
        # Verifica que os campos foram removidos antes de criar o participante
        called_data = mock_serializer_instance.create.call_args[0][0]
        assert 'presidente_da_reuniao' not in called_data
        assert 'secretario_da_reuniao' not in called_data
        
        # Verifica que o participante foi associado à ata
        assert ata.presentes_na_ata.first() == mock_participante


@override_flag('historico-de-membros', active=False)
def test_update_serializer_remove_campos_quando_flag_desativada(ata_prestacao_conta_iniciada):
    """Testa se campos presidente_da_reuniao e secretario_da_reuniao são removidos no update quando flag está desativada"""
    from unittest.mock import patch
    
    serializer = AtaCreateSerializer()
    
    presentes_data = [{
        'identificacao': '7654321',
        'nome': 'Teste Update',
        'cargo': 'Cargo Update',
        'presidente_da_reuniao': False,
        'secretario_da_reuniao': True,
        'membro': False,
        'professor_gremio': False,
        'presente': True
    }]
    
    validated_data = {
        'presentes_na_ata': presentes_data
    }
    
    # Mock do PresentesAtaCreateSerializer para capturar os dados passados
    with patch('sme_ptrf_apps.core.api.serializers.ata_serializer.PresentesAtaCreateSerializer') as mock_serializer_class:
        mock_serializer_instance = mock_serializer_class.return_value
        mock_participante = baker.make('Participante', ata=ata_prestacao_conta_iniciada)
        mock_serializer_instance.create.return_value = mock_participante
        
        ata = serializer.update(ata_prestacao_conta_iniciada, validated_data)
        
        # Verifica que o create foi chamado
        assert mock_serializer_instance.create.called
        
        # Verifica que os campos foram removidos antes de criar o participante
        called_data = mock_serializer_instance.create.call_args[0][0]
        assert 'presidente_da_reuniao' not in called_data
        assert 'secretario_da_reuniao' not in called_data
        
        # Verifica que a ata foi atualizada corretamente
        assert ata == ata_prestacao_conta_iniciada