import json
from unittest.mock import patch

import pytest
from requests import ConnectTimeout, ReadTimeout
from rest_framework import status

from sme_ptrf_apps.core.services import SmeIntegracaoApiException, TerceirizadasException

pytestmark = pytest.mark.django_db


def test_consulta_codigo_eol(jwt_authenticated_client_a):
    path = 'sme_ptrf_apps.core.api.views.membro_associacao_viewset.SmeIntegracaoApiService.get_informacao_aluno'
    with patch(path) as mock_get:
        data = {
            "codigoAluno": 5298880,
            "anoLetivo": 2021,
            "nomeAluno": "TERESA SUGANUMA",
            "nomeSocialAluno": None,
            "codigoSituacaoMatricula": 1,
            "situacaoMatricula": "Ativo",
            "dataSituacao": "2021-08-24T13:45:33.647",
            "dataNascimento": "1952-04-17T00:00:00",
            "numeroAlunoChamada": 0,
            "codigoTurma": 2355718,
            "nomeResponsavel": "TERESA SUGANUMA",
            "tipoResponsavel": "4",
            "celularResponsavel": "",
            "dataAtualizacaoContato": "2012-07-11T21:38:31.663"
        }

        mock_get.return_value = data

        cod_eol = '5298880'
        response = jwt_authenticated_client_a.get(f'/api/membros-associacao/codigo-identificacao/?codigo-eol={cod_eol}')
        result = json.loads(response.content)

        assert response.status_code == status.HTTP_200_OK
        assert result == data


