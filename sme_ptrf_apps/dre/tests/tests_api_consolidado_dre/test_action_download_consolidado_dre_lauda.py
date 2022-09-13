import mimetypes

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_download_lauda(
    jwt_authenticated_client_dre,
    lauda_teste_api,
    consolidado_dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    dre_teste_api_consolidado_dre,
    arquivo_gerado_lauda_teste_api,
    tipo_conta_cheque_teste_api,
    usuario_dre_teste_api,
):

    lauda_uuid = lauda_teste_api.uuid
    arquivo_nome = lauda_teste_api.arquivo_lauda_txt.name
    arquivo_path = lauda_teste_api.arquivo_lauda_txt.path
    arquivo_file_mime = mimetypes.guess_type(lauda_teste_api.arquivo_lauda_txt.name)[0]

    url = f'/api/consolidados-dre/download-lauda/?lauda={lauda_uuid}'

    response = jwt_authenticated_client_dre.get(url)

    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Disposition'][0] == f'attachment; filename={arquivo_nome}'
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Type'][0] == f'{arquivo_file_mime}'
    assert response.status_code == status.HTTP_200_OK
