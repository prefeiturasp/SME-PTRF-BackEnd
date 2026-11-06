import pytest
from datetime import date

from sme_ptrf_apps.core.api.serializers.presentes_ata_serializer import (
    PresentesAtaCreateSerializer,
)


pytestmark = pytest.mark.django_db


def test_presentes_ata_create_serializer_valido(ata_2020_1_teste):
    serializer = PresentesAtaCreateSerializer(data={
        'ata': str(ata_2020_1_teste.uuid),
        'identificacao': '0001',
        'nome': 'Arnaldo',
        'cargo': 'Vogal',
        'data_inicio_no_cargo': '25/03/2024',
        'vago': True,
        'membro': True,
        'presente': True,
        'presidente_da_reuniao': True,
        'secretario_da_reuniao': False,
        'professor_gremio': False,
    })

    assert serializer.is_valid(), serializer.errors
    validated = serializer.validated_data
    assert validated['ata'] == ata_2020_1_teste
    assert validated['data_inicio_no_cargo'] == date(2024, 3, 25)
    assert validated['vago'] is True
    assert validated['presidente_da_reuniao'] is True
    assert validated['secretario_da_reuniao'] is False


@pytest.mark.parametrize('data_informada', ['25/03/2024', '2024-03-25'])
def test_presentes_ata_create_serializer_aceita_formatos_data_inicio_no_cargo(ata_2020_1_teste, data_informada):
    serializer = PresentesAtaCreateSerializer(data={
        'ata': str(ata_2020_1_teste.uuid),
        'data_inicio_no_cargo': data_informada,
    })

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data['data_inicio_no_cargo'] == date(2024, 3, 25)


def test_presentes_ata_create_serializer_data_inicio_no_cargo_formato_invalido(ata_2020_1_teste):
    serializer = PresentesAtaCreateSerializer(data={
        'ata': str(ata_2020_1_teste.uuid),
        'data_inicio_no_cargo': 'data-invalida',
    })

    assert not serializer.is_valid()
    assert 'data_inicio_no_cargo' in serializer.errors


def test_presentes_ata_create_serializer_valores_padrao(ata_2020_1_teste):
    serializer = PresentesAtaCreateSerializer(data={'ata': str(ata_2020_1_teste.uuid)})

    assert serializer.is_valid(), serializer.errors
    validated = serializer.validated_data
    assert validated['vago'] is False
    assert 'data_inicio_no_cargo' not in validated
    assert 'presidente_da_reuniao' not in validated
    assert 'secretario_da_reuniao' not in validated


def test_presentes_ata_create_serializer_presidente_e_secretario_nulos(ata_2020_1_teste):
    serializer = PresentesAtaCreateSerializer(data={
        'ata': str(ata_2020_1_teste.uuid),
        'presidente_da_reuniao': None,
        'secretario_da_reuniao': None,
    })

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data['presidente_da_reuniao'] is None
    assert serializer.validated_data['secretario_da_reuniao'] is None
