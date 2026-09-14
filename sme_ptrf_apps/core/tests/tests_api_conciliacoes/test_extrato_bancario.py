import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from ...models import ObservacaoConciliacao

pytestmark = pytest.mark.django_db


def test_extrato_bancario_sem_comprovante(jwt_authenticated_client_a, observacao_conciliacao_periodo_2020_1):
    response = jwt_authenticated_client_a.get(
        f'/api/conciliacoes/{observacao_conciliacao_periodo_2020_1.uuid}/extrato-bancario/',
        content_type='application/json')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['erro'] == 'extrato_bancario_nao_encontrado'


def test_extrato_bancario_arquivo_ausente_no_disco(jwt_authenticated_client_a, observacao_conciliacao_periodo_2020_1):
    ObservacaoConciliacao.objects.filter(pk=observacao_conciliacao_periodo_2020_1.pk).update(
        comprovante_extrato='comprovantes/arquivo_inexistente.pdf')

    response = jwt_authenticated_client_a.get(
        f'/api/conciliacoes/{observacao_conciliacao_periodo_2020_1.uuid}/extrato-bancario/',
        content_type='application/json')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['erro'] == 'extrato_bancario_nao_gerado'


def test_extrato_bancario_sucesso(jwt_authenticated_client_a, observacao_conciliacao_periodo_2020_1):
    observacao_conciliacao_periodo_2020_1.comprovante_extrato.save(
        'extrato.pdf', SimpleUploadedFile('extrato.pdf', b'%PDF-1.4 conteudo'), save=True)

    try:
        response = jwt_authenticated_client_a.get(
            f'/api/conciliacoes/{observacao_conciliacao_periodo_2020_1.uuid}/extrato-bancario/',
            content_type='application/json')

        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/pdf'
    finally:
        observacao_conciliacao_periodo_2020_1.comprovante_extrato.delete(save=True)
