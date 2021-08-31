import pytest
from django.contrib import admin
from freezegun import freeze_time

from ...models import RateioDespesa
from ...status_cadastro_completo import STATUS_COMPLETO
from ....core.models import Periodo

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
    assert model.status == STATUS_COMPLETO
    assert model.conferido
    assert isinstance(model.periodo_conciliacao, Periodo)
    assert model.valor_original
    assert model.saida_de_recurso_externo is False


def test_srt_model(rateio_despesa_capital):
    assert rateio_despesa_capital.__str__() == f'Rateio {rateio_despesa_capital.pk}'


def test_meta_modelo(rateio_despesa_capital):
    assert rateio_despesa_capital._meta.verbose_name == 'Rateio de despesa'
    assert rateio_despesa_capital._meta.verbose_name_plural == 'Rateios de despesas'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[RateioDespesa]


def test_marcar_conferido(rateio_despesa_nao_conferido):
    rateio_despesa_nao_conferido.marcar_conferido()
    rateio = RateioDespesa.objects.get(id=rateio_despesa_nao_conferido.id)
    assert rateio.conferido


def test_desmarcar_conferido(rateio_despesa_conferido):
    rateio_despesa_conferido.desmarcar_conferido()
    rateio = RateioDespesa.objects.get(id=rateio_despesa_conferido.id)
    assert not rateio.conferido


@freeze_time('2020-03-12')
def test_notificar_nao_conferido(rateio_despesa_01_03_2020_nao_conferido, parametros_tempo_nao_conferido_10_dias):
    assert rateio_despesa_01_03_2020_nao_conferido.notificar_dias_nao_conferido == 11


@freeze_time('2020-03-12')
def test_notificar_nao_conferido_quando_limite_e_superior(rateio_despesa_01_03_2020_nao_conferido,
                                                          parametros_tempo_nao_conferido_60_dias):
    assert rateio_despesa_01_03_2020_nao_conferido.notificar_dias_nao_conferido == 0


@freeze_time('2020-03-12')
def test_notificar_nao_conferido_quando_conferido(rateio_despesa_01_03_2020_conferido,
                                                  parametros_tempo_nao_conferido_10_dias):
    assert rateio_despesa_01_03_2020_conferido.notificar_dias_nao_conferido == 0


def test_despesa_conferida_quando_editada_deve_volta_para_nao_conferida(rateio_despesa_conferido):
    assert rateio_despesa_conferido.conferido, "Devia iniciar como conferida."
    rateio_despesa_conferido.valor_rateio = 100
    rateio_despesa_conferido.save()
    receita = RateioDespesa.objects.get(id=rateio_despesa_conferido.id)
    assert not receita.conferido, "Devia ter passado para não conferida."
