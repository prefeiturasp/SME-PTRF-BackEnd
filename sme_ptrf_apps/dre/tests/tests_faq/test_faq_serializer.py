import pytest

from ...api.serializers.faq_serializer import FaqSerializer

pytestmark = pytest.mark.django_db


def test_serializer(faq):
    serializer = FaqSerializer(faq)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['pergunta']
    assert serializer.data['resposta']
