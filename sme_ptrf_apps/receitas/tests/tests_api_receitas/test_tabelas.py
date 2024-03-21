import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

def test_get_tabelas(
    jwt_authenticated_client_p,
    tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    detalhe_tipo_receita
):
    response = jwt_authenticated_client_p.get(
        f'/api/receitas/tabelas/?associacao_uuid={associacao.uuid}', content_type='application/json')
    result = json.loads(response.content)

    """
    'periodos': [{'data_fim_realizacao_despesas': '2019-08-31',
                  'data_inicio_realizacao_despesas': '2019-01-01',
                  'referencia': '2019.1',
                  'referencia_por_extenso': '1° repasse de 2019',
                  'uuid': '8022449b-86b4-4884-a431-6dd352be5c62'}],
    """

    assert response.status_code == status.HTTP_200_OK

    assert len(result['tipos_receita']) == 1
    assert len(result['categorias_receita']) == 3
    assert len(result['acoes_associacao']) == 1
    assert len(result['contas_associacao']) == 1
    assert len(result['periodos']) == 1

def test_get_tabelas_tipos_receita_por_unidade(jwt_authenticated_client_p, associacao_factory, tipo_receita_factory):
    associacao_1 = associacao_factory.create()
    associacao_2 = associacao_factory.create()

    tipo = tipo_receita_factory.create()
    tipo.unidades.set([associacao_1.unidade], clear=True)

    tipo_2 = tipo_receita_factory.create()
    tipo_2.unidades.set([associacao_2.unidade], clear=True)

    response = jwt_authenticated_client_p.get(
        f'/api/receitas/tabelas/?associacao_uuid={associacao_1.uuid}', content_type='application/json')
    result = json.loads(response.content)

    assert len(result['tipos_receita']) == 1
    assert result['tipos_receita'][0]['nome'] == tipo.nome
    assert response.status_code == status.HTTP_200_OK

def test_get_tabelas_tipos_receita_sem_unidade(jwt_authenticated_client_p, associacao_factory, tipo_receita_factory):
    associacao_1 = associacao_factory.create()

    tipo = tipo_receita_factory.create()
    tipo_2 = tipo_receita_factory.create()

    response = jwt_authenticated_client_p.get(
        f'/api/receitas/tabelas/?associacao_uuid={associacao_1.uuid}', content_type='application/json')
    result = json.loads(response.content)

    assert len(result['tipos_receita']) == 2
    assert result['tipos_receita'][0]['nome'] == tipo.nome
    assert result['tipos_receita'][1]['nome'] == tipo_2.nome
    assert response.status_code == status.HTTP_200_OK
