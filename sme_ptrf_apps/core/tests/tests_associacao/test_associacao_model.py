import pytest
from django.contrib import admin

from ...models import Associacao
from ....core.models import Unidade, Periodo
from waffle.testutils import override_flag

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


def test_get_associacoes_ativas_no_periodo_deve_desconsiderar_associacoes_nao_iniciadas(
    associacao_iniciada_2020_1,
    associacao_iniciada_2020_2,
    outra_associacao_sem_periodo_inicial,
    periodo_2020_2,
    dre,
):
    result = Associacao.get_associacoes_ativas_no_periodo(periodo=periodo_2020_2, dre=dre)
    # Quantidade de associações deve ser 1, pois a associacao iniciada em 2020_2 e a associacaoo sem periodo inicial nao devem ser consideradas
    assert len(result) == 1
    assert result[0] == associacao_iniciada_2020_1


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


@override_flag('historico-de-membros', active=True)
def test_get_dados_presidente_composicao_vigente(associacao_factory, mandato_factory, ocupante_cargo_factory, composicao_factory, cargo_composicao_factory):
    from datetime import timedelta

    associacao = associacao_factory.create()
    mandato = mandato_factory.create()
    ocupante_cargo = ocupante_cargo_factory.create()

    composicao = composicao_factory.create(
        mandato=mandato,
        associacao=associacao,
        data_inicial=mandato.data_inicial,
        data_final=mandato.data_inicial + timedelta(days=31)
    )

    cargo_composicao_factory.create(
        composicao=composicao,
        ocupante_do_cargo=ocupante_cargo,
        cargo_associacao='PRESIDENTE_DIRETORIA_EXECUTIVA'
    )

    dados_presidente = associacao.dados_presidente_composicao_vigente()

    assert dados_presidente["nome"] == ocupante_cargo.nome
    assert dados_presidente["cargo_educacao"] == ocupante_cargo.cargo_educacao
    assert dados_presidente["telefone"] == ocupante_cargo.telefone
    assert dados_presidente["email"] == ocupante_cargo.email
    assert dados_presidente["endereco"] == ocupante_cargo.endereco
    assert dados_presidente["bairro"] == ocupante_cargo.bairro
    assert dados_presidente["cep"] == ocupante_cargo.cep


@override_flag('historico-de-membros', active=True)
def test_get_dados_presidente_composicao_vigente_com_composicao_anterior(associacao_factory, mandato_factory, composicao_factory, ocupante_cargo_factory, cargo_composicao_factory):
    from datetime import timedelta, datetime

    associacao = associacao_factory.create()
    mandato = mandato_factory.create(data_inicial=datetime.today() - timedelta(days=60))

    # Criando composicao anterior
    composicao_anterior = composicao_factory.create(
        mandato=mandato,
        associacao=associacao,
        data_inicial=mandato.data_inicial,
        data_final=datetime.today() - timedelta(days=1)
    )

    ocupante_cargo_anterior = ocupante_cargo_factory.create()

    cargo_composicao_factory.create(
        composicao=composicao_anterior,
        ocupante_do_cargo=ocupante_cargo_anterior,
        cargo_associacao='PRESIDENTE_DIRETORIA_EXECUTIVA'
    )

    # Criando composicao vigente
    composicao_vigente = composicao_factory.create(
        mandato=mandato,
        associacao=associacao,
        data_inicial=composicao_anterior.data_final + timedelta(days=1),
        data_final=datetime.today() + timedelta(days=31)
    )

    ocupante_cargo_vigente = ocupante_cargo_factory.create()

    cargo_composicao_factory.create(
        composicao=composicao_vigente,
        ocupante_do_cargo=ocupante_cargo_vigente,
        cargo_associacao='PRESIDENTE_DIRETORIA_EXECUTIVA'
    )

    dados_presidente = associacao.dados_presidente_composicao_vigente()

    assert dados_presidente["nome"] == ocupante_cargo_vigente.nome
    assert dados_presidente["cargo_educacao"] == ocupante_cargo_vigente.cargo_educacao
    assert dados_presidente["telefone"] == ocupante_cargo_vigente.telefone
    assert dados_presidente["email"] == ocupante_cargo_vigente.email
    assert dados_presidente["endereco"] == ocupante_cargo_vigente.endereco
    assert dados_presidente["bairro"] == ocupante_cargo_vigente.bairro
    assert dados_presidente["cep"] == ocupante_cargo_vigente.cep


@override_flag('historico-de-membros', active=True)
def test_get_dados_presidente_composicao_vigente_sem_presidente_cadastrado(associacao_factory, mandato_factory, ocupante_cargo_factory, composicao_factory, cargo_composicao_factory):
    from datetime import timedelta

    associacao = associacao_factory.create()
    mandato = mandato_factory.create()
    ocupante_cargo = ocupante_cargo_factory.create()

    composicao = composicao_factory.create(
        mandato=mandato,
        associacao=associacao,
        data_inicial=mandato.data_inicial,
        data_final=mandato.data_inicial + timedelta(days=31)
    )

    cargo_composicao_factory.create(
        composicao=composicao,
        ocupante_do_cargo=ocupante_cargo,
        cargo_associacao='SECRETARIO'
    )

    dados_presidente = associacao.dados_presidente_composicao_vigente()

    assert dados_presidente["nome"] == ''
    assert dados_presidente["cargo_educacao"] == ''
    assert dados_presidente["telefone"] == ''
    assert dados_presidente["email"] == ''
    assert dados_presidente["endereco"] == ''
    assert dados_presidente["bairro"] == ''
    assert dados_presidente["cep"] == ''
