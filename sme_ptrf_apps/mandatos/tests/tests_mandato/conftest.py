from datetime import date
import pytest
from model_bakery import baker
from ...models import Mandato

pytestmark = pytest.mark.django_db

@pytest.fixture
def mandato_2023_a_2025():
    return baker.make(
        'Mandato',
        referencia_mandato='2023 a 2025',
        data_inicial=date(2023, 7, 19),
        data_final=date(2023, 7, 20),
    )
