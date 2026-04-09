import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

URL = '/api/demonstrativo-financeiro/documento-previa/'


def test_documento_previa_formato_invalido_retorna_400(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'conta-associacao': str(conta_associacao.uuid),
            'periodo': str(periodo.uuid),
            'formato_arquivo': 'TXT',
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametro_inválido'


def test_documento_previa_sem_conta_associacao_retorna_400(
    jwt_authenticated_client_a,
    periodo,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'periodo': str(periodo.uuid),
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametros_requeridos'


def test_documento_previa_sem_periodo_retorna_400(
    jwt_authenticated_client_a,
    conta_associacao,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'conta-associacao': str(conta_associacao.uuid),
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametros_requeridos'


def test_documento_previa_uuid_inexistente_retorna_404(
    jwt_authenticated_client_a,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'conta-associacao': '00000000-0000-0000-0000-000000000000',
            'periodo': '00000000-0000-0000-0000-000000000001',
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['erro'] == 'arquivo_nao_gerado'


def test_documento_previa_sem_demonstrativo_retorna_404(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
):
    response = jwt_authenticated_client_a.get(
        URL,
        {
            'conta-associacao': str(conta_associacao.uuid),
            'periodo': str(periodo.uuid),
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['erro'] == 'arquivo_nao_gerado'


def test_documento_previa_pdf_arquivo_inexistente_retorna_404(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
    demonstrativo_financeiro_previa,
):
    # Arquivo aponta para caminho inexistente — open() falha no try/except da view
    demonstrativo_financeiro_previa.arquivo_pdf = 'inexistente/arquivo.pdf'
    demonstrativo_financeiro_previa.arquivo = 'inexistente/arquivo.xlsx'
    demonstrativo_financeiro_previa.save()

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


def test_documento_previa_pdf_com_arquivo_retorna_200(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
    demonstrativo_financeiro_previa,
    mock_arquivo_pdf,
):
    demonstrativo_financeiro_previa.arquivo_pdf = str(mock_arquivo_pdf)
    demonstrativo_financeiro_previa.save()

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


def test_documento_previa_xlsx_com_arquivo_retorna_200(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
    demonstrativo_financeiro_previa,
    mock_arquivo_xlsx,
):
    demonstrativo_financeiro_previa.arquivo = str(mock_arquivo_xlsx)
    demonstrativo_financeiro_previa.arquivo_pdf = 'dummy/arquivo.pdf'
    demonstrativo_financeiro_previa.save()

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


def test_documento_previa_formato_padrao_e_pdf(
    jwt_authenticated_client_a,
    periodo,
    conta_associacao,
    demonstrativo_financeiro_previa,
    mock_arquivo_pdf,
):
    """Sem formato_arquivo, deve usar PDF como padrão (diferente de documento-final que usa XLSX)."""
    demonstrativo_financeiro_previa.arquivo_pdf = str(mock_arquivo_pdf)
    demonstrativo_financeiro_previa.save()

    from unittest.mock import patch, mock_open
    with patch('builtins.open', mock_open(read_data=b"%PDF fake")):
        response = jwt_authenticated_client_a.get(
            URL,
            {
                'conta-associacao': str(conta_associacao.uuid),
                'periodo': str(periodo.uuid),
            },
        )

    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/pdf'
