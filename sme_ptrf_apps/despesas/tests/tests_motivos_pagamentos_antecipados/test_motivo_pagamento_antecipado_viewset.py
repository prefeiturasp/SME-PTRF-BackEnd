import pytest

from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.motivos_pagamento_antecipado_viewset import MotivosPagamentoAntecipadoViewSet

pytestmark = pytest.mark.django_db


def test_view_set(motivo_pagamento_adiantado_01, usuario_permissao_despesa):
    request = APIRequestFactory().get("")
    detalhe = MotivosPagamentoAntecipadoViewSet.as_view({"get": "retrieve"})
    force_authenticate(request, user=usuario_permissao_despesa)
    response = detalhe(request, uuid=motivo_pagamento_adiantado_01.uuid)

    assert response.status_code == status.HTTP_200_OK
