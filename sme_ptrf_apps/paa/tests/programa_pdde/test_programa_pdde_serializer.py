import pytest

from sme_ptrf_apps.paa.api.serializers import ProgramaPddeSerializer


pytestmark = pytest.mark.django_db


def test_programa_pdde_list_serializer(programa_pdde):
    serializer = ProgramaPddeSerializer(programa_pdde)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'nome' in serializer.data
    assert 'pode_ser_excluida' in serializer.data
