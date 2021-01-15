import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_retrieve_periodo(
    jwt_authenticated_client_a,
    periodo_2021_2
):
    response = jwt_authenticated_client_a.get(
        f'/api/periodos/{periodo_2021_2.uuid}/', content_type='application/json')

    result = json.loads(response.content)

    p = periodo_2021_2

    esperado = {
        "uuid": f'{p.uuid}',
        "id": p.id,
        "referencia": p.referencia,
        "data_inicio_realizacao_despesas": f'{p.data_inicio_realizacao_despesas}' if p.data_inicio_realizacao_despesas else None,
        "data_fim_realizacao_despesas": f'{p.data_fim_realizacao_despesas}' if p.data_fim_realizacao_despesas else None,
        "data_prevista_repasse": f'{p.data_prevista_repasse}' if p.data_prevista_repasse else None,
        "data_inicio_prestacao_contas": f'{p.data_inicio_prestacao_contas}' if p.data_inicio_prestacao_contas else None,
        "data_fim_prestacao_contas": f'{p.data_fim_prestacao_contas}' if p.data_fim_prestacao_contas else None,
        "periodo_anterior": {
            "uuid": f'{p.periodo_anterior.uuid}',
            "referencia": p.periodo_anterior.referencia,
            "data_inicio_realizacao_despesas": f'{p.periodo_anterior.data_inicio_realizacao_despesas}' if p.periodo_anterior.data_inicio_realizacao_despesas else None,
            "data_fim_realizacao_despesas": f'{p.periodo_anterior.data_fim_realizacao_despesas}' if p.periodo_anterior.data_fim_realizacao_despesas else None,
            "referencia_por_extenso": f"{p.periodo_anterior.referencia.split('.')[1]}° repasse de {p.referencia.split('.')[0]}"
        },
        "editavel": p.editavel,
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
