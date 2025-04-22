
import json

import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import TipoConta, Unidade
from sme_ptrf_apps.receitas.models import TipoReceita, DetalheTipoReceita


pytestmark = pytest.mark.django_db


def test_post_sucesso(jwt_authenticated_client_p, tipo_conta, dre_ipiranga, detalhe_tipo_receita): 
    payload = {
        "unidades": [str(dre_ipiranga.uuid)],
        "tipos_conta": [str(tipo_conta.uuid)],
        "detalhes": [detalhe_tipo_receita.id],
        "nome": "Tipo receita 001"
    }
    response = jwt_authenticated_client_p.post(f'/api/tipos-receitas/',
                                              content_type='application/json',
                                              data=json.dumps(payload))
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED
    assert TipoReceita.objects.count() == 2
    assert TipoReceita.objects.filter(nome="Tipo receita 001").exists() is True


def test_post_sucesso_002_sem_detalhes(jwt_authenticated_client_p, tipo_conta, dre_ipiranga, detalhe_tipo_receita): 
    payload = {
        "tipos_conta": [str(tipo_conta.uuid)],
        "unidades": [str(dre_ipiranga.uuid)],
        "nome": "Tipo receita 001"
    }
    response = jwt_authenticated_client_p.post(f'/api/tipos-receitas/',
                                              content_type='application/json',
                                              data=json.dumps(payload))
    content = json.loads(response.content)
    assert response.status_code == status.HTTP_201_CREATED
    assert TipoReceita.objects.count() == 2
    assert TipoReceita.objects.filter(nome="Tipo receita 001").exists() is True


def test_post_erro_payload(jwt_authenticated_client_p, tipo_conta, dre_ipiranga, detalhe_tipo_receita): 
    payload = {
        "unidades": [str(dre_ipiranga.uuid)],
        "detalhes": [detalhe_tipo_receita.id],
        "nome": "Tipo receita 001"
    }
    response = jwt_authenticated_client_p.post(f'/api/tipos-receitas/',
                                              content_type='application/json',
                                              data=json.dumps(payload))
    content = json.loads(response.content)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert content == {'tipos_conta': ['This field is required.']}


def test_post_erro_payload_nome_duplicado(jwt_authenticated_client_p, tipo_conta, dre_ipiranga, detalhe_tipo_receita): 
    payload = {
        "tipos_conta": [str(tipo_conta.uuid)],
        "unidades": [str(dre_ipiranga.uuid)],
        "detalhes": [detalhe_tipo_receita.id],
        "nome": "Estorno"
    }
    response = jwt_authenticated_client_p.post(f'/api/tipos-receitas/',
                                              content_type='application/json',
                                              data=json.dumps(payload))
    content = json.loads(response.content)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert content == {'non_field_errors': 'Este Tipo de Receita já existe.'}
