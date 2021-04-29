import json
import pytest

from django.contrib.auth import get_user_model
from rest_framework import status

pytestmark = pytest.mark.django_db

def test_criar_usuario_servidor(
        jwt_authenticated_client_u,
        grupo_1,
        visao_ue,
        unidade_ue_271170,
):

    payload = {
        'e_servidor': True,
        'username': "9876543",
        'name': "Lukaku Silva",
        'email': 'lukaku@gmail.com',
        'visao': "UE",
        'groups': [
            grupo_1.id,
        ],
        'unidade': unidade_ue_271170.codigo_eol
    }

    response = jwt_authenticated_client_u.post(
        "/api/usuarios/", data=json.dumps(payload), content_type='application/json')
    result = response.json()

    esperado = {
        'username': '9876543',
        'email': 'lukaku@gmail.com',
        'name': 'Lukaku Silva',
        'e_servidor': True,
        'groups': [grupo_1.id,],
    }
    User = get_user_model()
    u = User.objects.filter(username='9876543').first()

    assert list(u.visoes.values_list('nome', flat=True)) == ["UE",]
    assert list(u.unidades.values_list('codigo_eol', flat=True)) == [unidade_ue_271170.codigo_eol,]
    assert response.status_code == status.HTTP_201_CREATED
    assert result == esperado


def test_criar_usuario_servidor_sem_email_e_sem_nome(
        jwt_authenticated_client_u,
        grupo_1,
        visao_ue,
        unidade_ue_271170
):

    payload = {
        'e_servidor': True,
        'username': "9876543",
        'name': "",
        'email': "",
        'visao': "UE",
        'groups': [
            grupo_1.id,
        ],
        'unidade': unidade_ue_271170.codigo_eol
    }
    response = jwt_authenticated_client_u.post(
        "/api/usuarios/", data=json.dumps(payload), content_type='application/json')
    result = response.json()
    esperado = {
        'username': '9876543',
        'email': '',
        'name': '',
        'e_servidor': True,
        'groups': [grupo_1.id,]
    }
    User = get_user_model()
    u = User.objects.filter(username='9876543').first()

    assert list(u.visoes.values_list('nome', flat=True)) == ["UE",]
    assert list(u.unidades.values_list('codigo_eol', flat=True)) == [unidade_ue_271170.codigo_eol,]
    assert response.status_code == status.HTTP_201_CREATED
    assert result == esperado
