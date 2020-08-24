import pytest
from model_bakery import baker

@pytest.fixture
def cat_01():
    return baker.make(
        'FaqCategoria',
        nome='Geral'
    )


@pytest.fixture
def cat_02():
    return baker.make(
        'FaqCategoria',
        nome='Associações'
    )

@pytest.fixture
def faq_01(cat_01):
    return baker.make(
        'Faq',
        pergunta='Pergunta 01 - Cat Geral 01',
        resposta='Esta é a resposta da Pergunta 01',
        categoria=cat_01
    )


@pytest.fixture
def faq_02(cat_02):
    return baker.make(
        'Faq',
        pergunta='Pergunta 02 - Cat Associações 01',
        resposta='Esta é a resposta da Pergunta 02',
        categoria=cat_02
    )


@pytest.fixture
def cat_com_uuid():
    return baker.make(
        'FaqCategoria',
        uuid="aa82b8df-a62a-4e13-92d4-bb5e3a72be70",
        nome='Geral'
    )
