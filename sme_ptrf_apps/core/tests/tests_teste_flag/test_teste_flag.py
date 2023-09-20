import json
import pytest
from rest_framework import status
from waffle.testutils import override_flag

pytestmark = pytest.mark.django_db


@override_flag('teste-flag', active=True)
def test_view_teste_flag_flag_ligada(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(f'/api/teste-flag', content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    assert json.loads(response.content) == {'mensagem': 'Se está vendo essa mensagem é porque a teste-flag está ativa.'}


@override_flag('teste-flag', active=False)
def test_view_teste_flag_flag_desligada(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(f'/api/teste-flag', content_type='application/json')
    assert response.status_code == status.HTTP_404_NOT_FOUND


@override_flag('teste-flag', active=True)
def test_view_versao_flag_ligada(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(f'/api/versao', content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    assert json.loads(response.content) == {'versao': 'teste-flag'}


@override_flag('teste-flag', active=False)
def test_view_versao_flag_desligada(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(f'/api/versao', content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    assert json.loads(response.content) != {'versao': 'teste-flag'}
