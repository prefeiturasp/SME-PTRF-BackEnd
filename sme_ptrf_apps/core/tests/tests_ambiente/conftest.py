import pytest
from model_bakery import baker

pytestmark = pytest.mark.django_db


@pytest.fixture
def ambiente_dev():
    return baker.make(
        'Ambiente',
        prefixo='dev',
        nome='Desenvolvimento'
    )


@pytest.fixture
def ambiente_hom():
    return baker.make(
        'Ambiente',
        prefixo='hom',
        nome='Homologação'
    )
