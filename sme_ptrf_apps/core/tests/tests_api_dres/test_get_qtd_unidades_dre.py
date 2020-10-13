import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def _dre1():
    return baker.make(
        'Unidade',
        codigo_eol='000001',
        tipo_unidade='DRE',
        nome='Dre1',
        sigla='D1'
    )

@pytest.fixture
def _dre2():
    return baker.make(
        'Unidade',
        codigo_eol='000002',
        tipo_unidade='DRE',
        nome='Dre2',
        sigla='D2'
    )

@pytest.fixture
def _unidade1_dre_1(_dre1):
    return baker.make(
        'Unidade',
        codigo_eol="000003",
        tipo_unidade="EMEI",
        nome="A",
        dre=_dre1,
    )

@pytest.fixture
def _unidade2_dre_1(_dre1):
    return baker.make(
        'Unidade',
        codigo_eol="000004",
        tipo_unidade="EMEI",
        nome="B",
        dre=_dre1,
    )

@pytest.fixture
def _unidade3_dre_2(_dre2):
    return baker.make(
        'Unidade',
        codigo_eol="000005",
        tipo_unidade="EMEI",
        nome="C",
        dre=_dre2,
    )

def test_api_retrieve_dre(client, _dre1, _dre2, _unidade1_dre_1, _unidade2_dre_1, _unidade3_dre_2):
    response = client.get(f'/api/dres/{_dre1.uuid}/qtd-unidades/', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = {
        "uuid": f'{_dre1.uuid}',
        "qtd_unidades": 2,
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado
