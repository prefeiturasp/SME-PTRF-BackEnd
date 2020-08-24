import pytest
from django.contrib import admin
from ...models import Faq

pytestmark = pytest.mark.django_db


def test_instance_model(faq):
    model = faq
    assert isinstance(model, Faq)
    assert model.id
    assert model.uuid
    assert model.pergunta
    assert model.resposta
    assert model.categoria


