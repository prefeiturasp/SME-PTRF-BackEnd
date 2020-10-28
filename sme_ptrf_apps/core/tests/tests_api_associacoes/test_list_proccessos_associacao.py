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

    esperado = [
        {
            'uuid': f'{processo_associacao_123456_2019.uuid}',
            'associacao':
                {
                    'id': processo_associacao_123456_2019.associacao.id,
                    'nome': processo_associacao_123456_2019.associacao.nome
                },
            'criado_em': processo_associacao_123456_2019.criado_em.isoformat("T"),
            'alterado_em': processo_associacao_123456_2019.alterado_em.isoformat("T"),
            'numero_processo': processo_associacao_123456_2019.numero_processo,
            'ano': processo_associacao_123456_2019.ano,
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
