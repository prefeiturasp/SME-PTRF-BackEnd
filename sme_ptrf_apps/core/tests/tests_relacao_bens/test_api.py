from unittest.mock import patch

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# relacao_bens_info
# ---------------------------------------------------------------------------

def test_relacoes_info_sem_bens_adquiridos(jwt_authenticated_client_a, periodo, conta_associacao):
    url = f"/api/relacao-bens/relacao-bens-info/?conta-associacao={conta_associacao.uuid}&periodo={periodo.uuid}"
    response = jwt_authenticated_client_a.get(url)
    result = response.json()

    assert result == "Não houve bem adquirido ou produzido no referido período."


def test_relacoes_info_documento_pendente_geracao(
        jwt_authenticated_client_a, periodo, conta_associacao, rateio_despesa_demonstrativo):
    url = f"/api/relacao-bens/relacao-bens-info/?conta-associacao={conta_associacao.uuid}&periodo={periodo.uuid}"
    response = jwt_authenticated_client_a.get(url)
    result = response.json()

    assert result == "Documento pendente de geração"


def test_relacoes_info_com_relacao_bens_previa(
        jwt_authenticated_client_a, periodo, conta_associacao, relacao_bens_previa):
    url = f"/api/relacao-bens/relacao-bens-info/?conta-associacao={conta_associacao.uuid}&periodo={periodo.uuid}"
    response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == str(relacao_bens_previa)


def test_relacoes_info_com_relacao_bens_final(
        jwt_authenticated_client_a, periodo, conta_associacao, prestacao_conta, relacao_bens_final):
    url = f"/api/relacao-bens/relacao-bens-info/?conta-associacao={conta_associacao.uuid}&periodo={periodo.uuid}"
    response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == str(relacao_bens_final)


# ---------------------------------------------------------------------------
# previa
# ---------------------------------------------------------------------------

