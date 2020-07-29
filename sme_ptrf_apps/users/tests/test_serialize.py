import pytest
from unittest.mock import patch
from sme_ptrf_apps.users.api.serializers import RedefinirSenhaSerializer, AlteraEmailSerializer
from rest_framework.response import Response
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db

User = get_user_model()


def test_alterar_senha_serialize(usuario):
    path = "sme_ptrf_apps.users.api.serializers.user.SmeIntegracaoService.redefine_senha"
    with patch(path) as mock_method:
        mock_method.return_value = "Ok"
        payload = {
            "password_atual": 'Sgp0418',
            "password": '123456qw',
            "password2": '123456qw'
        }
        user = User.objects.filter(username=usuario.username).get()
        serializer = RedefinirSenhaSerializer()
        validated_data = serializer.validate(payload)
        assert validated_data
        instance = serializer.update(usuario, validated_data)
        assert not isinstance(instance, Response)
        assert user.password != usuario.password
        assert True


def test_alterar_email_serialize(usuario):
    path = "sme_ptrf_apps.users.api.serializers.user.SmeIntegracaoService.redefine_email"
    with patch(path) as mock_method:
        mock_method.return_value = "Ok"
        payload = {
            "email": 'sme2@amcom.com.br',
            "email2": 'sme2@amcom.com.br'
        }
        user = User.objects.filter(username=usuario.username).get()
        serializer = AlteraEmailSerializer()
        validated_data = serializer.validate(payload)
        assert validated_data
        instance = serializer.update(usuario, validated_data)
        assert not isinstance(instance, Response)
        assert user.email != usuario.email
        assert True
