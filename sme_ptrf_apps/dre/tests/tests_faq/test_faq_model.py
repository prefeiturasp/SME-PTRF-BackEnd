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


def test_str_model(faq):
    assert faq.__str__() == 'Pergunta 01'


def test_meta_model(faq):
    assert faq._meta.verbose_name == 'Faq - Pergunta e Resposta'
    assert faq._meta.verbose_name_plural == 'Faqs - Perguntas e Respostas'


