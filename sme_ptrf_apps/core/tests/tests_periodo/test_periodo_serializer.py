import pytest

from ...api.serializers.periodo_serializer import (PeriodoSerializer, PeriodoLookUpSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(periodo):
    serializer = PeriodoSerializer(periodo)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['referencia']
    assert serializer.data['data_inicio_realizacao_despesas']
    assert serializer.data['data_fim_realizacao_despesas']
    assert serializer.data['data_prevista_repasse']
    assert serializer.data['data_inicio_prestacao_contas']
    assert serializer.data['data_fim_prestacao_contas']


def test_lookup_serializer(periodo):
    serializer = PeriodoLookUpSerializer(periodo)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['referencia']
    assert serializer.data['data_inicio_realizacao_despesas']
    assert serializer.data['data_fim_realizacao_despesas']
