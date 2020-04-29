import pytest

from sme_ptrf_apps.receitas.api.serializers import RepasseSerializer

pytestmark = pytest.mark.django_db


def test_serializer(repasse):
    serializer = RepasseSerializer(repasse)
    assert serializer.data
