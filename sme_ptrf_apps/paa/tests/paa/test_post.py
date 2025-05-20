from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import json
import pytest

from rest_framework import status

from sme_ptrf_apps.paa.models import Paa, PeriodoPaa
from sme_ptrf_apps.paa.fixtures.factories.parametro_paa import ParametroPaaFactory
from sme_ptrf_apps.paa.fixtures.factories.paa import PaaFactory
from sme_ptrf_apps.paa.fixtures.factories.periodo_paa import PeriodoPaaFactory


pytestmark = pytest.mark.django_db


def test_create_sucesso_mes_elaboracao_atual(jwt_authenticated_client_sme, flag_paa, associacao):
    PeriodoPaaFactory.create(referencia="Periodo Teste",
                                      data_inicial=date.today() - timedelta(weeks=5),
                                      data_final=date.today() + timedelta(weeks=5))
    ParametroPaaFactory.create(mes_elaboracao_paa=date.today().month)
    payload = {
        "associacao": str(associacao.uuid),
    }
    response = jwt_authenticated_client_sme.post('/api/paa/',
                                                 content_type='application/json',
                                                 data=json.dumps(payload))

    assert response.status_code == status.HTTP_201_CREATED, response.content
    paa = Paa.objects.all()
    assert len(paa) == 1


def test_create_mes_nao_liberado_para_elaboracao(jwt_authenticated_client_sme, flag_paa, associacao):
    ParametroPaaFactory.create(mes_elaboracao_paa=date.today().month+1)
    payload = {
        "associacao": str(associacao.uuid),
    }
    response = jwt_authenticated_client_sme.post('/api/paa/',
                                                 content_type='application/json',
                                                 data=json.dumps(payload))
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.content
    paa = Paa.objects.all()
    assert len(paa) == 0
    assert content['non_field_errors'] == ["Mês não liberado para Elaboração de novo PAA."]


def test_create_mes_nao_definido_em_parametro(jwt_authenticated_client_sme, flag_paa, associacao):
    payload = {
        "associacao": str(associacao.uuid),
    }
    response = jwt_authenticated_client_sme.post('/api/paa/',
                                                 content_type='application/json',
                                                 data=json.dumps(payload))
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.content
    paa = Paa.objects.all()
    assert len(paa) == 0
    assert content['non_field_errors'] == [("Nenhum parâmetro de mês para Elaboração de "
                                            "Novo PAA foi definido no Admin.")]


def test_create_duplicado(jwt_authenticated_client_sme, flag_paa, paa, associacao):
    ParametroPaaFactory.create(mes_elaboracao_paa=date.today().month)
    payload = {
        "associacao": str(associacao.uuid),
    }
    response = jwt_authenticated_client_sme.post('/api/paa/',
                                                 content_type='application/json',
                                                 data=json.dumps(payload))
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.content
    paa = Paa.objects.all()
    assert len(paa) == 1
    assert content['non_field_errors'] == [("Já existe um PAA para a Associação informada.")]


def test_create_sem_periodo_vigente_encontrado(jwt_authenticated_client_sme, flag_paa, associacao):
    assert PeriodoPaa.objects.count() == 0
    ParametroPaaFactory.create(mes_elaboracao_paa=date.today().month)
    payload = {
        "associacao": str(associacao.uuid),
    }
    response = jwt_authenticated_client_sme.post('/api/paa/',
                                                content_type='application/json',
                                                data=json.dumps(payload))
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.content
    assert content['non_field_errors'] == ['Nenhum Período vigente foi encontrado.']