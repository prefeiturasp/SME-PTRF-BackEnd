import json
import pytest
from unittest.mock import patch, ANY
from rest_framework import status

from sme_ptrf_apps.paa.enums import PaaStatusEnum

pytestmark = pytest.mark.django_db

_RETIFICACAO_SERVICE_PATH = 'sme_ptrf_apps.paa.services.valida_geracao_documentos_service.RetificacaoPaaService'
_TASK_PREVIA_PATH = 'sme_ptrf_apps.paa.api.views.paa_viewset.gerar_previa_documento_paa_retificacao_async'
_TASK_FINAL_PATH = 'sme_ptrf_apps.paa.api.views.paa_viewset.gerar_documento_paa_retificacao_async'
_PAA_SERVICE_PODE_GERAR_PATH = 'sme_ptrf_apps.paa.api.views.paa_viewset.PaaService.pode_gerar_documento_final'


@pytest.fixture
def paa_em_retificacao(paa_factory):
    paa = paa_factory()
    paa.status = PaaStatusEnum.EM_RETIFICACAO.name
    paa.save()
    return paa


@pytest.fixture
def alteracoes_mock():
    return {'prioridades': {'uuid-1': {'acao': 'modificado'}}}


# gerar-previa-documento — guard para EM_RETIFICACAO

def test_gerar_previa_documento_bloqueado_quando_paa_em_retificacao(
    jwt_authenticated_client_sme, flag_paa, paa_em_retificacao
):
    response = jwt_authenticated_client_sme.post(
        f'/api/paa/{paa_em_retificacao.uuid}/gerar-previa-documento/',
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Erro ao gerar documento: PAA está em retificação.' in response.json()["mensagem"]


# gerar-previa-retificacao

def test_gerar_previa_retificacao_retorna_400_quando_paa_nao_em_retificacao(
    jwt_authenticated_client_sme, flag_paa, paa_factory
):
    paa = paa_factory()

    response = jwt_authenticated_client_sme.post(
        f'/api/paa/{paa.uuid}/gerar-previa-retificacao/',
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'não está em retificação' in response.json()["mensagem"]


def test_gerar_previa_retificacao_retorna_400_quando_ja_em_processamento(
    jwt_authenticated_client_sme, flag_paa, paa_em_retificacao, documento_paa_factory
):
    documento_paa_factory(
        paa=paa_em_retificacao,
        versao='PREVIA',
        retificacao=True,
        status_geracao='EM_PROCESSAMENTO',
    )

    response = jwt_authenticated_client_sme.post(
        f'/api/paa/{paa_em_retificacao.uuid}/gerar-previa-retificacao/',
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "Há uma geração de prévia de retificação em processamento. Aguarde a conclusão para gerar a versão final."
    ) in response.json()["mensagem"]


def test_gerar_previa_retificacao_retorna_400_quando_sem_alteracoes(
    jwt_authenticated_client_sme, flag_paa, paa_em_retificacao
):
    with patch(_RETIFICACAO_SERVICE_PATH) as mock_service:
        mock_service.return_value.identificar_alteracoes.return_value = {}

        response = jwt_authenticated_client_sme.post(
            f'/api/paa/{paa_em_retificacao.uuid}/gerar-previa-retificacao/',
            content_type='application/json',
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Nenhuma alteração' in response.json()["mensagem"]


def test_gerar_previa_retificacao_sucesso(
    jwt_authenticated_client_sme, flag_paa, paa_em_retificacao, alteracoes_mock
):
    with patch(_RETIFICACAO_SERVICE_PATH) as mock_service, \
         patch(_TASK_PREVIA_PATH) as mock_task:
        mock_service.return_value.identificar_alteracoes.return_value = alteracoes_mock

        response = jwt_authenticated_client_sme.post(
            f'/api/paa/{paa_em_retificacao.uuid}/gerar-previa-retificacao/',
            content_type='application/json',
        )

    assert 'prévia de retificação' in response.json()["mensagem"]
    assert response.status_code == status.HTTP_200_OK, response.json()["mensagem"]
    mock_task.apply_async.assert_called_once()


# gerar-retificacao (documento final)
def test_gerar_retificacao_retorna_400_quando_paa_nao_em_retificacao(
    jwt_authenticated_client_sme, flag_paa, paa_factory
):
    paa = paa_factory()

    response = jwt_authenticated_client_sme.post(
        f'/api/paa/{paa.uuid}/gerar-documento-retificacao/',
        content_type='application/json',
        data=json.dumps({'confirmar': 1}),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'não está em retificação' in response.json()["mensagem"]


def test_gerar_retificacao_retorna_400_sem_confirmacao(
    jwt_authenticated_client_sme, flag_paa, paa_em_retificacao, alteracoes_mock
):
    with patch(_RETIFICACAO_SERVICE_PATH) as mock_service, \
         patch(_PAA_SERVICE_PODE_GERAR_PATH, return_value=[]):
        mock_service.return_value.identificar_alteracoes.return_value = alteracoes_mock

        response = jwt_authenticated_client_sme.post(
            f'/api/paa/{paa_em_retificacao.uuid}/gerar-documento-retificacao/',
            content_type='application/json',
            data=json.dumps({}),
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'confirmar' in response.json()


def test_gerar_retificacao_retorna_400_quando_sem_alteracoes(
    jwt_authenticated_client_sme, flag_paa, paa_em_retificacao
):
    with patch(_RETIFICACAO_SERVICE_PATH) as mock_service:
        mock_service.return_value.identificar_alteracoes.return_value = {}

        response = jwt_authenticated_client_sme.post(
            f'/api/paa/{paa_em_retificacao.uuid}/gerar-documento-retificacao/',
            content_type='application/json',
            data=json.dumps({'confirmar': 1}),
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Nenhuma alteração' in response.json()["mensagem"]


def test_gerar_retificacao_sucesso(
    jwt_authenticated_client_sme, flag_paa, paa_em_retificacao, alteracoes_mock
):
    with patch(_RETIFICACAO_SERVICE_PATH) as mock_service, \
         patch(_PAA_SERVICE_PODE_GERAR_PATH, return_value=[]), \
         patch(_TASK_FINAL_PATH) as mock_task:
        mock_service.return_value.identificar_alteracoes.return_value = alteracoes_mock

        response = jwt_authenticated_client_sme.post(
            f'/api/paa/{paa_em_retificacao.uuid}/gerar-documento-retificacao/',
            content_type='application/json',
            data=json.dumps({'confirmar': 1}),
        )

    assert response.status_code == status.HTTP_200_OK, response.json()["mensagem"]
    assert 'retificação' in response.json()["mensagem"]
    mock_task.apply_async.assert_called_once_with(
        args=[str(paa_em_retificacao.uuid), ANY]
    )


# documento-previa com ?retificacao=true

def test_documento_previa_retorna_400_quando_nao_existe_retificacao(
    jwt_authenticated_client_sme, flag_paa, paa_factory
):
    paa = paa_factory()

    response = jwt_authenticated_client_sme.get(
        f'/api/paa/{paa.uuid}/documento-previa/?retificacao=true',
    )

    assert response.status_code == 400
    assert 'não gerado' in response.json()["mensagem"]


def test_documento_previa_sem_retificacao_retorna_400_quando_nao_existe(
    jwt_authenticated_client_sme, flag_paa, paa_factory
):
    paa = paa_factory()

    response = jwt_authenticated_client_sme.get(
        f'/api/paa/{paa.uuid}/documento-previa/',
    )

    assert response.status_code == 400
    assert 'não gerado' in response.json()["mensagem"]
