import pytest
from ...models import FaqCategoria

pytestmark = pytest.mark.django_db


def test_instance_model(faq_categoria):
    model = faq_categoria
    assert isinstance(model, FaqCategoria)
    assert model.id
    assert model.uuid
    assert model.nome


def test_str_model(faq_categoria):
    assert faq_categoria.__str__() == 'Geral'


def test_meta_model(faq_categoria):
    assert faq_categoria._meta.verbose_name == 'Faq - Categoria'
    assert faq_categoria._meta.verbose_name_plural == 'Faqs - Categorias'
