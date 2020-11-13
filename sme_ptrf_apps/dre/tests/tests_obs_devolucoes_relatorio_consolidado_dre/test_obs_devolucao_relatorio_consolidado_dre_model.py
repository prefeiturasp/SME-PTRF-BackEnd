import pytest
from django.contrib import admin

from ...models import ObsDevolucaoRelatorioConsolidadoDRE
from ....core.models import Unidade, Periodo, TipoConta, TipoDevolucaoAoTesouro
from ....receitas.models import DetalheTipoReceita

pytestmark = pytest.mark.django_db


def test_instance_model_devolucao_conta(obs_devolucao_conta_relatorio_dre_consolidado):
    model = obs_devolucao_conta_relatorio_dre_consolidado
    assert isinstance(model, ObsDevolucaoRelatorioConsolidadoDRE)
    assert isinstance(model.dre, Unidade)
    assert isinstance(model.periodo, Periodo)
    assert isinstance(model.tipo_conta, TipoConta)
    assert isinstance(model.tipo_devolucao_a_conta, DetalheTipoReceita)
    assert model.tipo_devolucao == 'CONTA'
    assert model.observacao

def test_instance_model_devolucao_tesouro(obs_devolucao_tesouro_relatorio_dre_consolidado):
    model = obs_devolucao_tesouro_relatorio_dre_consolidado
    assert isinstance(model, ObsDevolucaoRelatorioConsolidadoDRE)
    assert isinstance(model.dre, Unidade)
    assert isinstance(model.periodo, Periodo)
    assert isinstance(model.tipo_conta, TipoConta)
    assert isinstance(model.tipo_devolucao_ao_tesouro, TipoDevolucaoAoTesouro)
    assert model.tipo_devolucao == 'TESOURO'
    assert model.observacao

def test_str_model(obs_devolucao_conta_relatorio_dre_consolidado):
    assert obs_devolucao_conta_relatorio_dre_consolidado.__str__() == 'Teste devolução à conta'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[ObsDevolucaoRelatorioConsolidadoDRE]
