import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

URL = '/api/demonstrativo-financeiro/documento-final/'


def test_documento_final_formato_invalido_retorna_400(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'conta-associacao': str(conta_associacao.uuid),
            'periodo': str(periodo.uuid),
            'formato_arquivo': 'CSV',
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametro_inválido'


def test_documento_final_sem_conta_associacao_retorna_400(
    jwt_authenticated_client_a,
    periodo,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'periodo': str(periodo.uuid),
            'formato_arquivo': 'XLSX',
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametros_requeridos'


def test_documento_final_sem_periodo_retorna_400(
    jwt_authenticated_client_a,
    conta_associacao,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'conta-associacao': str(conta_associacao.uuid),
            'formato_arquivo': 'XLSX',
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametros_requeridos'


def test_documento_final_uuid_inexistente_retorna_404(
    jwt_authenticated_client_a,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'conta-associacao': '00000000-0000-0000-0000-000000000000',
            'periodo': '00000000-0000-0000-0000-000000000001',
            'formato_arquivo': 'XLSX',
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['erro'] == 'arquivo_nao_gerado'


def test_documento_final_sem_demonstrativo_retorna_404(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'conta-associacao': str(conta_associacao.uuid),
            'periodo': str(periodo.uuid),
            'formato_arquivo': 'XLSX',
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['erro'] == 'arquivo_nao_gerado'


def test_documento_final_xlsx_arquivo_inexistente_retorna_404(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
    demonstrativo_financeiro_final,
):
    # Usa caminho relativo ao MEDIA_ROOT; arquivo não existe em disco — open() falha no try/except
    demonstrativo_financeiro_final.arquivo_pdf = 'inexistente/arquivo.pdf'
    demonstrativo_financeiro_final.arquivo = 'inexistente/arquivo.xlsx'
    demonstrativo_financeiro_final.save()

    response = jwt_authenticated_client_a.get(
        URL,
        {
            'conta-associacao': str(conta_associacao.uuid),
            'periodo': str(periodo.uuid),
            'formato_arquivo': 'XLSX',
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['erro'] == 'arquivo_nao_gerado'


def test_documento_final_pdf_arquivo_inexistente_retorna_404(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
    demonstrativo_financeiro_final,
):
    # Usa caminho relativo ao MEDIA_ROOT; arquivo não existe em disco — open() falha no try/except
    demonstrativo_financeiro_final.arquivo_pdf = 'inexistente/arquivo.pdf'
    demonstrativo_financeiro_final.arquivo = 'inexistente/arquivo.xlsx'
    demonstrativo_financeiro_final.save()

    response = jwt_authenticated_client_a.get(
        URL,
        {
            'conta-associacao': str(conta_associacao.uuid),
            'periodo': str(periodo.uuid),
            'formato_arquivo': 'PDF',
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['erro'] == 'arquivo_nao_gerado'


def test_documento_final_xlsx_com_arquivo_retorna_200(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
    demonstrativo_financeiro_final,
    mock_arquivo_xlsx,
):
    demonstrativo_financeiro_final.arquivo = str(mock_arquivo_xlsx)
    demonstrativo_financeiro_final.arquivo_pdf = 'dummy/arquivo.pdf'
    demonstrativo_financeiro_final.save()

    from unittest.mock import patch, mock_open
    with patch('builtins.open', mock_open(read_data=b"PK fake xlsx")):
        response = jwt_authenticated_client_a.get(
            URL,
            {
                'conta-associacao': str(conta_associacao.uuid),
                'periodo': str(periodo.uuid),
                'formato_arquivo': 'XLSX',
            },
        )

    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'demonstrativo_financeiro.xlsx' in response['Content-Disposition']


def test_documento_final_pdf_com_arquivo_retorna_200(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
    demonstrativo_financeiro_final,
    mock_arquivo_pdf,
):
    demonstrativo_financeiro_final.arquivo_pdf = str(mock_arquivo_pdf)
    demonstrativo_financeiro_final.save()

    from unittest.mock import patch, mock_open
    with patch('builtins.open', mock_open(read_data=b"%PDF fake")):
        response = jwt_authenticated_client_a.get(
            URL,
            {
                'conta-associacao': str(conta_associacao.uuid),
                'periodo': str(periodo.uuid),
                'formato_arquivo': 'PDF',
            },
        )

    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/pdf'
    assert 'demonstrativo_financeiro.pdf' in response['Content-Disposition']


def test_documento_final_formato_padrao_e_xlsx(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
    demonstrativo_financeiro_final,
    mock_arquivo_xlsx,
):
    """Sem formato_arquivo, deve usar XLSX como padrão."""
    demonstrativo_financeiro_final.arquivo = str(mock_arquivo_xlsx)
    demonstrativo_financeiro_final.arquivo_pdf = 'dummy/arquivo.pdf'
    demonstrativo_financeiro_final.save()

    from unittest.mock import patch, mock_open
    with patch('builtins.open', mock_open(read_data=b"PK fake xlsx")):
        response = jwt_authenticated_client_a.get(
            URL,
            {
                'conta-associacao': str(conta_associacao.uuid),
                'periodo': str(periodo.uuid),
            },
        )

    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
