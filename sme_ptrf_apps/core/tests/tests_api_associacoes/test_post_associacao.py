import json
import pytest

from rest_framework import status
from sme_ptrf_apps.core.models import Associacao, Unidade

pytestmark = pytest.mark.django_db


def test_api_post_associacao(jwt_authenticated_client_a, periodo_anterior):
    payload = {
        "nome": "Nome alterado",
        "processo_regularidade": "123456",
        "nome": 'Escola Teste',
        "cnpj": '52.302.275/0001-83',
        "periodo_inicial": periodo_anterior.id,
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

    print(registro_alterado)
    print(registro_alterado.unidade)
    assert response.status_code == status.HTTP_201_CREATED
    assert registro_alterado.uuid
    assert registro_alterado.unidade.uuid
