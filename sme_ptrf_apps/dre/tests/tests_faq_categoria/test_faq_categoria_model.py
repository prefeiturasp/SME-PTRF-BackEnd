import pytest
from ...models import FaqCategoria

pytestmark = pytest.mark.django_db


def test_instance_model(faq_categoria):
    model = faq_categoria
    assert isinstance(model, FaqCategoria)
    assert model.id
    assert model.uuid
    assert model.nome
