import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def comentario_analise_prestacao(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'ComentarioAnalisePrestacao',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        ordem=1,
        comentario='Teste',
    )

def test_list_comentarios_analise_prestacao(client, prestacao_conta_2020_1_conciliada, comentario_analise_prestacao):
    prestacao_uuid = prestacao_conta_2020_1_conciliada.uuid

    response = client.get(f'/api/comentarios-de-analises/?prestacao_conta__uuid={prestacao_uuid}',
                          content_type='application/json')

    result = json.loads(response.content)

    esperado = [
        {
            'uuid': f'{comentario_analise_prestacao.uuid}',
            'prestacao_conta': f'{prestacao_conta_2020_1_conciliada.uuid}',
            'ordem': 1,
            'comentario': 'Teste',
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado, "Não retornou o resultado esperado"


def test_list_comentarios_analise_prestacao_nao_existe(client, prestacao_conta_2020_1_conciliada, comentario_analise_prestacao):
    uuid_prestacao_inexistemte = comentario_analise_prestacao.uuid

    response = client.get(f'/api/comentarios-de-analise/?prestacao_conta__uuid={uuid_prestacao_inexistemte}',
                          content_type='application/json')

    result = json.loads(response.content)

    esperado = []

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado, "Deveria ter retornado uma lista vazia."
