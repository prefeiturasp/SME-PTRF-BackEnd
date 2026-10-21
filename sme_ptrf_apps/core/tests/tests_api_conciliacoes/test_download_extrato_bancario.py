import json
from uuid import uuid4

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from ...models import ObservacaoConciliacao

pytestmark = pytest.mark.django_db


def test_download_extrato_bancario_sem_uuid(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(
        '/api/conciliacoes/download-extrato-bancario/', content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'parametros_requeridos'


def test_download_extrato_bancario_observacao_nao_encontrada(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(
        f'/api/conciliacoes/download-extrato-bancario/?observacao_uuid={uuid4()}', content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'Objeto não encontrado.'


def test_download_extrato_bancario_sem_comprovante(jwt_authenticated_client_a, observacao_conciliacao_periodo_2020_1):
    observacao = observacao_conciliacao_periodo_2020_1

    response = jwt_authenticated_client_a.get(
        f'/api/conciliacoes/download-extrato-bancario/?observacao_uuid={observacao.uuid}',
        content_type='application/json')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json.loads(response.content)['erro'] == 'extrato_bancario_nao_encontrado'


def test_download_extrato_bancario_arquivo_ausente_no_disco(
        jwt_authenticated_client_a, observacao_conciliacao_periodo_2020_1):
    observacao = observacao_conciliacao_periodo_2020_1
    ObservacaoConciliacao.objects.filter(pk=observacao.pk).update(
        comprovante_extrato='comprovantes/arquivo_inexistente.pdf')

    response = jwt_authenticated_client_a.get(
        f'/api/conciliacoes/download-extrato-bancario/?observacao_uuid={observacao.uuid}',
        content_type='application/json')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json.loads(response.content)['erro'] == 'extrato_bancario_nao_gerado'


def test_download_extrato_bancario_sucesso(jwt_authenticated_client_a, observacao_conciliacao_periodo_2020_1):
    observacao = observacao_conciliacao_periodo_2020_1
    observacao.comprovante_extrato.save(
        'extrato.pdf', SimpleUploadedFile('extrato.pdf', b'%PDF-1.4 conteudo'), save=True)

    try:
        response = jwt_authenticated_client_a.get(
            f'/api/conciliacoes/download-extrato-bancario/?observacao_uuid={observacao.uuid}',
            content_type='application/json')

        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/pdf'
    finally:
        observacao.comprovante_extrato.delete(save=True)
