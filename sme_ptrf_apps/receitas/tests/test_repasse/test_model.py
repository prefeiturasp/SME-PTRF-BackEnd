import pytest
from model_bakery import baker

from sme_ptrf_apps.receitas.models import Repasse
from sme_ptrf_apps.receitas.models.repasse import StatusRepasse

pytestmark = pytest.mark.django_db


def test_model(repasse):
    model = repasse
    assert isinstance(repasse, Repasse)
    assert model.associacao
    assert model.periodo
    assert model.valor_capital
    assert model.valor_custeio
    assert model.valor_livre == 0
    assert model.conta_associacao
    assert model.acao_associacao
    assert model.status == 'PENDENTE'


def test_str(repasse):
    assert str(repasse) == "Repasse<val_capital: 1000.28, val_custeio: 1000.4>"


def test_valor_total(repasse):
    assert repasse.valor_total == repasse.valor_capital + repasse.valor_custeio


def test_valor_realizado_nenhum_realizado(repasse):
    assert repasse.valor_realizado == 0


def test_valor_realizado_todos_realizados(repasse):
    repasse.realizado_capital = True
    repasse.realizado_custeio = True
    repasse.realizado_livre = True
    assert repasse.valor_realizado == 3


def test_possui_receita_vinculada_false(repasse):
    assert repasse.possui_receita_vinculada is False


def test_possui_receita_vinculada_true(repasse):
    tipo = baker.make('TipoReceita')
    baker.make('Receita', repasse=repasse, tipo_receita=tipo)
    assert repasse.possui_receita_vinculada is True


def test_get_campos_editaveis_nenhum_realizado(repasse):
    resultado = repasse.get_campos_editaveis()
    assert resultado['campos_identificacao'] is True
    assert resultado['valor_capital'] is True
    assert resultado['valor_custeio'] is True
    assert resultado['valor_livre'] is True
    assert resultado['campos_de_realizacao'] is False


def test_get_campos_editaveis_capital_realizado(repasse):
    repasse.realizado_capital = True
    repasse.save()
    resultado = repasse.get_campos_editaveis()
    assert resultado['campos_identificacao'] is False
    assert resultado['valor_capital'] is False
    assert resultado['valor_custeio'] is True
    assert resultado['valor_livre'] is True


def test_get_campos_editaveis_custeio_realizado(repasse):
    repasse.realizado_custeio = True
    repasse.save()
    resultado = repasse.get_campos_editaveis()
    assert resultado['campos_identificacao'] is False
    assert resultado['valor_capital'] is True
    assert resultado['valor_custeio'] is False
    assert resultado['valor_livre'] is True


def test_get_campos_editaveis_livre_realizado(repasse):
    repasse.realizado_livre = True
    repasse.save()
    resultado = repasse.get_campos_editaveis()
    assert resultado['campos_identificacao'] is False
    assert resultado['valor_capital'] is True
    assert resultado['valor_custeio'] is True
    assert resultado['valor_livre'] is False


def test_repasses_pendentes_da_acao_associacao_no_periodo(repasse, acao_associacao, periodo):
    qs = Repasse.repasses_pendentes_da_acao_associacao_no_periodo(acao_associacao, periodo)
    assert repasse in qs


def test_repasses_pendentes_da_acao_associacao_no_periodo_exclui_realizados(
    repasse_2020_1_realizado, acao_associacao, periodo_2020_1
):
    qs = Repasse.repasses_pendentes_da_acao_associacao_no_periodo(acao_associacao, periodo_2020_1)
    assert repasse_2020_1_realizado not in qs


def test_repasses_pendentes_da_acao_associacao_no_periodo_filtra_por_conta(
    repasse, acao_associacao, periodo, conta_associacao
):
    qs = Repasse.repasses_pendentes_da_acao_associacao_no_periodo(
        acao_associacao, periodo, conta_associacao=conta_associacao
    )
    assert repasse in qs


def test_repasses_pendentes_da_acao_associacao_no_periodo_conta_incorreta(
    repasse, acao_associacao, periodo, conta_associacao_factory
):
    outra_conta = conta_associacao_factory()
    qs = Repasse.repasses_pendentes_da_acao_associacao_no_periodo(
        acao_associacao, periodo, conta_associacao=outra_conta
    )
    assert repasse not in qs


def test_status_to_json():
    resultado = Repasse.status_to_json()
    ids = [item['id'] for item in resultado]
    assert StatusRepasse.PENDENTE.name in ids
    assert StatusRepasse.REALIZADO.name in ids
    for item in resultado:
        assert 'id' in item
        assert 'nome' in item


def test_filter_by_recurso_sem_recurso_retorna_queryset_completo(repasse):
    qs = Repasse.objects.all()
    resultado = Repasse.filter_by_recurso(qs, recurso=None)
    assert repasse in resultado
