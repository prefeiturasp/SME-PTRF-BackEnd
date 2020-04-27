import pytest
from django.contrib import admin

from ...models import Fornecedor

pytestmark = pytest.mark.django_db


def test_instance_model(fornecedor_jose):
    model = fornecedor_jose
    assert isinstance(model, Fornecedor)
    assert model.nome
    assert model.cpf_cnpj
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_srt_model(fornecedor_jose):
    assert fornecedor_jose.__str__() == 'José - 079.962.460-84'


def test_meta_modelo(fornecedor_jose):
    assert fornecedor_jose._meta.verbose_name == 'Fornecedor'
    assert fornecedor_jose._meta.verbose_name_plural == 'Fornecedores'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Fornecedor]
