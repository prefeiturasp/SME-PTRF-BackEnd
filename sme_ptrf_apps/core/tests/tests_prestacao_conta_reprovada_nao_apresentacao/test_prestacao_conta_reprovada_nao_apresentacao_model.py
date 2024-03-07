import pytest
from django.contrib import admin
from datetime import date
from ...models import PrestacaoContaReprovadaNaoApresentacao, Associacao, Periodo

pytestmark = pytest.mark.django_db


def test_instance_model(prestacao_conta_reprovada_nao_apresentacao_factory):
    model = prestacao_conta_reprovada_nao_apresentacao_factory.create()

    assert isinstance(model, PrestacaoContaReprovadaNaoApresentacao)
    assert isinstance(model.associacao, Associacao)
    assert isinstance(model.periodo, Periodo)
    assert model.data_de_reprovacao
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_srt_model(prestacao_conta_reprovada_nao_apresentacao_factory, periodo_factory):
    periodo = periodo_factory.create(
        data_inicio_realizacao_despesas=date(2024, 1, 1),
        data_fim_realizacao_despesas=date(2024, 6, 1),
        referencia='2024.1',
    )
    model = prestacao_conta_reprovada_nao_apresentacao_factory.create(
        periodo=periodo
    )
    assert model.__str__() == '2024.1 - 2024-01-01 a 2024-06-01'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[PrestacaoContaReprovadaNaoApresentacao]
