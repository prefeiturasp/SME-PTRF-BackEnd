import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import DemonstrativoFinanceiro

pytestmark = pytest.mark.django_db


def test_pdf_sem_arquivo_retorna_404(
    jwt_authenticated_client_a,
    demonstrativo_financeiro_final,
):
    url = f'/api/demonstrativo-financeiro/{demonstrativo_financeiro_final.uuid}/pdf/'

    response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['erro'] == 'arquivo_nao_gerado'


def test_pdf_com_arquivo_retorna_200(
    jwt_authenticated_client_a,
    demonstrativo_financeiro_final,
    mock_arquivo_pdf,
):
    demonstrativo_financeiro_final.arquivo_pdf = str(mock_arquivo_pdf)
    demonstrativo_financeiro_final.save()

    url = f'/api/demonstrativo-financeiro/{demonstrativo_financeiro_final.uuid}/pdf/'

    from unittest.mock import patch, mock_open
    with patch('builtins.open', mock_open(read_data=b"%PDF fake")):
        response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/pdf'
    assert 'demonstrativo_financeiro.pdf' in response['Content-Disposition']


def test_pdf_uuid_inexistente_retorna_404(
    jwt_authenticated_client_a,
):
    url = '/api/demonstrativo-financeiro/00000000-0000-0000-0000-000000000000/pdf/'

    with pytest.raises(DemonstrativoFinanceiro.DoesNotExist):
        jwt_authenticated_client_a.get(url)
