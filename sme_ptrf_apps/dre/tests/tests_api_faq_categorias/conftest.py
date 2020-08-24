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
