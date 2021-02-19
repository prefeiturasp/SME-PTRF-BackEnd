import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_retrieve_arquivo(
    jwt_authenticated_client_a,
    arquivo_carga
):
    response = jwt_authenticated_client_a.get(
        f'/api/arquivos/{arquivo_carga.uuid}/', content_type='application/json')

    result = json.loads(response.content)

    esperado = {
        "id": arquivo_carga.id,
        "criado_em": arquivo_carga.criado_em.isoformat("T"),
        "alterado_em": arquivo_carga.alterado_em.isoformat("T"),
        "uuid": f'{arquivo_carga.uuid}',
        "identificador": arquivo_carga.identificador,
        "conteudo": 'http://testserver/media/arquivo.csv',
        "tipo_carga": "CARGA_ASSOCIACOES",
        "tipo_delimitador": "DELIMITADOR_VIRGULA",
        "status": "PENDENTE",
        "log": None,
        "ultima_execucao": None
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
