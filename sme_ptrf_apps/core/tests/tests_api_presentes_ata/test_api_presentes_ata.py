import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_get_presentes_ata_nao_agrupados(
    jwt_authenticated_client_a,
    presente_ata_membro_arnaldo,
    presente_ata_membro_e_conselho_fiscal_benedito,
    presente_ata_nao_membro_carlos
):
    response = jwt_authenticated_client_a.get(
        f'/api/presentes-ata/?ata__uuid={presente_ata_membro_arnaldo.ata.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 3


def test_get_presentes_agrupados(
    jwt_authenticated_client_a,
    presente_ata_membro,
    presente_ata_membro_e_conselho_fiscal,
    presente_ata_nao_membro,
    membro_associacao_presidente_conselho_01
):
    response = jwt_authenticated_client_a.get(
        f'/api/presentes-ata/membros-e-nao-membros/?ata_uuid={presente_ata_membro.ata.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result['presentes_ata_conselho_fiscal']) == 1
    assert len(result['presentes_membros']) == 2
    assert len(result['presentes_nao_membros']) == 1


def test_get_padrao_presentes(
    jwt_authenticated_client_a, presente_ata_membro,
):
    response = jwt_authenticated_client_a.get(
        f'/api/presentes-ata/padrao-de-presentes/?ata_uuid={presente_ata_membro.ata.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK


def test_nome_cargo_membro_associacao(
    jwt_authenticated_client_a, presente_ata_membro,
):
    identificador = "12345"
    response = jwt_authenticated_client_a.get(
        f'/api/presentes-ata/get-nome-cargo-membro-associacao/?ata_uuid={presente_ata_membro.ata.uuid}&identificador={identificador}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
