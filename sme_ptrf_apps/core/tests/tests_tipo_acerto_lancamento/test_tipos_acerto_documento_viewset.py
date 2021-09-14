import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.tipos_acerto_documento_viewset import TiposAcertoDocumentoViewSet

pytestmark = pytest.mark.django_db


@pytest.fixture
def tipo_documento_prestacao_conta_ata():
    return baker.make('TipoDocumentoPrestacaoConta', nome='Cópia da ata da prestação de contas')


@pytest.fixture
def tipo_acerto_documento_assinatura(tipo_documento_prestacao_conta_ata):
    tipo_acerto = baker.make('TipoAcertoDocumento', nome='Enviar com assinatura')
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_ata)
    tipo_acerto.save()
    return tipo_acerto


def test_view_set(tipo_acerto_documento_assinatura, usuario_permissao_associacao):
    request = APIRequestFactory().get("")
    detalhe = TiposAcertoDocumentoViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=tipo_acerto_documento_assinatura.uuid)

    assert response.status_code == status.HTTP_200_OK
