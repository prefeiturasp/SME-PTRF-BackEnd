import pytest
from datetime import date
from ...models import ReceitaPrevistaOutroRecursoPeriodo
from ...admin import ReceitaPrevistaOutroRecursoPeriodoAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def receitas_previstas_outros_recursos_periodo_admin():
    return ReceitaPrevistaOutroRecursoPeriodoAdmin(
        model=ReceitaPrevistaOutroRecursoPeriodo, admin_site=site)


@pytest.fixture
def outro_recurso_periodo(periodo_paa_factory, outro_recurso_factory, outro_recurso_periodo_factory):
    periodo_paa = periodo_paa_factory.create(
        referencia='2000.11',
        data_inicial=date(2000, 1, 1),
        data_final=date(2000, 4, 30),
    )
    outro_recurso = outro_recurso_factory.create(nome='Teste I')
    return outro_recurso_periodo_factory.create(
        outro_recurso=outro_recurso,
        periodo_paa=periodo_paa,
        ativo=True
    )


@pytest.fixture
def receita_prevista_outro_recurso_periodo(
        receita_prevista_outro_recurso_periodo_factory,
        outro_recurso_periodo):

    return receita_prevista_outro_recurso_periodo_factory.create(
        outro_recurso_periodo=outro_recurso_periodo,
        previsao_valor_custeio=101,
        previsao_valor_capital=102,
        previsao_valor_livre=103
    )
