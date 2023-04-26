import pytest
from django.contrib import admin

from ...models import Associacao
from ....core.models import Unidade, Periodo

pytestmark = pytest.mark.django_db


def test_instance_model(associacao):
    model = associacao
    assert isinstance(model, Associacao)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.cnpj
    assert isinstance(model.unidade, Unidade)
    assert isinstance(model.periodo_inicial, Periodo)
    assert model.ccm
    assert model.email
    assert model.processo_regularidade is not None


def test_instance_model_campos_presidente_ausente(associacao_com_presidente_ausente):
    model = associacao_com_presidente_ausente
    assert model.status_presidente == 'AUSENTE'
    assert model.cargo_substituto_presidente_ausente == 'VICE_PRESIDENTE_DIRETORIA_EXECUTIVA'


def test_srt_model(associacao):
    assert associacao.__str__() == 'Escola Teste'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Associacao]


def test_get_associacoes_ativas_no_periodo_deve_desconsiderar_associacoes_nao_iniciadas_parametro_ativo(
    associacao_iniciada_2020_1,
    associacao_iniciada_2020_2,
    periodo_2020_2,
    parametros_desconsidera_nao_iniciadas,
    dre,
):
    result = Associacao.get_associacoes_ativas_no_periodo(periodo=periodo_2020_2, dre=dre)
    # Quantidade de associações deve ser 1, pois a associacao iniciada em 2020_2 nao deve ser considerada
    assert len(result) == 1
    assert result[0] == associacao_iniciada_2020_1

def test_get_associacoes_ativas_no_periodo_deve_desconsiderar_associacoes_nao_iniciadas_parametro_inativo(
    associacao_iniciada_2020_1,
    associacao_iniciada_2020_2,
    periodo_2020_2,
    parametros_nao_desconsidera_nao_iniciadas,
    dre,
):
    result = Associacao.get_associacoes_ativas_no_periodo(periodo=periodo_2020_2, dre=dre)
    # Quantidade de associações deve ser deve ser 2, pois o parâmetro de desconsiderar associacoes nao iniciadas está inativo
    assert len(result) == 2


def test_get_associacoes_ativas_no_periodo_deve_desconsiderar_associacoes_encerradas(
    associacao_encerrada_2020_1,
    associacao_encerrada_2020_2,
    periodo_2020_2,
    dre,
):
    result = Associacao.get_associacoes_ativas_no_periodo(periodo=periodo_2020_2, dre=dre)
    # Quantidade de associações deve ser 1, pois a associacao encerrada em 2020_1 nao deve ser considerada
    assert len(result) == 1
    assert result[0] == associacao_encerrada_2020_2
