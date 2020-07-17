import json

import pytest
from rest_framework.status import HTTP_200_OK

pytestmark = pytest.mark.django_db


def test_repasses_pendentes(
    client,
    periodo,
    repasse,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao):

    response = client.get(f'/api/repasses/pendentes/?acao-associacao={acao_associacao.uuid}&data=02/09/2019', content_type='application/json')
    result = json.loads(response.content)
    esperado = {
        'valor_capital': '1000.28',
        'valor_custeio': '1000.40',
        'valor_livre': '0.00',
        'acao_associacao': {
            'uuid': str(acao_associacao.uuid),
            'id': acao_associacao.id,
            'nome': acao_associacao.acao.nome
        },
        'conta_associacao': {
            'uuid': str(conta_associacao.uuid),
            'nome': conta_associacao.tipo_conta.nome
        },
        'periodo': {
            'uuid': str(periodo.uuid),
            'data_inicio_realizacao_despesas': '2019-09-01',
            'data_fim_realizacao_despesas': '2019-11-30'
        }
    }

    assert result == esperado


def test_repasses_pendentes_livre_aplicacao(
    client,
    periodo_2020_1,
    repasse_2020_1_livre_aplicacao_pendente,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao):

    response = client.get(f'/api/repasses/pendentes/?acao-associacao={acao_associacao.uuid}&data=02/03/2020', content_type='application/json')
    result = json.loads(response.content)
    esperado = {
        'valor_capital': '0.00',
        'valor_custeio': '0.00',
        'valor_livre': '1000.00',
        'acao_associacao': {
            'uuid': str(acao_associacao.uuid),
            'id': acao_associacao.id,
            'nome': acao_associacao.acao.nome
        },
        'conta_associacao': {
            'uuid': str(conta_associacao.uuid),
            'nome': conta_associacao.tipo_conta.nome
        },
        'periodo': {
            'uuid': str(periodo_2020_1.uuid),
            'data_inicio_realizacao_despesas': '2020-01-01',
            'data_fim_realizacao_despesas': '2020-06-30'
        }
    }

    assert result == esperado
