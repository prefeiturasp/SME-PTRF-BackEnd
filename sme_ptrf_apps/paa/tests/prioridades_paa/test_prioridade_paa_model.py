import pytest
from sme_ptrf_apps.paa.models import PrioridadePaa
from sme_ptrf_apps.paa.fixtures.factories import PrioridadePaaFactory
from sme_ptrf_apps.paa.models.prioridade_paa import SimNaoChoices


@pytest.mark.django_db
def test_criacao_prioridade_paa(flag_paa, paa):
    PrioridadePaaFactory(paa=paa)
    assert PrioridadePaa.objects.count() == 1


@pytest.mark.django_db
def test_prioridade_nome_da_acao_pdde(flag_paa, paa, acao_pdde, programa_pdde):
    prioridade = PrioridadePaaFactory(
        recurso="PDDE",
        tipo_aplicacao="CAPITAL",
        acao_associacao=None,
        programa_pdde=programa_pdde,
        paa=paa,
        acao_pdde=acao_pdde
    )
    assert prioridade.nome() == acao_pdde.nome


@pytest.mark.django_db
def test_prioridade_nome_da_acao_associacao(flag_paa, paa, acao_associacao):
    prioridade = PrioridadePaaFactory(
        recurso="PTRF",
        tipo_aplicacao="CAPITAL",
        acao_associacao=acao_associacao,
        paa=paa,
    )
    assert prioridade.nome() == acao_associacao.acao.nome


@pytest.mark.django_db
def test_prioridade_nome_de_recurso_proprio(flag_paa, paa):
    prioridade = PrioridadePaaFactory(
        recurso="RECURSO_PROPRIO",
        acao_associacao=None,
        acao_pdde=None,
        programa_pdde=None,
        tipo_despesa_custeio=None,
        tipo_aplicacao="CAPITAL",
        paa=paa,
    )
    assert prioridade.nome() == 'Recursos Próprios'


def test_simnao_choices_values():
    assert SimNaoChoices.SIM == 1
    assert SimNaoChoices.NAO == 0
    assert SimNaoChoices(1).label == "Sim"
    assert SimNaoChoices(0).label == "Não"


def test_simnao_choices_to_dict():
    dict_esperado = [
        {"key": 1, "value": "Sim"},
        {"key": 0, "value": "Não"}
    ]
    assert SimNaoChoices.to_dict() == dict_esperado
