import pytest

from ...api.serializers.faq_categoria_serializer import FaqCategoriaSerializer

pytestmark = pytest.mark.django_db


def test_serializer(faq_categoria):
    serializer = FaqCategoriaSerializer(faq_categoria)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['nome']