def test_consulta_codigo_identificacao_sem_codigo_eol(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get('/api/membros-associacao/codigo-identificacao/')
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
    response = jwt_authenticated_client_a.get('/api/membros-associacao/codigo-identificacao/?rf=')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_consulta_codigo_eol_com_associacao_uuid(jwt_authenticated_client_a, associacao):
    path = 'sme_ptrf_apps.core.api.views.membro_associacao_viewset.SmeIntegracaoApiService.get_informacao_aluno'
    with patch(path) as mock_get:
        data = {"codigoAluno": 5298880, "nomeAluno": "TERESA SUGANUMA"}
        mock_get.return_value = data

        cod_eol = '5298880'
        response = jwt_authenticated_client_a.get(
            f'/api/membros-associacao/codigo-identificacao/?codigo-eol={cod_eol}&associacao_uuid={associacao.uuid}'
        )
        result = json.loads(response.content)

        assert response.status_code == status.HTTP_200_OK
        assert result == data


def test_consulta_codigo_identificacao_rf_sme_integracao_exception(jwt_authenticated_client_a):
    path = 'sme_ptrf_apps.core.api.views.membro_associacao_viewset.TerceirizadasService.get_informacao_servidor'
    with patch(path) as mock_get:
        mock_get.side_effect = SmeIntegracaoApiException('Erro na API de integração SME.')

        rf = '7210418'
        response = jwt_authenticated_client_a.get(f'/api/membros-associacao/codigo-identificacao/?rf={rf}')
        result = json.loads(response.content)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert result == {'detail': 'Erro na API de integração SME.'}


def test_consulta_codigo_identificacao_rf_terceirizadas_exception(jwt_authenticated_client_a):
    path = 'sme_ptrf_apps.core.api.views.membro_associacao_viewset.TerceirizadasService.get_informacao_servidor'
    with patch(path) as mock_get:
        mock_get.side_effect = TerceirizadasException('Erro na API de terceirizadas.')

        rf = '7210418'
        response = jwt_authenticated_client_a.get(f'/api/membros-associacao/codigo-identificacao/?rf={rf}')
        result = json.loads(response.content)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert result == {'detail': 'Erro na API de terceirizadas.'}


def test_consulta_codigo_identificacao_rf_read_timeout(jwt_authenticated_client_a):
    path = 'sme_ptrf_apps.core.api.views.membro_associacao_viewset.TerceirizadasService.get_informacao_servidor'
    with patch(path) as mock_get:
        mock_get.side_effect = ReadTimeout()

        rf = '7210418'
        response = jwt_authenticated_client_a.get(f'/api/membros-associacao/codigo-identificacao/?rf={rf}')
        result = json.loads(response.content)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert result == {'detail': 'EOL Timeout'}


def test_consulta_codigo_identificacao_rf_connect_timeout(jwt_authenticated_client_a):
    path = 'sme_ptrf_apps.core.api.views.membro_associacao_viewset.TerceirizadasService.get_informacao_servidor'
    with patch(path) as mock_get:
        mock_get.side_effect = ConnectTimeout()

        rf = '7210418'
        response = jwt_authenticated_client_a.get(f'/api/membros-associacao/codigo-identificacao/?rf={rf}')
        result = json.loads(response.content)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert result == {'detail': 'EOL Timeout'}


def test_consulta_cpf_responsavel_sem_cpf(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get('/api/membros-associacao/cpf-responsavel/')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'parametros_requeridos'


def test_consulta_cpf_responsavel_com_associacao_uuid(jwt_authenticated_client_a, associacao):
    cpf = '148.712.970-04'
    response = jwt_authenticated_client_a.get(
        f'/api/membros-associacao/cpf-responsavel/?cpf={cpf}&associacao_uuid={associacao.uuid}'
    )
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {'detail': 'Pode ser cadastrado.'}


def test_lista_cargos(jwt_authenticated_client_a):
    path = 'sme_ptrf_apps.core.api.views.membro_associacao_viewset.TerceirizadasService.get_informacao_servidor'
    with patch(path) as mock_get:
        data = [{"nm_pessoa": "LUCIMARA CARDOSO RODRIGUES", "cargo": "ASSISTENTE DE DIRETOR DE ESCOLA"}]
        mock_get.return_value = data

        rf = '7210418'
        response = jwt_authenticated_client_a.get(f'/api/membros-associacao/lista-cargos/?rf={rf}')
        result = json.loads(response.content)

        assert response.status_code == status.HTTP_200_OK
        assert result == data


def test_lista_cargos_sem_rf(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get('/api/membros-associacao/lista-cargos/')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'parametros_requeridos'


def test_lista_cargos_sme_integracao_exception(jwt_authenticated_client_a):
    path = 'sme_ptrf_apps.core.api.views.membro_associacao_viewset.TerceirizadasService.get_informacao_servidor'
    with patch(path) as mock_get:
        mock_get.side_effect = SmeIntegracaoApiException('Erro na API de integração SME.')

        rf = '7210418'
        response = jwt_authenticated_client_a.get(f'/api/membros-associacao/lista-cargos/?rf={rf}')
        result = json.loads(response.content)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert result == {'detail': 'Erro na API de integração SME.'}


def test_lista_cargos_terceirizadas_exception(jwt_authenticated_client_a):
    path = 'sme_ptrf_apps.core.api.views.membro_associacao_viewset.TerceirizadasService.get_informacao_servidor'
    with patch(path) as mock_get:
        mock_get.side_effect = TerceirizadasException('Erro na API de terceirizadas.')

        rf = '7210418'
        response = jwt_authenticated_client_a.get(f'/api/membros-associacao/lista-cargos/?rf={rf}')
        result = json.loads(response.content)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert result == {'detail': 'Erro na API de terceirizadas.'}


def test_lista_cargos_read_timeout(jwt_authenticated_client_a):
    path = 'sme_ptrf_apps.core.api.views.membro_associacao_viewset.TerceirizadasService.get_informacao_servidor'
    with patch(path) as mock_get:
        mock_get.side_effect = ReadTimeout()

        rf = '7210418'
        response = jwt_authenticated_client_a.get(f'/api/membros-associacao/lista-cargos/?rf={rf}')
        result = json.loads(response.content)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert result == {'detail': 'EOL Timeout'}


def test_lista_cargos_connect_timeout(jwt_authenticated_client_a):
    path = 'sme_ptrf_apps.core.api.views.membro_associacao_viewset.TerceirizadasService.get_informacao_servidor'
    with patch(path) as mock_get:
        mock_get.side_effect = ConnectTimeout()

        rf = '7210418'
        response = jwt_authenticated_client_a.get(f'/api/membros-associacao/lista-cargos/?rf={rf}')
        result = json.loads(response.content)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert result == {'detail': 'EOL Timeout'}
