from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.prestacoes_contas_viewset import PrestacoesContasViewSet
from sme_ptrf_apps.paa.models import Paa


def _call_view(api_request_factory, view, user, **kwargs):
    request = api_request_factory.get("")
    force_authenticate(request, user=user)
    return view(request, **kwargs)


def test_view_set(prestacao_conta, usuario_permissao_associacao):
    """Garante que a rota base de retrieve está respondendo corretamente."""
    request = APIRequestFactory().get("")
    detalhe = PrestacoesContasViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=prestacao_conta.uuid)

    assert response.status_code == status.HTTP_200_OK


def test_sem_paa(
    prestacao_conta,
    usuario_permissao_associacao,
    api_request_factory,
    prestacao_uuid_view,
):
    """Cenário onde nenhum PAA coincide com os filtros da query (404 Not Found)."""
    response = _call_view(
        api_request_factory,
        prestacao_uuid_view,
        usuario_permissao_associacao,
        uuid=prestacao_conta.uuid,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "Nenhum PAA encontrado para o período informado"


@patch('django.db.models.query.QuerySet.first')
@patch.object(Paa, 'get_documentos')
def test_sem_documentos(
    mock_get_documentos,
    mock_first,
    prestacao_conta,
    usuario_permissao_associacao,
    api_request_factory,
    prestacao_uuid_view,
    paa_base,
):
    """
    Cenário onde o PAA existe, mas todos os documentos retornam None.
    Os retificados devem ser removidos pelo filtro interno da nova action.
    """

    mock_get_documentos.return_value = (None, None, None, None)
    mock_first.return_value = paa_base

    response = _call_view(
        api_request_factory,
        prestacao_uuid_view,
        usuario_permissao_associacao,
        uuid=prestacao_conta.uuid,
    )

    assert response.status_code == status.HTTP_200_OK

    assert len(response.data) == 2
    assert response.data[0]["nome"] == "Plano Anual-Documento pendente de geração"
    assert response.data[0]["tipo"] == "DOC-PAA"
    assert response.data[1]["tipo"] == "ATA-PAA"


@patch('django.db.models.query.QuerySet.first')
@patch.object(Paa, 'get_documentos')
def test_documento_original(
    mock_get_documentos,
    mock_first,
    prestacao_conta,
    usuario_permissao_associacao,
    api_request_factory,
    prestacao_uuid_view,
    paa_base,
    documento_paa_com_arquivo,
):
    """Cenário onde existe um documento original gerado anexado ao PAA."""
    mock_get_documentos.return_value = (documento_paa_com_arquivo, None, None, None)
    mock_first.return_value = paa_base

    response = _call_view(
        api_request_factory,
        prestacao_uuid_view,
        usuario_permissao_associacao,
        uuid=prestacao_conta.uuid,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["tipo"] == "DOC-PAA"
    assert "Plano Anual-" in response.data[0]["nome"]
    assert response.data[0]["uuid"] == str(documento_paa_com_arquivo.uuid)


@patch('django.db.models.query.QuerySet.first')
@patch.object(Paa, 'get_documentos')
def test_ata(
    mock_get_documentos,
    mock_first,
    prestacao_conta,
    usuario_permissao_associacao,
    api_request_factory,
    prestacao_uuid_view,
    paa_base,
    ata_apresentacao,
):
    """Cenário onde existe a ata de apresentação do PAA gerada."""
    mock_get_documentos.return_value = (None, ata_apresentacao, None, None)
    mock_first.return_value = paa_base

    response = _call_view(
        api_request_factory,
        prestacao_uuid_view,
        usuario_permissao_associacao,
        uuid=prestacao_conta.uuid,
    )

    assert response.status_code == status.HTTP_200_OK

    ata_doc = next((item for item in response.data if item["tipo"] == "ATA-PAA"), None)

    assert ata_doc is not None
    assert "Ata de Apresentação do PAA-" in ata_doc["nome"]
    assert ata_doc["uuid"] == str(ata_apresentacao.uuid)
