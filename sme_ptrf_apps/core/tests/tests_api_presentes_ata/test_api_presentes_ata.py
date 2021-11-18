import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_get_presentes_ata_nao_agrupados(
    jwt_authenticated_client_a, presente_ata_membro, presente_ata_membro_e_conselho_fiscal, presente_ata_nao_membro
):
    response = jwt_authenticated_client_a.get(
        f'/api/presentes-ata/?ata__uuid={presente_ata_membro.ata.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    esperado = [
        {'ata': f'{presente_ata_membro.ata.uuid}',
         'cargo': presente_ata_membro.cargo,
         'editavel': presente_ata_membro.editavel,
         'identificacao': presente_ata_membro.identificacao,
         'membro': presente_ata_membro.membro,
         'nome': presente_ata_membro.nome
        },
        {'ata': f'{presente_ata_membro_e_conselho_fiscal.ata.uuid}',
         'cargo': presente_ata_membro_e_conselho_fiscal.cargo,
         'editavel': presente_ata_membro_e_conselho_fiscal.editavel,
         'identificacao': presente_ata_membro_e_conselho_fiscal.identificacao,
         'membro': presente_ata_membro_e_conselho_fiscal.membro,
         'nome': presente_ata_membro_e_conselho_fiscal.nome
         },
        {'ata': f'{presente_ata_nao_membro.ata.uuid}',
         'cargo': presente_ata_nao_membro.cargo,
         'editavel': presente_ata_nao_membro.editavel,
         'identificacao': presente_ata_nao_membro.identificacao,
         'membro': presente_ata_nao_membro.membro,
         'nome': presente_ata_nao_membro.nome
         }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert esperado == result


def test_get_presentes_agrupados(
    jwt_authenticated_client_a, presente_ata_membro, presente_ata_membro_e_conselho_fiscal, presente_ata_nao_membro
):
    response = jwt_authenticated_client_a.get(
        f'/api/presentes-ata/membros-e-nao-membros/?ata_uuid={presente_ata_membro.ata.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'presentes_ata_conselho_fiscal': [
            {
                'alterado_em': presente_ata_membro_e_conselho_fiscal.alterado_em.isoformat("T"),
                'ata_id': presente_ata_membro_e_conselho_fiscal.ata.id,
                'cargo': presente_ata_membro_e_conselho_fiscal.cargo,
                'conselho_fiscal': presente_ata_membro_e_conselho_fiscal.conselho_fiscal,
                'criado_em': presente_ata_membro_e_conselho_fiscal.criado_em.isoformat("T"),
                'id': presente_ata_membro_e_conselho_fiscal.id,
                'identificacao': presente_ata_membro_e_conselho_fiscal.identificacao,
                'membro': presente_ata_membro_e_conselho_fiscal.membro,
                'nome': presente_ata_membro_e_conselho_fiscal.nome,
                'uuid': f'{presente_ata_membro_e_conselho_fiscal.uuid}'
             }
        ],
        'presentes_membros': [
            {
                'alterado_em': presente_ata_membro.alterado_em.isoformat("T"),
                'ata_id': presente_ata_membro.ata.id,
                'cargo': presente_ata_membro.cargo,
                'conselho_fiscal': presente_ata_membro.conselho_fiscal,
                'criado_em': presente_ata_membro.criado_em.isoformat("T"),
                'id': presente_ata_membro.id,
                'identificacao': presente_ata_membro.identificacao,
                'membro': presente_ata_membro.membro,
                'nome': presente_ata_membro.nome,
                'uuid': f'{presente_ata_membro.uuid}'
            },
            {
                'alterado_em': presente_ata_membro_e_conselho_fiscal.alterado_em.isoformat("T"),
                'ata_id': presente_ata_membro_e_conselho_fiscal.ata.id,
                'cargo': presente_ata_membro_e_conselho_fiscal.cargo,
                'conselho_fiscal': presente_ata_membro_e_conselho_fiscal.conselho_fiscal,
                'criado_em': presente_ata_membro_e_conselho_fiscal.criado_em.isoformat("T"),
                'id': presente_ata_membro_e_conselho_fiscal.id,
                'identificacao': presente_ata_membro_e_conselho_fiscal.identificacao,
                'membro': presente_ata_membro_e_conselho_fiscal.membro,
                'nome': presente_ata_membro_e_conselho_fiscal.nome,
                'uuid': f'{presente_ata_membro_e_conselho_fiscal.uuid}'
            }
        ],
        'presentes_nao_membros': [
            {
                'alterado_em': presente_ata_nao_membro.alterado_em.isoformat("T"),
                'ata_id': presente_ata_nao_membro.ata.id,
                'cargo': presente_ata_nao_membro.cargo,
                'conselho_fiscal': presente_ata_nao_membro.conselho_fiscal,
                'criado_em': presente_ata_nao_membro.criado_em.isoformat("T"),
                'id': presente_ata_nao_membro.id,
                'identificacao': presente_ata_nao_membro.identificacao,
                'membro': presente_ata_nao_membro.membro,
                'nome': presente_ata_nao_membro.nome,
                'uuid': f'{presente_ata_nao_membro.uuid}'
             }
        ]}

    assert response.status_code == status.HTTP_200_OK
    assert esperado == result


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
