import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from ...models import ConsolidadoDRE, Lauda
from sme_ptrf_apps.core.models import Unidade, Periodo, TipoConta

pytestmark = pytest.mark.django_db


def test_instance_model(
    lauda_teste_model_lauda,
    consolidado_dre_teste_model_lauda,
    dre_teste_model_lauda,
    periodo_teste_model_lauda,
    tipo_conta_cartao_teste_model_lauda,
    usuario_dre_teste_lauda_model
):
    model = lauda_teste_model_lauda
    assert isinstance(model, Lauda)
    assert isinstance(model.consolidado_dre, ConsolidadoDRE)
    assert isinstance(model.dre, Unidade)
    assert isinstance(model.periodo, Periodo)
    assert isinstance(model.tipo_conta, TipoConta)
    assert isinstance(model.usuario, get_user_model())
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert not model.arquivo_lauda_txt
    assert model.dre
    assert model.periodo
    assert model.tipo_conta
    assert model.usuario
    assert model.status


def test_str_model(lauda_teste_model_lauda):
    assert lauda_teste_model_lauda.__str__() == 'Lauda não gerada'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Lauda]
