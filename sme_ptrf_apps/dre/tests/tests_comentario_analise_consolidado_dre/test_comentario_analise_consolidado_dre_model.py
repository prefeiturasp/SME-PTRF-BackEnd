import pytest
from django.contrib import admin
from ...models import ConsolidadoDRE, ComentarioAnaliseConsolidadoDRE

pytestmark = pytest.mark.django_db


def test_instance_model(comentario_analise_consolidado_dre_01, consolidado_dre_teste_model_comentario_analise_consolidado_dre):
    model = comentario_analise_consolidado_dre_01
    assert isinstance(model, ComentarioAnaliseConsolidadoDRE)
    assert isinstance(model.consolidado_dre, ConsolidadoDRE)
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.ordem
    assert model.comentario
    assert model.notificado is False
    assert model.notificado_em is None


def test_str_model(comentario_analise_consolidado_dre_01):
    assert comentario_analise_consolidado_dre_01.__str__() == '1 - Este é um comentario de analise de consolidadodo DRE'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[ComentarioAnaliseConsolidadoDRE]
