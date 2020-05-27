import json

import pytest
from rest_framework import status

from ...api.serializers import ReceitaListaSerializer
from ...models import Receita

pytestmark = pytest.mark.django_db


def test_api_desconciliar_receita(client, receita_conferida):
    receita_uuid = receita_conferida.uuid

    url = f'/api/receitas/{receita_uuid}/desconciliar/'

    response = client.patch(url, content_type='application/json')

    result = json.loads(response.content)

    receita_desconciliada = Receita.by_uuid(receita_uuid)
    result_esperado = ReceitaListaSerializer(receita_desconciliada, many=False).data

    # Converte campos não string em strings para que a comparação funcione
    result_esperado['uuid'] = f'{result_esperado["uuid"]}'
    result_esperado['data'] = f'{result_esperado["data"]}'

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado

    assert not receita_desconciliada.conferido, "Receita não deveria estar marcada como conferida."
