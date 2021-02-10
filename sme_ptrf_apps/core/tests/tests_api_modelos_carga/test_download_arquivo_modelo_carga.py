import pytest

from rest_framework import status

from sme_ptrf_apps.core.choices.tipos_carga import CARGA_ASSOCIACOES

pytestmark = pytest.mark.django_db


def test_download_arquivo_modelo_carga(jwt_authenticated_client, modelo_carga_associacao):
    response = jwt_authenticated_client.get(f'/api/modelos-cargas/{CARGA_ASSOCIACOES}/download/')

    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Disposition'][0] == f'attachment; filename={modelo_carga_associacao.arquivo.name}'
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Type'][0] == 'text/csv'
    assert response.status_code == status.HTTP_200_OK
