import json
from unittest.mock import patch

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_consulta_codigo_eol(jwt_authenticated_client_a):

    path = 'sme_ptrf_apps.core.api.views.membro_associacao_viewset.TerceirizadasService.get_informacao_aluno'
    with patch(path) as mock_get:
        data = {
            "cd_aluno": 789798,
            "nm_aluno": "DANIEL RODRIGUES MARAN",
            "nm_social_aluno": None,
            "dt_nascimento_aluno": "1993-03-07T00:00:00",
            "cd_sexo_aluno": "M",
            "nm_mae_aluno": "REGINALDA RODRIGUES MARAN",
            "nm_pai_aluno": "SALVIO DONIZETI MARAN"
        }

        mock_get.return_value = data

        cod_eol = '789798'
        response = jwt_authenticated_client_a.get(f'/api/membros-associacao/codigo-identificacao/?codigo-eol={cod_eol}')
        result = json.loads(response.content)

        assert response.status_code == status.HTTP_200_OK
        assert result == data


def test_consulta_codigo_identificacao_sem_codigo_eol(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(f'/api/membros-associacao/codigo-identificacao/')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_consulta_codigo_identificacao_rf(jwt_authenticated_client_a):

    path = 'sme_ptrf_apps.core.api.views.membro_associacao_viewset.TerceirizadasService.get_informacao_servidor'
    with patch(path) as mock_get:
        data = [
            {
                "nm_pessoa": "LUCIMARA CARDOSO RODRIGUES",
                "cd_cpf_pessoa": "12808888813",
                "cargo": "ASSISTENTE DE DIRETOR DE ESCOLA",
                "cd_divisao": "093319",
                "divisao": "ALMEIDA JUNIOR, PROF.",
                "cd_coord": "108300",
                "coord": "DIRETORIA REGIONAL DE EDUCACAO CAPELA DO SOCORRO"
            }
        ]

        mock_get.return_value = data

        rf = '7210418'
        response = jwt_authenticated_client_a.get(f'/api/membros-associacao/codigo-identificacao/?rf={rf}')
        result = json.loads(response.content)

        assert response.status_code == status.HTTP_200_OK
        assert result == data


def test_consulta_cpf_responsavel(jwt_authenticated_client_a):
    cpf = '148.712.970-04'
    response = jwt_authenticated_client_a.get(f'/api/membros-associacao/cpf-responsavel/?cpf={cpf}')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {'detail': 'Pode ser cadastrado.'}


def test_consulta_codigo_identificacao_rf_com_membro_ja_cadastrado(jwt_authenticated_client_a, membro_associacao):
    rf = membro_associacao.codigo_identificacao
    response = jwt_authenticated_client_a.get(f'/api/membros-associacao/codigo-identificacao/?rf={rf}')
    result = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == {"detail": "Membro já cadastrado."}


def test_consulta_codigo_eol_com_membro_ja_cadastrado(jwt_authenticated_client_a, membro_associacao):

    cod_eol = membro_associacao.codigo_identificacao
    response = jwt_authenticated_client_a.get(f'/api/membros-associacao/codigo-identificacao/?codigo-eol={cod_eol}')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == {"detail": "Membro já cadastrado."}


def test_consulta_cpf_responsavel_com_membro_ja_cadastrado(jwt_authenticated_client_a, membro_associacao):

    cpf = membro_associacao.cpf
    response = jwt_authenticated_client_a.get(f'/api/membros-associacao/cpf-responsavel/?cpf={cpf}')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == {"detail": "Membro já cadastrado."}


def test_consulta_codigo_identificacao_sem_rf(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(f'/api/membros-associacao/codigo-identificacao/?rf=')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
