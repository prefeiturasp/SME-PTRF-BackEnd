import json
import pytest

from rest_framework import status


from sme_ptrf_apps.core.models import Arquivo

pytestmark = pytest.mark.django_db


def test_create_arquivo(
    jwt_authenticated_client_a,
    arquivo
):
    payload = {
        'identificador': 'teste_postman',
        'tipo_carga': 'CARGA_ASSOCIACOES',
        'tipo_delimitador': 'DELIMITADOR_PONTO_VIRGULA',
        'status': 'PENDENTE',
        'conteudo': arquivo
    }

    response = jwt_authenticated_client_a.post(
        '/api/arquivos/', data=payload, format='multipart')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Arquivo.objects.filter(uuid=result['uuid']).exists()

    assert Arquivo.objects.get(uuid=result['uuid']).conteudo == arquivo
