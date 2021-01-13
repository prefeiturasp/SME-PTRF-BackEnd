import pytest

from model_bakery import baker


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
def unidade_bravo(dre_alfa):
    return baker.make(
        'Unidade',
        codigo_eol="000086",
        tipo_unidade="EMEI",
        nome="Bravo",
        sigla="",
        dre=dre_alfa,
    )


@pytest.fixture
def associacao_charli(unidade_bravo, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Charli',
        cnpj='52.302.275/0001-83',
        unidade=unidade_bravo,
        periodo_inicial=periodo_anterior,
    )


@pytest.fixture
def acao_associacao_charli_x(associacao_charli, acao_x):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao_charli,
        acao=acao_x
    )


@pytest.fixture
def acao_associacao_charli_y(associacao_charli, acao_y):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao_charli,
        acao=acao_y
    )


@pytest.fixture
def unidade_delta(dre_alfa):
    return baker.make(
        'Unidade',
        codigo_eol="000087",
        tipo_unidade="EMEI",
        nome="Delta",
        sigla="",
        dre=dre_alfa,
    )


@pytest.fixture
def associacao_eco(unidade_delta, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Eco',
        cnpj='94.175.194/0001-00',
        unidade=unidade_delta,
        periodo_inicial=periodo_anterior,
    )


@pytest.fixture
def acao_associacao_eco_x(associacao_eco, acao_x):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao_eco,
        acao=acao_x
    )
