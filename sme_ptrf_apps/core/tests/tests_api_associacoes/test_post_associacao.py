import json

import pytest

from rest_framework import status
from sme_ptrf_apps.core.models import Associacao, Unidade

from freezegun import freeze_time

pytestmark = pytest.mark.django_db


def test_api_post_associacao(jwt_authenticated_client_a, periodo_anterior):
    payload = {
        "nome": "Nome alterado",
        "cnpj": '52.302.275/0001-83',
        "periodo_inicial": str(periodo_anterior.uuid),
        "ccm": '0.000.00-0',
        "email": "ollyverottoboni@gmail.com",
        "processo_regularidade": '123456',
        "unidade": {
            'codigo_eol': "786543",
            'nome': 'Unidade Nova',
            'email': 'unidadenova@gmail.com',
            'telefone': '11992735056',
            'numero': '89',
            'tipo_logradouro': 'Rua',
            'logradouro': 'Flamengo',
            'bairro': 'Ferreira',
            'cep': '05524160'
        }
    }
    response = jwt_authenticated_client_a.post(f'/api/associacoes/', data=json.dumps(payload),
                          content_type='application/json')

    registro_alterado = Associacao.objects.first()

    assert response.status_code == status.HTTP_201_CREATED
    assert registro_alterado.uuid
    assert registro_alterado.unidade.uuid


def test_api_post_associacao_deve_gerar_erro_data_de_encerramento_maior_que_periodo_inicial_data_fim_realizacao_despesas(
    jwt_authenticated_client_a,
    periodo_anterior
):
    with pytest.raises(Exception) as excinfo:
        payload = {
            "nome": "Nome alterado",
            "cnpj": '52.302.275/0001-83',
            "periodo_inicial": str(periodo_anterior.uuid),
            "data_de_encerramento": "2019-08-29",
            "ccm": '0.000.00-0',
            "email": "ollyverottoboni@gmail.com",
            "processo_regularidade": '123456',
            "unidade": {
                'codigo_eol': "786543",
                'nome': 'Unidade Nova',
                'email': 'unidadenova@gmail.com',
                'telefone': '11992735056',
                'numero': '89',
                'tipo_logradouro': 'Rua',
                'logradouro': 'Flamengo',
                'bairro': 'Ferreira',
                'cep': '05524160'
            }
        }
        response = jwt_authenticated_client_a.post(f'/api/associacoes/', data=json.dumps(payload),
                                                   content_type='application/json')
    assert excinfo.typename == 'ValidationError'

    assert excinfo.value.messages[0] == 'Data de encerramento não pode ser menor que data_fim_realizacao_despesas do período inicial'


@freeze_time('2023-04-18')
def test_api_post_associacao_deve_gerar_erro_data_de_encerramento_maior_que_data_de_hoje(
    jwt_authenticated_client_a,
    periodo_anterior
):
    with pytest.raises(Exception) as excinfo:
        payload = {
            "nome": "Nome alterado",
            "cnpj": '52.302.275/0001-83',
            "periodo_inicial": str(periodo_anterior.uuid),
            "data_de_encerramento": "2023-04-19",
            "ccm": '0.000.00-0',
            "email": "ollyverottoboni@gmail.com",
            "processo_regularidade": '123456',
            "unidade": {
                'codigo_eol': "786543",
                'nome': 'Unidade Nova',
                'email': 'unidadenova@gmail.com',
                'telefone': '11992735056',
                'numero': '89',
                'tipo_logradouro': 'Rua',
                'logradouro': 'Flamengo',
                'bairro': 'Ferreira',
                'cep': '05524160'
            }
        }
        response = jwt_authenticated_client_a.post(f'/api/associacoes/', data=json.dumps(payload),
                                                   content_type='application/json')
    assert excinfo.typename == 'ValidationError'

    assert excinfo.value.messages[0] == 'Data de encerramento não pode ser maior que a data de Hoje'

