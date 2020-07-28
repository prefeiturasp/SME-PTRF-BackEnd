import pytest
from sme_ptrf_apps.core.api.serializers import TagLookupSerializer

pytestmark = pytest.mark.django_db


def test_taglookupserializer(tag):
    serializer = TagLookupSerializer(tag)

    campos_esperados = [
        'uuid',
        'nome',
        'status'
    ]

    assert serializer.data
    assert [key for key in serializer.data.keys()] == campos_esperados
