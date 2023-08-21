import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def teste_get_cargos_composicao(
    cargo_composicao_01,
    cargo_composicao_02,
    jwt_authenticated_client_sme,
):
    response = jwt_authenticated_client_sme.get(
        f'/api/cargos-composicao/',
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    # ['results'] por causa da paginação na viewset
    assert len(result['results']) == 2


def teste_get_cargo_composicao(
    cargo_composicao_01,
    cargo_composicao_02,
    ocupante_cargo_01,
    jwt_authenticated_client_sme,
):
    response = jwt_authenticated_client_sme.get(
        f'/api/cargos-composicao/{cargo_composicao_01.uuid}/',
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result['cargo_associacao'] == 'Presidente da diretoria executiva'
    assert result['ocupante_do_cargo']['nome'] == 'Ollyver Ottoboni'
