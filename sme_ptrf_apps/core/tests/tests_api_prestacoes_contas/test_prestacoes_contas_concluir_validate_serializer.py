import pytest

from uuid import uuid4
from sme_ptrf_apps.core.api.serializers.validation_serializers import PrestacoesContasConcluirValidateSerializer

pytestmark = pytest.mark.django_db


def test_serializer_valida_uuids(associacao, periodo):
    valid_data = {
        'associacao_uuid': str(associacao.uuid),
        'periodo_uuid': str(periodo.uuid)
    }

    serializer = PrestacoesContasConcluirValidateSerializer(data=valid_data)

    assert serializer.is_valid(), "Serializer deve ser válido com UUIDs existentes"


def test_serializer_ausente_exige_substituto(associacao, periodo):
    serializer = PrestacoesContasConcluirValidateSerializer(data={
        'associacao_uuid': str(associacao.uuid),
        'periodo_uuid': str(periodo.uuid),
        'status_presidente': 'AUSENTE',
    })

    assert not serializer.is_valid()


def test_serializer_presente_zera_substituto(associacao, periodo):
    serializer = PrestacoesContasConcluirValidateSerializer(data={
        'associacao_uuid': str(associacao.uuid),
        'periodo_uuid': str(periodo.uuid),
        'status_presidente': 'PRESENTE',
        'cargo_substituto_presidente_ausente': 'VICE_PRESIDENTE_DIRETORIA_EXECUTIVA',
    })

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data['cargo_substituto_presidente_ausente'] is None


def test_serializer_rejeita_presidente_como_substituto(associacao, periodo):
    serializer = PrestacoesContasConcluirValidateSerializer(data={
        'associacao_uuid': str(associacao.uuid),
        'periodo_uuid': str(periodo.uuid),
        'status_presidente': 'AUSENTE',
        'cargo_substituto_presidente_ausente': 'PRESIDENTE_DIRETORIA_EXECUTIVA',
    })

    assert not serializer.is_valid()


def test_serializer_aceita_vogal_como_substituto(associacao, periodo):
    serializer = PrestacoesContasConcluirValidateSerializer(data={
        'associacao_uuid': str(associacao.uuid),
        'periodo_uuid': str(periodo.uuid),
        'status_presidente': 'AUSENTE',
        'cargo_substituto_presidente_ausente': 'VOGAL_3',
    })

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data['cargo_substituto_presidente_ausente'] == 'VOGAL_3'


def test_serializer_rejeita_uuids_nao_existentes(db):
    invalid_data = {
        'associacao_uuid': str(uuid4()),
        'periodo_uuid': str(uuid4())
    }

    serializer = PrestacoesContasConcluirValidateSerializer(data=invalid_data)
    assert not serializer.is_valid(), "Serializer deve ser inválido com UUIDs não existentes"
