import json

import pytest
from model_bakery import baker

from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def parametro_fique_de_olho_rel_dre_abc():
    return baker.make(
        'ParametroFiqueDeOlhoRelDre',
        fique_de_olho='abc',
    )


def test_api_get_status_relatorio_analise_completa_rel_nao_gerado(jwt_authenticated_client_relatorio_consolidado,
                                                                  parametro_fique_de_olho_rel_dre_abc):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/fique-de-olho/',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {'detail': 'abc'}

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
