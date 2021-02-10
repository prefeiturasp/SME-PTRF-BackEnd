import json
import pytest


from rest_framework import status

from sme_ptrf_apps.core.models import Arquivo

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_update_arquivo(arquivo2):
    payload = {
        'identificador': 'alterado',
        'conteudo': arquivo2
    }
    return payload


def test_update_arquivo(
    jwt_authenticated_client_a,
    arquivo_carga,
    payload_update_arquivo,
    arquivo,
    arquivo2
):

    assert Arquivo.objects.get(uuid=arquivo_carga.uuid).identificador == 'carga_previsao_repasse'
    assert Arquivo.objects.get(uuid=arquivo_carga.uuid).conteudo == arquivo

    response = jwt_authenticated_client_a.patch(
        f'/api/arquivos/{arquivo_carga.uuid}/', data=payload_update_arquivo, format='multipart')

    assert response.status_code == status.HTTP_200_OK

    assert Arquivo.objects.get(uuid=arquivo_carga.uuid).identificador == 'alterado'
    assert Arquivo.objects.get(uuid=arquivo_carga.uuid).conteudo == arquivo2
