import logging

from django.contrib.auth import get_user_model
from requests import ConnectTimeout, ReadTimeout
from rest_framework import serializers, status, exceptions
from rest_framework.fields import SerializerMethodField
from rest_framework.response import Response

from sme_ptrf_apps.users.api.validations.usuario_validations import (
    checa_senha,
    emails_devem_ser_iguais,
    senha_nao_pode_ser_nulo,
    senhas_devem_ser_iguais,
)
from sme_ptrf_apps.users.services import (SmeIntegracaoException, SmeIntegracaoService,
                                          cria_ou_atualiza_usuario_core_sso)
from sme_ptrf_apps.users.models import Grupo, Visao

from ....core.models import Unidade

User = get_user_model()
logger = logging.getLogger(__name__)


class VisaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visao
        fields = ['nome', 'id']


class GrupoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grupo
        fields = ['id', 'name', 'descricao']


class GrupoComVisaoSerializer(serializers.ModelSerializer):
    visoes = VisaoSerializer(many=True)

    class Meta:
        model = Grupo
        fields = ['id', 'name', 'descricao', 'visoes']


class UnidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidade
        fields = ['uuid', 'nome', 'codigo_eol', 'tipo_unidade']


class UserSerializer(serializers.ModelSerializer):
    groups = SerializerMethodField()
    unidades = UnidadeSerializer(many=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "name", "url", "e_servidor", "groups", "unidades"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"}
        }

    def get_groups(self, instance):
        groups = instance.groups.order_by('id')
        return GrupoSerializer(groups, many=True).data


class UserRetrieveSerializer(serializers.ModelSerializer):
    visoes = VisaoSerializer(many=True)
    groups = GrupoComVisaoSerializer(many=True)
    unidades = UnidadeSerializer(many=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "name", "url", "e_servidor", "groups", "unidades", "visoes"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"}
        }


class UserLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class UserCreateSerializer(serializers.ModelSerializer):
    visao = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    unidade = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = ["username", "email", "name", "e_servidor", "visao", "groups", "unidade", "visoes"]

    def create(self, validated_data):
        dados_usuario = {
            "login": validated_data["username"],
            "eol_unidade": validated_data["unidade"],
            "email": validated_data["email"],
            "nome": validated_data["name"],
            "servidor_s_n": "S" if validated_data["e_servidor"] else "N",
        }

        # O usuário pode ser criado informando uma visão ou uma lista de visões
        if "visao" in validated_data:
            dados_usuario["visao"] = validated_data["visao"]
        elif "visoes" in validated_data:
            dados_usuario["visoes"] = validated_data["visoes"]

        try:
            cria_ou_atualiza_usuario_core_sso(
                dados_usuario=dados_usuario
            )
            logger.info(f'Usuário {validated_data["username"]} criado/atualizado no CoreSSO com sucesso.')

        except Exception as e:
            logger.error(f'Erro ao tentar cria/atualizar usuário {validated_data["username"]} no CoreSSO: {str(e)}')

        user = User.criar_usuario(dados=validated_data)

        return user

    def update(self, instance, validated_data):
        dados_usuario = {
            "login": validated_data["username"],
            "eol_unidade": validated_data["unidade"],
            "email": validated_data["email"],
            "nome": validated_data["name"],
            "servidor_s_n": "S" if validated_data["e_servidor"] else "N",
        }

        # O usuário pode ser criado informando uma visão ou uma lista de visões
        if "visao" in validated_data:
            dados_usuario["visao"] = validated_data["visao"]
        elif "visoes" in validated_data:
            dados_usuario["visoes"] = validated_data["visoes"]

        try:
            cria_ou_atualiza_usuario_core_sso(
                dados_usuario=dados_usuario
            )
            logger.info(f'Usuário {validated_data["username"]} criado/atualizado no CoreSSO com sucesso.')

        except Exception as e:
            logger.error(f'Erro ao tentar cria/atualizar usuário {validated_data["username"]} no CoreSSO: {str(e)}')

        visao = validated_data.pop('visao') if 'visao' in validated_data else None
        if visao:
            instance.add_visao_se_nao_existir(visao=visao)

        unidade = validated_data.pop('unidade')
        if unidade:
            instance.add_unidade_se_nao_existir(codigo_eol=unidade)

        return super().update(instance, validated_data)


class AlteraEmailSerializer(serializers.ModelSerializer):
    email2 = serializers.EmailField(required=False)

    def validate(self, attrs):
        emails_devem_ser_iguais(attrs.get('email'), attrs.get('email2'))
        attrs.pop('email2')
        return attrs

    def update(self, instance, validated_data):
        try:
            SmeIntegracaoService.redefine_email(instance.username, validated_data['email'])
            instance.email = validated_data.get('email')
            instance.save()
        except SmeIntegracaoException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ReadTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        return instance

    class Meta:
        model = User
        fields = ["uuid", "username", "email", "email2"]


class RedefinirSenhaSerializer(serializers.ModelSerializer):
    password_atual = serializers.CharField(required=True)
    password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        senha_nao_pode_ser_nulo(attrs.get('password_atual'))
        senha_nao_pode_ser_nulo(attrs.get('password'))
        senha_nao_pode_ser_nulo(attrs.get('password2'))
        senhas_devem_ser_iguais(attrs.get('password'), attrs.get('password2'))
        attrs.pop('password2')
        return attrs

    def update(self, instance, validated_data):
        try:
            checa_senha(instance, validated_data['password_atual'])
            SmeIntegracaoService.redefine_senha(instance.username, validated_data['password'])
            instance.set_password(validated_data.get('password'))
            instance.hash_redefinicao = ''
            instance.save()
        except SmeIntegracaoException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ReadTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({'detail': str(err)}, status=status.HTTP_400_BAD_REQUEST)

        return instance

    class Meta:
        model = User
        fields = ['password_atual', 'password', 'password2']
