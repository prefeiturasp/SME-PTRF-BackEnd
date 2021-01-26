import pytest

from model_bakery import baker
from datetime import date


@pytest.fixture
def acao_x():
    return baker.make('Acao', nome='X')


@pytest.fixture
def acao_y():
    return baker.make('Acao', nome='Y')


@pytest.fixture
def dre_alfa():
    return baker.make(
        'Unidade',
        codigo_eol='108500',
        tipo_unidade='DRE',
        nome='Alfa',
        sigla='A'
    )


@pytest.fixture
def unidade_bravo_000086(dre_alfa):
    return baker.make(
        'Unidade',
        codigo_eol="000086",
        tipo_unidade="EMEI",
        nome="Bravo",
        sigla="",
        dre=dre_alfa,
    )


@pytest.fixture
def associacao_charli_bravo_000086(unidade_bravo_000086, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Charli',
        cnpj='52.302.275/0001-83',
        unidade=unidade_bravo_000086,
        periodo_inicial=periodo_anterior,
    )


@pytest.fixture
def acao_associacao_charli_bravo_000086_x(associacao_charli_bravo_000086, acao_x):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao_charli_bravo_000086,
        acao=acao_x
    )


@pytest.fixture
def acao_associacao_charli_bravo_000086_y(associacao_charli_bravo_000086, acao_y):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao_charli_bravo_000086,
        acao=acao_y
    )


@pytest.fixture
def unidade_delta_000087(dre_alfa):
    return baker.make(
        'Unidade',
        codigo_eol="000087",
        tipo_unidade="EMEI",
        nome="Delta",
        sigla="",
        dre=dre_alfa,
    )


@pytest.fixture
def associacao_eco_delta_000087(unidade_delta_000087, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Eco',
        cnpj='94.175.194/0001-00',
        unidade=unidade_delta_000087,
        periodo_inicial=periodo_anterior,
    )


@pytest.fixture
def acao_associacao_eco_delta_000087_x(associacao_eco_delta_000087, acao_x):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao_eco_delta_000087,
        acao=acao_x
    )


@pytest.fixture
def acao_associacao_eco_delta_000087_y_inativa(associacao_eco_delta_000087, acao_y):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao_eco_delta_000087,
        acao=acao_y,
        status='INATIVA'
    )


@pytest.fixture
def conta_associacao_eco_delta(associacao_eco_delta_000087, tipo_conta):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao_eco_delta_000087,
        tipo_conta=tipo_conta,
        banco_nome='Banco do Brasil',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='534653264523'
    )


@pytest.fixture
def receita_usando_acao_associacao_eco_delta_x(
    acao_associacao_eco_delta_000087_x,
    conta_associacao_eco_delta,
    tipo_receita,
    detalhe_tipo_receita
):
    return baker.make(
        'Receita',
        associacao=acao_associacao_eco_delta_000087_x.associacao,
        data=date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao_eco_delta,
        acao_associacao=acao_associacao_eco_delta_000087_x,
        tipo_receita=tipo_receita,
        categoria_receita='CUSTEIO',
        detalhe_tipo_receita=detalhe_tipo_receita,
    )
