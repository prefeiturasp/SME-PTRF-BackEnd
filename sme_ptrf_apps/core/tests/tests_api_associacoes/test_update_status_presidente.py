import json
import pytest

from datetime import date
from rest_framework import status
from model_bakery import baker

from ...models import Associacao

pytestmark = pytest.mark.django_db

@pytest.fixture
def periodo_2019_1():
    return baker.make(
        'Periodo',
        referencia='2019.1',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 6, 30),
        periodo_anterior=None
    )


@pytest.fixture
def associacao_presidente_presente(unidade, periodo_2019_1):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-83',
        unidade=unidade,
        periodo_inicial=periodo_2019_1,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456',
        status_presidente='PRESENTE',
        cargo_substituto_presidente_ausente=None,
    )


@pytest.fixture
def associacao_presidente_ausente(unidade, periodo_2019_1):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-83',
        unidade=unidade,
        periodo_inicial=periodo_2019_1,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456',
        status_presidente='AUSENTE',
        cargo_substituto_presidente_ausente='VICE_PRESIDENTE_DIRETORIA_EXECUTIVA',
    )


def test_update_status_presidente_para_ausente(jwt_authenticated_client_a, associacao_presidente_presente):
    payload = {
        "status_presidente": "AUSENTE",
        "cargo_substituto_presidente_ausente": "VICE_PRESIDENTE_DIRETORIA_EXECUTIVA"
    }

    response = jwt_authenticated_client_a.patch(
        f'/api/associacoes/{associacao_presidente_presente.uuid}/update-status-presidente/',
        data=json.dumps(payload),
        content_type='application/json')

    registro_alterado = Associacao.objects.get(uuid=associacao_presidente_presente.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert registro_alterado.status_presidente == "AUSENTE"
    assert registro_alterado.cargo_substituto_presidente_ausente == "VICE_PRESIDENTE_DIRETORIA_EXECUTIVA"


def test_update_status_presidente_para_presente(jwt_authenticated_client_a, associacao_presidente_ausente):
    payload = {
        "status_presidente": "PRESENTE",
        "cargo_substituto_presidente_ausente": None
    }

    response = jwt_authenticated_client_a.patch(
        f'/api/associacoes/{associacao_presidente_ausente.uuid}/update-status-presidente/',
        data=json.dumps(payload),
        content_type='application/json')

    registro_alterado = Associacao.objects.get(uuid=associacao_presidente_ausente.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert registro_alterado.status_presidente == 'PRESENTE'
    assert registro_alterado.cargo_substituto_presidente_ausente is None
