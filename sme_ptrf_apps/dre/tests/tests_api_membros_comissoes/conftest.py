import pytest

from model_bakery import baker


@pytest.fixture
def dre_x():
    return baker.make('Unidade', codigo_eol='812345', tipo_unidade='DRE', nome='X', sigla='X')


@pytest.fixture
def dre_y():
    return baker.make('Unidade', codigo_eol='912345', tipo_unidade='DRE', nome='Y', sigla='Y')


@pytest.fixture
def comissao_a():
    return baker.make('Comissao', nome='A')


@pytest.fixture
def comissao_b():
    return baker.make('Comissao', nome='B')


@pytest.fixture
def membro_beto_comissao_a_b_dre_x(comissao_a, comissao_b, dre_x):
    membro = baker.make(
        'MembroComissao',
        rf='123456',
        nome='Beto',
        cargo='teste',
        email='beto@teste.com',
        dre=dre_x,
        comissoes=[comissao_a, comissao_b]
    )
    return membro


@pytest.fixture
def membro_alex_comissao_a_dre_x(comissao_a, dre_x):
    membro = baker.make(
        'MembroComissao',
        rf='123457',
        nome='Alex',
        cargo='teste',
        email='alex@teste.com',
        dre=dre_x,
        comissoes=[comissao_a, ]
    )
    return membro


@pytest.fixture
def membro_jose_comissao_a_b_dre_y(comissao_a, comissao_b, dre_y):
    membro = baker.make(
        'MembroComissao',
        rf='123458',
        nome='José',
        cargo='teste',
        email='ze@teste.com',
        dre=dre_y,
        comissoes=[comissao_a, comissao_b]
    )
    return membro
