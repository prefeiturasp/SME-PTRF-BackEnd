import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_action_repasses_pendentes_por_periodo(jwt_authenticated_client_a, associacao, periodo, repasse):
    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/{associacao.uuid}/repasses-pendentes-por-periodo/?periodo_uuid={periodo.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    esperado = [
        {
            'repasse_periodo': repasse.periodo.referencia,
            'repasse_acao': repasse.acao_associacao.acao.nome,
            'repasse_total': round(repasse.valor_capital + repasse.valor_custeio + repasse.valor_livre, 2),
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
