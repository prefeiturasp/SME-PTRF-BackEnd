import json
import uuid

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_download_documento_pdf(
    jwt_authenticated_client_a,
    analise_prestacao_conta_2020_1_teste_analises_sem_versao,
):
    analise_prestacao = analise_prestacao_conta_2020_1_teste_analises_sem_versao
    analise_prestacao.arquivo_pdf = SimpleUploadedFile(
        "relatorio_acertos.pdf",
        b"%PDF-1.4 fake pdf",
        content_type="application/pdf",
    )
    analise_prestacao.save()

    url = f'/api/analises-prestacoes-contas/download-documento-pdf/?analise_prestacao_uuid={analise_prestacao.uuid}'

    response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/pdf'
    assert response['Content-Disposition'] == 'attachment; filename=relatorio_acertos.pdf'


def test_api_download_documento_pdf_arquivo_nao_gerado(
    jwt_authenticated_client_a,
    analise_prestacao_conta_2020_1_teste_analises_sem_versao,
):
    analise_prestacao = analise_prestacao_conta_2020_1_teste_analises_sem_versao

    url = f'/api/analises-prestacoes-contas/download-documento-pdf/?analise_prestacao_uuid={analise_prestacao.uuid}'

    response = jwt_authenticated_client_a.get(url)
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert result['erro'] == 'arquivo_nao_gerado'


def test_api_download_documento_pdf_sem_uuid(
    jwt_authenticated_client_a,
):
    url = '/api/analises-prestacoes-contas/download-documento-pdf/'

    response = jwt_authenticated_client_a.get(url)
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'parametros_requeridos'


def test_api_download_documento_pdf_analise_nao_encontrada(
    jwt_authenticated_client_a,
):
    analise_inexistente = uuid.uuid4()
    url = f'/api/analises-prestacoes-contas/download-documento-pdf/?analise_prestacao_uuid={analise_inexistente}'

    response = jwt_authenticated_client_a.get(url)
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'Objeto não encontrado.'


def test_api_download_documento_pdf_uuid_invalido(
    jwt_authenticated_client_a,
):
    url = '/api/analises-prestacoes-contas/download-documento-pdf/?analise_prestacao_uuid=uuid-invalido'

    response = jwt_authenticated_client_a.get(url)
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'Ocorreu um erro!'
