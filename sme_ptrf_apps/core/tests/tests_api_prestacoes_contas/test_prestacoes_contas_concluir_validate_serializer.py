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


def test_serializer_rejeita_uuids_nao_existentes(db):
    invalid_data = {
        'associacao_uuid': str(uuid4()),
        'periodo_uuid': str(uuid4())
    }

    serializer = PrestacoesContasConcluirValidateSerializer(data=invalid_data)
    assert not serializer.is_valid(), "Serializer deve ser inválido com UUIDs não existentes"
