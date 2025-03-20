import json

import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import TipoConta, Unidade


pytestmark = pytest.mark.django_db


def test_get_sucesso(jwt_authenticated_client_p, tipo_receita_estorno):
    response = jwt_authenticated_client_p.get(f'/api/tipos-receitas/',
                                              content_type='application/json')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 1
    assert content["count"] == 1
    assert content["results"][0]["nome"] == "Estorno"


def test_get_sem_filtros(jwt_authenticated_client_p, tipo_receita_estorno, tipo_receita_repasse):
    response = jwt_authenticated_client_p.get(f'/api/tipos-receitas/',
                                              content_type='application/json')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 2
    assert content["count"] == 2


def test_get_sucesso(jwt_authenticated_client_p, tipo_receita_estorno, tipo_receita_repasse):
    response = jwt_authenticated_client_p.get(f'/api/tipos-receitas/?nome=Estorno',
                                              content_type='application/json')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 1
    assert content["count"] == 1
    assert content["results"][0]["nome"] == "Estorno"
    

def test_get_sem_registros(jwt_authenticated_client_p, tipo_receita_estorno, tipo_receita_repasse):
    response = jwt_authenticated_client_p.get(f'/api/tipos-receitas/?nome=Nome123',
                                              content_type='application/json')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 0
    assert content["count"] == 0


def test_get_tipo_conta(jwt_authenticated_client_p, tipo_receita_estorno, tipo_receita_repasse):
    tipo_conta = TipoConta.objects.filter(nome='Cheque').first()
    response = jwt_authenticated_client_p.get(f'/api/tipos-receitas/?tipos_conta__uuid={tipo_conta.uuid}',
                                              content_type='application/json')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 2
    assert content["count"] == 2


def test_get_e_repasse(jwt_authenticated_client_p, tipo_receita_estorno, tipo_receita_repasse):
    response = jwt_authenticated_client_p.get(f'/api/tipos-receitas/?e_repasse=0',
                                              content_type='application/json')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 1
    assert content["count"] == 1


def test_get_aceita_capital(jwt_authenticated_client_p, tipo_receita_estorno, tipo_receita_repasse):
    response = jwt_authenticated_client_p.get(f'/api/tipos-receitas/?aceita_capital=1',
                                              content_type='application/json')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 1
    assert content["count"] == 1


def test_get_unidade(jwt_authenticated_client_p, tipo_receita_estorno, tipo_receita_repasse):
    unidade = Unidade.objects.filter(codigo_eol='108600').first()
    response = jwt_authenticated_client_p.get(f'/api/tipos-receitas/?unidades__uuid={unidade.uuid}',
                                              content_type='application/json')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 2
    assert content["count"] == 2


def test_get_unidade_002(jwt_authenticated_client_p, tipo_receita_estorno, tipo_receita_repasse):
    unidade = Unidade.objects.filter(codigo_eol='99999').first()
    response = jwt_authenticated_client_p.get(f'/api/tipos-receitas/?unidades__uuid={unidade.uuid}',
                                              content_type='application/json')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 1
    assert content["count"] == 1
