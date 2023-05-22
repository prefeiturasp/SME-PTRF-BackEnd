import pytest
from sme_ptrf_apps.core.api.serializers import TagLookupSerializer, TagSerializer

pytestmark = pytest.mark.django_db


def test_tag_serializer(tag):
    serializer = TagSerializer(tag)

    campos_esperados = [
        "id",
        "nome",
        "criado_em",
        "alterado_em",
        "uuid",
        "status"
    ]

    assert serializer.data
    assert [key for key in serializer.data.keys()] == campos_esperados


def test_taglookupserializer(tag):
    serializer = TagLookupSerializer(tag)

    campos_esperados = [
        'uuid',
        'nome',
        'status',
        'id'
    ]

    assert serializer.data
    assert [key for key in serializer.data.keys()] == campos_esperados
