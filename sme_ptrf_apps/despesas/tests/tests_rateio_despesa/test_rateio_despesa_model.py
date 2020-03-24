import pytest
from django.contrib import admin

from ...models import RateioDespesa

pytestmark = pytest.mark.django_db


def test_instance_model(rateio_despesa_capital):
    model = rateio_despesa_capital
    assert isinstance(model, RateioDespesa)
    assert model.associacao
    assert model.despesa
    assert model.conta_associacao
    assert model.acao_associacao
    assert model.aplicacao_recurso
    assert model.tipo_custeio
    assert model.especificacao_material_servico
    assert model.valor_rateio
    assert model.quantidade_itens_capital
    assert model.valor_item_capital
    assert model.numero_processo_incorporacao_capital
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.status == RateioDespesa.STATUS_INCOMPLETO


def test_srt_model(rateio_despesa_capital):
    assert rateio_despesa_capital.__str__() == '123456 - 100.00'


def test_meta_modelo(rateio_despesa_capital):
    assert rateio_despesa_capital._meta.verbose_name == 'Rateio de despesa'
    assert rateio_despesa_capital._meta.verbose_name_plural == 'Rateios de despesas'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[RateioDespesa]
