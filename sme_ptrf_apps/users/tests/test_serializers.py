import pytest
from unittest.mock import patch
from sme_ptrf_apps.users.api.serializers import RedefinirSenhaSerializer, AlteraEmailSerializer, UserCreateSerializer
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
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


@pytest.mark.django_db
def test_create_usuario_erro_core_sso_nao_cria_usuario():
    payload = {
        "username": "teste.user",
        "email": "teste@teste.com",
        "name": "Usuário Teste",
        "e_servidor": True,
        "unidade": "123456",
        "visao": "ADMIN",
    }

    serializer = UserCreateSerializer(data=payload)
    assert serializer.is_valid(), serializer.errors

    with patch(
        "sme_ptrf_apps.users.api.serializers.user.cria_ou_atualiza_usuario_core_sso",
        side_effect=Exception("Erro no CoreSSO"),
    ) as mock_core_sso:

        with pytest.raises(ValidationError) as exc:
            serializer.save()

    mock_core_sso.assert_called_once()
    assert User.objects.filter(username="teste.user").exists() is False
    assert "Erro ao tentar cria/atualizar usuário" in str(exc.value)


@pytest.mark.django_db
def test_update_usuario_erro_core_sso_nao_atualiza_usuario():
    user = User.objects.create(
        username="teste.user",
        email="original@teste.com",
        name="Nome Original",
        e_servidor=True,
    )

    payload = {
        "username": "teste.user",
        "email": "novo@teste.com",
        "name": "Nome Alterado",
        "e_servidor": True,
        "unidade": "999999",
        "visao": "ADMIN",
    }

    serializer = UserCreateSerializer(instance=user, data=payload)
    assert serializer.is_valid(), serializer.errors

    with patch(
        "sme_ptrf_apps.users.api.serializers.user.cria_ou_atualiza_usuario_core_sso",
        side_effect=Exception("Falha CoreSSO"),
    ):
        with pytest.raises(ValidationError):
            serializer.save()

    user.refresh_from_db()
    assert user.email == "original@teste.com"
    assert user.name == "Nome Original"
