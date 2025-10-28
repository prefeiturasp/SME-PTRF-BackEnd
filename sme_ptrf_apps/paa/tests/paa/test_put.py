from datetime import date, timedelta
import json
import pytest

from rest_framework import status

from sme_ptrf_apps.paa.models import Paa
from sme_ptrf_apps.paa.fixtures.factories.parametro_paa import ParametroPaaFactory
from sme_ptrf_apps.paa.fixtures.factories.periodo_paa import PeriodoPaaFactory


pytestmark = pytest.mark.django_db


def test_update(jwt_authenticated_client_sme, flag_paa, paa_factory, associacao):
    periodo_paa_1 = PeriodoPaaFactory.create(referencia="Periodo Teste",
                                             data_inicial=date.today() - timedelta(weeks=5),
                                             data_final=date.today() + timedelta(weeks=5))
    paa = paa_factory.create(periodo_paa=periodo_paa_1, associacao=associacao)
    ParametroPaaFactory.create(mes_elaboracao_paa=date.today().month)
    payload = {
        "texto_introducao": "Teste texto"
    }
    response = jwt_authenticated_client_sme.patch(f'/api/paa/{paa.uuid}/',
                                                  content_type='application/json',
                                                  data=json.dumps(payload))

    assert response.status_code == status.HTTP_200_OK, response.content
    paa = Paa.objects.first()
    assert paa.texto_introducao == payload["texto_introducao"]


def test_update_texto_conclusao(jwt_authenticated_client_sme, flag_paa, paa_factory, associacao):
    periodo_paa_1 = PeriodoPaaFactory.create(referencia="Periodo Teste",
                                             data_inicial=date.today() - timedelta(weeks=5),
                                             data_final=date.today() + timedelta(weeks=5))
    paa = paa_factory.create(periodo_paa=periodo_paa_1, associacao=associacao)
    ParametroPaaFactory.create(mes_elaboracao_paa=date.today().month)
    payload = {
        "texto_conclusao": "Teste texto conclusão"
    }
    response = jwt_authenticated_client_sme.patch(f'/api/paa/{paa.uuid}/',
                                                  content_type='application/json',
                                                  data=json.dumps(payload))

    assert response.status_code == status.HTTP_200_OK, response.content
    paa = Paa.objects.first()
    assert paa.texto_conclusao == payload["texto_conclusao"]


def test_update_ambos_textos(jwt_authenticated_client_sme, flag_paa, paa_factory, associacao):
    periodo_paa_1 = PeriodoPaaFactory.create(referencia="Periodo Teste",
                                             data_inicial=date.today() - timedelta(weeks=5),
                                             data_final=date.today() + timedelta(weeks=5))
    paa = paa_factory.create(periodo_paa=periodo_paa_1, associacao=associacao)
    ParametroPaaFactory.create(mes_elaboracao_paa=date.today().month)
    payload = {
        "texto_introducao": "Teste texto introdução",
        "texto_conclusao": "Teste texto conclusão"
    }
    response = jwt_authenticated_client_sme.patch(f'/api/paa/{paa.uuid}/',
                                                  content_type='application/json',
                                                  data=json.dumps(payload))

    assert response.status_code == status.HTTP_200_OK, response.content
    paa = Paa.objects.first()
    assert paa.texto_introducao == payload["texto_introducao"]
    assert paa.texto_conclusao == payload["texto_conclusao"]
