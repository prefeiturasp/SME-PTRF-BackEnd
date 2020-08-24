import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_retrieve_tecnico_dre(
    jwt_authenticated_client,
    tecnico_jose_dre_ipiranga):
    response = jwt_authenticated_client.get(
        f'/api/tecnicos-dre/{tecnico_jose_dre_ipiranga.uuid}/', content_type='application/json')
    result = json.loads(response.content)
    esperado = {
        "uuid": f'{tecnico_jose_dre_ipiranga.uuid}',
        "nome": tecnico_jose_dre_ipiranga.nome,
        "rf": tecnico_jose_dre_ipiranga.rf,
        "dre": {
            'uuid': f'{tecnico_jose_dre_ipiranga.dre.uuid}',
            'codigo_eol': f'{tecnico_jose_dre_ipiranga.dre.codigo_eol}',
            'tipo_unidade': f'{tecnico_jose_dre_ipiranga.dre.tipo_unidade}',
            'nome': f'{tecnico_jose_dre_ipiranga.dre.nome}',
            'sigla': f'{tecnico_jose_dre_ipiranga.dre.sigla}',
        },
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
