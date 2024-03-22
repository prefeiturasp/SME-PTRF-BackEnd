import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def processo_de_outra_associacao(associacao_sem_periodo_inicial):
    return baker.make(
        'ProcessoAssociacao',
        associacao=associacao_sem_periodo_inicial,
        numero_processo='777777',
        ano='2019'
    )


def test_list_processos_da_associacao(jwt_authenticated_client_a, associacao, processo_associacao_123456_2019,
                                       processo_de_outra_associacao):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/processos/',
                          content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1
    assert result[0]['associacao']['id'] == processo_associacao_123456_2019.associacao.id
    assert result[0]['numero_processo'] == processo_associacao_123456_2019.numero_processo
    assert result[0]['ano'] == processo_associacao_123456_2019.ano
    assert any(periodo['referencia'] == '2019.1' for periodo in result[0]['periodos'])
    assert any(periodo['referencia'] == '2019.2' for periodo in result[0]['periodos'])
