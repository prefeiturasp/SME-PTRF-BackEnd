import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_download_ata_parecer_tecnico(
    jwt_authenticated_client_dre,
    ata_parecer_tecnico_teste_api,
    consolidado_dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    dre_teste_api_consolidado_dre,
    arquivo_gerado_ata_parecer_tecnico_teste_api
):

    ata_uuid = ata_parecer_tecnico_teste_api.uuid

    url = f'/api/consolidados-dre/download-ata-parecer-tecnico/?ata={ata_uuid}'

    response = jwt_authenticated_client_dre.get(url)

    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Disposition'][0] == 'attachment; filename=ata_parecer_tecnico.pdf'
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Type'][0] == 'application/pdf'
    assert response.status_code == status.HTTP_200_OK
