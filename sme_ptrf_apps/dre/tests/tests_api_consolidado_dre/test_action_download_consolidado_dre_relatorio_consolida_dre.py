import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_relatorio_final(
    jwt_authenticated_client_relatorio_consolidado,
    periodo_teste_api_consolidado_dre,
    dre_teste_api_consolidado_dre,
    tipo_conta_cheque_teste_api,
    relatorio_dre_consolidado_gerado_final_teste_api,
    ano_analise_regularidade_2022_teste_api
):

    relatorio_uuid = relatorio_dre_consolidado_gerado_final_teste_api.uuid

    url = f'/api/consolidados-dre/{relatorio_uuid}/download/'

    response = jwt_authenticated_client_relatorio_consolidado.get(url)

    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Disposition'][0] == 'attachment; filename=relatorio_fisico_financeiro_dre.pdf'
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Type'][0] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert response.status_code == status.HTTP_200_OK
