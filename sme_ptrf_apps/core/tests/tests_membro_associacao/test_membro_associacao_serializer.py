import pytest

from sme_ptrf_apps.core.api.serializers import MembroAssociacaoListSerializer

pytestmark = pytest.mark.django_db


def test_membro_associacao_serializer(membro_associacao):
    membro = MembroAssociacaoListSerializer(membro_associacao)
    assert membro.data is not None

