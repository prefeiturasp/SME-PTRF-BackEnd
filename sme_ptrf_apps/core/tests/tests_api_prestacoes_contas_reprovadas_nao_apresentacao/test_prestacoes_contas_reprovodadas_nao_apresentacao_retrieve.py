import json
import pytest
from rest_framework import status
from waffle.testutils import override_flag

pytestmark = pytest.mark.django_db


@override_flag('pc-reprovada-nao-apresentacao', active=True)
def test_retrieve(jwt_authenticated_client_a, prestacao_conta_reprovada_nao_apresentacao_factory):

    pc = prestacao_conta_reprovada_nao_apresentacao_factory.create()

    url = f'/api/prestacoes-contas-reprovadas-nao-apresentacao/{pc.uuid}/'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert f"{pc.uuid}" == result["uuid"]

    assert response.status_code == status.HTTP_200_OK

