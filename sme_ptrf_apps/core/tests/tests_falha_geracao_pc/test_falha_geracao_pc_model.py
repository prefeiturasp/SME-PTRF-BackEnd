import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from ...models import FalhaGeracaoPc, Associacao, Periodo

pytestmark = pytest.mark.django_db


def test_instance_model(
    falha_geracao_pc_teste_falha_geracao_pc_01,
    usuario_dre_teste_falha_geracao_pc,
    associacao_teste_falha_geracao_pc,
    periodo_teste_falha_geracao_pc,
):
    model = falha_geracao_pc_teste_falha_geracao_pc_01
    assert isinstance(model, FalhaGeracaoPc)
    assert isinstance(model.ultimo_usuario, get_user_model())
    assert isinstance(model.associacao, Associacao)
    assert isinstance(model.periodo, Periodo)
    assert model.data_hora_ultima_ocorrencia
    assert model.qtd_ocorrencias_sucessivas
    assert model.resolvido


def test_str_model(
    falha_geracao_pc_teste_falha_geracao_pc_01,
    periodo_teste_falha_geracao_pc,
):
    assert falha_geracao_pc_teste_falha_geracao_pc_01.__str__() == f"Período {periodo_teste_falha_geracao_pc.referencia}"


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[FalhaGeracaoPc]