def test_previa_sem_parametros_retorna_400(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get("/api/relacao-bens/previa/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['erro'] == 'parametros_requeridos'


def test_previa_sem_datas_retorna_400(jwt_authenticated_client_a, periodo, conta_associacao):
    url = f"/api/relacao-bens/previa/?conta-associacao={conta_associacao.uuid}&periodo={periodo.uuid}"
    response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['erro'] == 'parametros_requeridos'


def test_previa_data_fim_menor_que_data_inicio_retorna_400(jwt_authenticated_client_a, periodo, conta_associacao):
    url = (
        f"/api/relacao-bens/previa/"
        f"?conta-associacao={conta_associacao.uuid}"
        f"&periodo={periodo.uuid}"
        f"&data_inicio=2019-10-01"
        f"&data_fim=2019-09-01"
    )
    response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['erro'] == 'erro_nas_datas'


def test_previa_data_fim_maior_que_fim_realizacao_retorna_400(jwt_authenticated_client_a, periodo, conta_associacao):
    # periodo.data_fim_realizacao_despesas == 2019-11-30
    url = (
        f"/api/relacao-bens/previa/"
        f"?conta-associacao={conta_associacao.uuid}"
        f"&periodo={periodo.uuid}"
        f"&data_inicio=2019-09-01"
        f"&data_fim=2019-12-31"
    )
    response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['erro'] == 'erro_nas_datas'


def test_previa_parametros_validos_retorna_200(jwt_authenticated_client_a, periodo, conta_associacao):
    url = (
        f"/api/relacao-bens/previa/"
        f"?conta-associacao={conta_associacao.uuid}"
        f"&periodo={periodo.uuid}"
        f"&data_inicio=2019-09-01"
        f"&data_fim=2019-11-30"
    )
    with patch('sme_ptrf_apps.core.api.views.relacao_bens_viewset.gerar_previa_relacao_de_bens_async') as mock_task:
        mock_task.delay.return_value = None
        response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'mensagem': 'Arquivo na fila para processamento.'}
    mock_task.delay.assert_called_once()


# ---------------------------------------------------------------------------
# documento_final
# ---------------------------------------------------------------------------

def test_documento_final_sem_parametros_retorna_400(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get("/api/relacao-bens/documento-final/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['erro'] == 'parametros_requeridos'


def test_documento_final_formato_invalido_retorna_400(jwt_authenticated_client_a, periodo, conta_associacao):
    url = (
        f"/api/relacao-bens/documento-final/"
        f"?conta-associacao={conta_associacao.uuid}"
        f"&periodo={periodo.uuid}"
        f"&formato_arquivo=CSV"
    )
    response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['erro'] == 'parametro_inválido'


def test_documento_final_sem_relacao_bens_retorna_404(
        jwt_authenticated_client_a, periodo, conta_associacao, prestacao_conta):
    url = (
        f"/api/relacao-bens/documento-final/"
        f"?conta-associacao={conta_associacao.uuid}"
        f"&periodo={periodo.uuid}"
    )
    response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['erro'] == 'arquivo_nao_gerado'


def test_documento_final_arquivo_pdf_nao_acessivel_retorna_404(
        jwt_authenticated_client_a, periodo, conta_associacao, relacao_bens_final):
    url = (
        f"/api/relacao-bens/documento-final/"
        f"?conta-associacao={conta_associacao.uuid}"
        f"&periodo={periodo.uuid}"
        f"&formato_arquivo=PDF"
    )
    response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['erro'] == 'arquivo_nao_gerado'


def test_documento_final_arquivo_xlsx_nao_acessivel_retorna_404(
        jwt_authenticated_client_a, periodo, conta_associacao, relacao_bens_final):
    url = (
        f"/api/relacao-bens/documento-final/"
        f"?conta-associacao={conta_associacao.uuid}"
        f"&periodo={periodo.uuid}"
        f"&formato_arquivo=XLSX"
    )
    response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['erro'] == 'arquivo_nao_gerado'


# ---------------------------------------------------------------------------
# documento_previa
# ---------------------------------------------------------------------------

def test_documento_previa_sem_parametros_retorna_400(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get("/api/relacao-bens/documento-previa/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['erro'] == 'parametros_requeridos'


def test_documento_previa_formato_invalido_retorna_400(jwt_authenticated_client_a, periodo, conta_associacao):
    url = (
        f"/api/relacao-bens/documento-previa/"
        f"?conta-associacao={conta_associacao.uuid}"
        f"&periodo={periodo.uuid}"
        f"&formato_arquivo=CSV"
    )
    response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['erro'] == 'parametro_inválido'


def test_documento_previa_sem_relacao_bens_retorna_404(jwt_authenticated_client_a, periodo, conta_associacao):
    url = (
        f"/api/relacao-bens/documento-previa/"
        f"?conta-associacao={conta_associacao.uuid}"
        f"&periodo={periodo.uuid}"
    )
    response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['erro'] == 'arquivo_nao_gerado'


def test_documento_previa_arquivo_pdf_nao_acessivel_retorna_404(
        jwt_authenticated_client_a, periodo, conta_associacao, relacao_bens_previa):
    url = (
        f"/api/relacao-bens/documento-previa/"
        f"?conta-associacao={conta_associacao.uuid}"
        f"&periodo={periodo.uuid}"
        f"&formato_arquivo=PDF"
    )
    response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['erro'] == 'arquivo_nao_gerado'


def test_documento_previa_arquivo_xlsx_nao_acessivel_retorna_404(
        jwt_authenticated_client_a, periodo, conta_associacao, relacao_bens_previa):
    url = (
        f"/api/relacao-bens/documento-previa/"
        f"?conta-associacao={conta_associacao.uuid}"
        f"&periodo={periodo.uuid}"
        f"&formato_arquivo=XLSX"
    )
    response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['erro'] == 'arquivo_nao_gerado'


# ---------------------------------------------------------------------------
# pdf (detail action)
# ---------------------------------------------------------------------------

def test_pdf_arquivo_nao_acessivel_retorna_404(jwt_authenticated_client_a, relacao_bens_previa):
    response = jwt_authenticated_client_a.get(f"/api/relacao-bens/{relacao_bens_previa.uuid}/pdf/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['erro'] == 'arquivo_nao_gerado'
