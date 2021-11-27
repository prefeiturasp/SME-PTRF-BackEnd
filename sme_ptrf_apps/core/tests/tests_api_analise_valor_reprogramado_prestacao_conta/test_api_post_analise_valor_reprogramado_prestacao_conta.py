import json
import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import AnaliseValorReprogramadoPrestacaoConta

pytestmark = pytest.mark.django_db


def test_create_analise_valor_reprogramado(jwt_authenticated_client_a, analise_prestacao_conta_2020_1, conta_associacao,
                                           acao_associacao):
    payload_nova_analise = {
        "analise_prestacao_conta": f'{analise_prestacao_conta_2020_1.uuid}',
        "conta_associacao": f'{conta_associacao.uuid}',
        "acao_associacao": f'{acao_associacao.uuid}',
        "valor_saldo_reprogramado_correto": True,
        "novo_saldo_reprogramado_custeio": None,
        "novo_saldo_reprogramado_capital": None,
        "novo_saldo_reprogramado_livre": None
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-valores-reprogramados/', data=json.dumps(payload_nova_analise), content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED
    assert AnaliseValorReprogramadoPrestacaoConta.objects.filter(uuid=result['uuid']).exists()
