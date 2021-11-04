import json
import pytest

from datetime import date
from model_bakery import baker
from rest_framework import status

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


def test_get_status_presidente_presente(
    jwt_authenticated_client_a,
    associacao_presidente_presente
):
    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/{associacao_presidente_presente.uuid}/status-presidente/',
        content_type='application/json')

    result = json.loads(response.content)

    esperado = {
                   'status_presidente': 'PRESENTE',
                   'cargo_substituto_presidente_ausente': None,
               }

    assert response.status_code == status.HTTP_200_OK

    assert result == esperado


def test_get_status_presidente_ausente(
    jwt_authenticated_client_a,
    associacao_presidente_ausente
):
    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/{associacao_presidente_ausente.uuid}/status-presidente/',
        content_type='application/json')

    result = json.loads(response.content)

    esperado = {
                   'status_presidente': 'AUSENTE',
                   'cargo_substituto_presidente_ausente': 'VICE_PRESIDENTE_DIRETORIA_EXECUTIVA',
               }

    assert response.status_code == status.HTTP_200_OK

    assert result == esperado
