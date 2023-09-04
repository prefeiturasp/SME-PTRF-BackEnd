import json

import pytest
from rest_framework import status

from ...models import Associacao, Unidade

pytestmark = pytest.mark.django_db


def test_api_get_associacoes_tabelas(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get('/api/associacoes/tabelas/', content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'tipos_unidade': Unidade.tipos_unidade_to_json(),
        'dres': Unidade.dres_to_json(),
        'filtro_informacoes': Associacao.filtro_informacoes_to_json()
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado

def test_api_get_associacoes_tabelas_filtro_dre(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get('/api/associacoes/tabelas/?filtros_informacoes_associacao_dre=True', content_type='application/json')
    result = json.loads(response.content)

    esperado = Associacao.filtro_informacoes_dre_to_json()

    assert response.status_code == status.HTTP_200_OK
    assert result['filtro_informacoes'] == esperado