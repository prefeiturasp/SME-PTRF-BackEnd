import pytest
from datetime import date
from django.contrib.admin.sites import site

from sme_ptrf_apps.situacao_patrimonial.admin import BemProduzidoAdmin, BemProduzidoRateioAdmin, BemProduzidoDespesaAdmin
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido, BemProduzidoDespesa, BemProduzidoRateio


@pytest.fixture
def periodo_2024_1(periodo_factory):
    return periodo_factory.create(
        referencia='2024.1',
        data_inicio_realizacao_despesas=date(2024, 1, 1),
        data_fim_realizacao_despesas=date(2024, 4, 30),
    )


@pytest.fixture
def periodo_2025_1(periodo_factory):
    return periodo_factory.create(
        referencia='2025.1',
        data_inicio_realizacao_despesas=date(2025, 1, 1),
        data_fim_realizacao_despesas=date(2025, 4, 30),
    )


@pytest.fixture
def flag_situacao_patrimonial(flag_factory):
    return flag_factory.create(name='situacao-patrimonial')


@pytest.fixture
def bem_produzido_admin():
    return BemProduzidoAdmin(model=BemProduzido, admin_site=site)


@pytest.fixture
def bem_produzido_despesa_admin():
    return BemProduzidoDespesaAdmin(model=BemProduzidoDespesa, admin_site=site)


@pytest.fixture
def bem_produzido_rateio_admin():
    return BemProduzidoRateioAdmin(model=BemProduzidoRateio, admin_site=site)


@pytest.fixture
def associacao_1(associacao_factory):
    return associacao_factory.create()


@pytest.fixture
def despesa_1(despesa_factory, associacao_1):
    return despesa_factory.create(associacao=associacao_1)


@pytest.fixture
def rateio_capital_1(rateio_despesa_factory, associacao_1, despesa_1):
    return rateio_despesa_factory.create(associacao=associacao_1, despesa=despesa_1, valor_rateio=200.0, aplicacao_recurso="CAPITAL")


@pytest.fixture
def rateio_custeio_1(rateio_despesa_factory, associacao_1, despesa_1):
    return rateio_despesa_factory.create(associacao=associacao_1, despesa=despesa_1, valor_rateio=200.0, aplicacao_recurso="CUSTEIO")


@pytest.fixture
def rateio_1(rateio_despesa_factory, associacao_1, despesa_1):
    return rateio_despesa_factory.create(associacao=associacao_1, despesa=despesa_1, valor_rateio=200.0)


@pytest.fixture
def bem_produzido_1(bem_produzido_factory, associacao_1):
    return bem_produzido_factory.create(associacao=associacao_1)


@pytest.fixture
def bem_produzido_despesa_1(bem_produzido_despesa_factory, bem_produzido_1, despesa_1):
    return bem_produzido_despesa_factory.create(bem_produzido=bem_produzido_1, despesa=despesa_1)


@pytest.fixture
def bem_produzido_rateio_1(bem_produzido_rateio_factory, rateio_1, bem_produzido_despesa_1):
    return bem_produzido_rateio_factory.create(bem_produzido_despesa=bem_produzido_despesa_1, rateio=rateio_1, valor_utilizado=120.0)


@pytest.fixture
def associacao_2(associacao_factory):
    return associacao_factory.create()


@pytest.fixture
def despesa_2(despesa_factory, associacao_2):
    return despesa_factory.create(associacao=associacao_2)


@pytest.fixture
def despesa_3(despesa_factory, associacao_2):
    return despesa_factory.create(associacao=associacao_2)


@pytest.fixture
def despesa_4(despesa_factory, associacao_2):
    return despesa_factory.create(associacao=associacao_2)


@pytest.fixture
def bem_produzido_2(bem_produzido_factory, associacao_2):
    return bem_produzido_factory.create(associacao=associacao_2)


@pytest.fixture
def bem_produzido_despesa_2(bem_produzido_despesa_factory, bem_produzido_2, despesa_2):
    return bem_produzido_despesa_factory.create(bem_produzido=bem_produzido_2, despesa=despesa_2)


@pytest.fixture
def bem_produzido_despesa_3(bem_produzido_despesa_factory, bem_produzido_2, despesa_3):
    return bem_produzido_despesa_factory.create(bem_produzido=bem_produzido_2, despesa=despesa_3)


@pytest.fixture
def bem_produzido_despesa_4(bem_produzido_despesa_factory, bem_produzido_2, despesa_4):
    return bem_produzido_despesa_factory.create(bem_produzido=bem_produzido_2, despesa=despesa_4)


@pytest.fixture
def especificacao_material_servico_1(especificacao_material_servico_factory):
    return especificacao_material_servico_factory.create(
        descricao="Especificação do Bem Produzido 1",
        uuid="1487c2e8-ff06-42d7-8115-33e036aaf6cc"
    )


@pytest.fixture
def bem_produzido_item_1(bem_produzido_item_factory, bem_produzido_1, despesa_1, especificacao_material_servico_1):
    return bem_produzido_item_factory.create(bem_produzido=bem_produzido_1, especificacao_do_bem=especificacao_material_servico_1)
