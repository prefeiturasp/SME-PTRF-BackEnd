import pytest
from django.contrib import admin

from ...models import EspecificacaoMaterialServico

pytestmark = pytest.mark.django_db


def test_instance_model(especificacao_material_servico):
    model = especificacao_material_servico
    assert isinstance(model, EspecificacaoMaterialServico)
    assert model.descricao
    assert model.aplicacao_recurso
    assert model.tipo_custeio
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_srt_model(especificacao_material_servico):
    assert especificacao_material_servico.__str__() == 'Material elétrico'


def test_meta_modelo(especificacao_material_servico):
    assert especificacao_material_servico._meta.verbose_name == 'Especificação de material ou serviço'
    assert especificacao_material_servico._meta.verbose_name_plural == 'Especificações de materiais ou serviços'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[EspecificacaoMaterialServico]
