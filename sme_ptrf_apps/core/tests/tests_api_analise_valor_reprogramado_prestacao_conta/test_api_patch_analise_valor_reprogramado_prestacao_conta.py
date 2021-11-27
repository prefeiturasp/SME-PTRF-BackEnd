import json
from decimal import Decimal

import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import AnaliseValorReprogramadoPrestacaoConta

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_patch_analise_valor_reprogramado(analise_valor_reprogramado_por_acao):
    payload = {
        "valor_saldo_reprogramado_correto": False,
        "novo_saldo_reprogramado_custeio": "5.00",
        "novo_saldo_reprogramado_capital": "5.00",
        "novo_saldo_reprogramado_livre": None
    }
    return payload


def test_patch_analise_valor_reprogramado(jwt_authenticated_client_a, analise_valor_reprogramado_por_acao, payload_patch_analise_valor_reprogramado):

    response = jwt_authenticated_client_a.patch(
        f'/api/analises-valores-reprogramados/{analise_valor_reprogramado_por_acao.uuid}/',
        data=json.dumps(payload_patch_analise_valor_reprogramado),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
    assert AnaliseValorReprogramadoPrestacaoConta.objects.get(uuid=analise_valor_reprogramado_por_acao.uuid).novo_saldo_reprogramado_custeio == Decimal(payload_patch_analise_valor_reprogramado['novo_saldo_reprogramado_custeio'])
