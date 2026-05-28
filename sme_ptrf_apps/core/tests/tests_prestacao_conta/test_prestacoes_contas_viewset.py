import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.prestacoes_contas_viewset import PrestacoesContasViewSet

pytestmark = pytest.mark.django_db


# =========================
# VIEW BASE
# =========================
def _call_view(api_request_factory, view, user, **kwargs):
    request = api_request_factory.get("")
    force_authenticate(request, user=user)
    return view(request, **kwargs)


def test_view_set(prestacao_conta, usuario_permissao_associacao):
    request = APIRequestFactory().get("")
    detalhe = PrestacoesContasViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=prestacao_conta.uuid)

    assert response.status_code == status.HTTP_200_OK


# =========================
# SEM PAA
# =========================
def test_sem_paa(
    prestacao_conta,
    usuario_permissao_associacao,
    api_request_factory,
    prestacao_uuid_view,
):
    response = _call_view(
        api_request_factory,
        prestacao_uuid_view,
        usuario_permissao_associacao,
        uuid=prestacao_conta.uuid,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["uuid"] is None
    assert "Nenhum PAA encontrado" in response.data[0]["mensagem_geracao"]


# =========================
# SEM DOCUMENTOS
# =========================
def test_sem_documentos(
    prestacao_conta,
    usuario_permissao_associacao,
    api_request_factory,
    prestacao_uuid_view,
    paa_base,
):
    response = _call_view(
        api_request_factory,
        prestacao_uuid_view,
        usuario_permissao_associacao,
        uuid=prestacao_conta.uuid,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["nome"] == "Plano Anual"


# =========================
# DOCUMENTO ORIGINAL
# =========================
def test_documento_original(
    prestacao_conta,
    usuario_permissao_associacao,
    api_request_factory,
    prestacao_uuid_view,
    documento_paa_com_arquivo,
):
    response = _call_view(
        api_request_factory,
        prestacao_uuid_view,
        usuario_permissao_associacao,
        uuid=prestacao_conta.uuid,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["tipo_documento"] == "documento-paa"
    assert "Documento PAA final" in response.data[0]["nome"]


# =========================
# ATA
# =========================
def test_ata(
    prestacao_conta,
    usuario_permissao_associacao,
    api_request_factory,
    prestacao_uuid_view,
    ata_apresentacao,
):
    response = _call_view(
        api_request_factory,
        prestacao_uuid_view,
        usuario_permissao_associacao,
        uuid=prestacao_conta.uuid,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["tipo_documento"] == "documento-ata"
