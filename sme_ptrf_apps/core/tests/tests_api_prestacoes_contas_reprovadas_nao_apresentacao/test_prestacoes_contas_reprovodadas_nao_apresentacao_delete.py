import json
import pytest
from rest_framework import status
from waffle.testutils import override_flag

pytestmark = pytest.mark.django_db


@override_flag('pc-reprovada-nao-apresentacao', active=True)
def test_delete(jwt_authenticated_client_a, prestacao_conta_reprovada_nao_apresentacao_factory):

    pc = prestacao_conta_reprovada_nao_apresentacao_factory.create()

    url = f'/api/prestacoes-contas-reprovadas-nao-apresentacao/{pc.uuid}/'

    response = jwt_authenticated_client_a.delete(url, content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT
