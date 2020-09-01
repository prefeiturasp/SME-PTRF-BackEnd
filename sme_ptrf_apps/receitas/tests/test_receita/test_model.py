import pytest
from freezegun import freeze_time

from ...models import Receita
from ...tipos_aplicacao_recurso_receitas import APLICACAO_LIVRE
from ....core.models import Periodo

pytestmark = pytest.mark.django_db


def test_instance(receita):
    model = receita
    assert isinstance(model, Receita)
    assert model.associacao
    assert model.data
    assert model.valor
    assert model.conta_associacao
    assert model.acao_associacao
    assert model.tipo_receita
    assert model.conferido
    assert isinstance(model.periodo_conciliacao, Periodo)
    assert model.detalhe_tipo_receita
    assert model.detalhe_outros is not None
    assert model.notificar_dias_nao_conferido is not None


def test_instance_receita_devolucao(receita_devolucao):
    model = receita_devolucao
    assert isinstance(model, Receita)
    assert model.associacao
    assert model.data
    assert model.valor
    assert model.conta_associacao
    assert model.acao_associacao
    assert model.tipo_receita
    assert model.tipo_receita.e_devolucao
    assert model.conferido
    assert isinstance(model.periodo_conciliacao, Periodo)
    assert model.referencia_devolucao
    assert model.detalhe_outros is not None


def test_str(receita):
    assert str(receita) == "RECEITA<Estorno A - 2020-03-26 - 100.0>"


def test_marcar_conferido(receita_nao_conferida):
    receita_nao_conferida.marcar_conferido()
    receita = Receita.objects.get(id=receita_nao_conferida.id)
    assert receita.conferido


def test_desmarcar_conferido(receita_conferida):
    receita_conferida.desmarcar_conferido()
    receita = Receita.objects.get(id=receita_conferida.id)
    assert not receita.conferido


def test_receita_livre_utilizacao(receita):
    receita.categoria_receita = APLICACAO_LIVRE
    receita.save()
    assert Receita.by_id(receita.id).categoria_receita == APLICACAO_LIVRE


@freeze_time('2020-03-12')
def test_notificar_nao_conferido(receita_nao_conferida_desde_01_03_2020, parametros_tempo_nao_conferido_10_dias):
    assert receita_nao_conferida_desde_01_03_2020.notificar_dias_nao_conferido == 11


@freeze_time('2020-03-12')
def test_notificar_nao_conferido_quando_limite_e_superior(receita_nao_conferida_desde_01_03_2020,
                                                          parametros_tempo_nao_conferido_60_dias):
    assert receita_nao_conferida_desde_01_03_2020.notificar_dias_nao_conferido == 0


@freeze_time('2020-03-12')
def test_notificar_nao_conferido_quando_conferido(receita_conferida, parametros_tempo_nao_conferido_10_dias):
    assert receita_conferida.notificar_dias_nao_conferido == 0
