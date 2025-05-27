import pytest
from model_bakery import baker
from ...models import ReceitaPrevistaPdde
from ...admin import ReceitaPrevistaPddeAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def receitas_previstas_pdde_admin():
    return ReceitaPrevistaPddeAdmin(model=ReceitaPrevistaPdde, admin_site=site)


@pytest.fixture
def receita_prevista_pdde(paa, acao_pdde):
    return baker.make(
        'ReceitaPrevistaPdde',
        paa=paa,
        acao_pdde=acao_pdde,
        previsao_valor_custeio=1000.,
        previsao_valor_capital=1000.,
        previsao_valor_livre=1000.,
        saldo_custeio=1000.,
        saldo_capital=1000.,
        saldo_livre=1000.,
    )


@pytest.fixture
def receita_prevista_pdde_sem_acao(paa):
    return baker.make(
        'ReceitaPrevistaPdde',
        paa=paa,
        acao_pdde=None,
        previsao_valor_custeio=1000.,
        previsao_valor_capital=1000.,
        previsao_valor_livre=1000.,
        saldo_custeio=1000.,
        saldo_capital=1000.,
        saldo_livre=1000.,
    )
