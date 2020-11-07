import json

import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_list_comentarios_analise_prestacao(jwt_authenticated_client, justificativa_relatorio_dre_consolidado):
    dre_uuid = justificativa_relatorio_dre_consolidado.dre.uuid
    periodo_uuid = justificativa_relatorio_dre_consolidado.periodo.uuid
    tipo_conta_uuid = justificativa_relatorio_dre_consolidado.tipo_conta.uuid

    response = jwt_authenticated_client.get(f'/api/justificativas-relatorios-consolidados-dre/?dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&tipo_conta__uuid={tipo_conta_uuid}',
                          content_type='application/json')

    result = json.loads(response.content)

    esperado = [
        {
            'uuid': f'{justificativa_relatorio_dre_consolidado.uuid}',
            'dre': f'{dre_uuid}',
            'tipo_conta': f'{tipo_conta_uuid}',
            'periodo': f'{periodo_uuid}',
            'texto': 'Teste',
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado, "Não retornou o resultado esperado"
