import datetime
import pytest

from model_bakery import baker

pytestmark = pytest.mark.django_db


@pytest.fixture
def u_dre():
    return baker.make('Unidade',
                      codigo_eol='99999',
                      tipo_unidade='DRE',
                      nome='DRE teste',
                      sigla='TT',
                      criado_em=datetime.datetime.now())
