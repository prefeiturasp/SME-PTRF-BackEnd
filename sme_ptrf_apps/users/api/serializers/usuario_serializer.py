# TODO Substitui serializers/user.py que deve ser removida ao fim da implantação da nova gestão de usuários.

import logging

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from sme_ptrf_apps.users.services import cria_ou_atualiza_usuario_core_sso
from sme_ptrf_apps.users.models import Grupo, Visao, UnidadeEmSuporte

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
    acesso_de_suporte = SerializerMethodField()

    class Meta:
        model = Unidade
        fields = ['uuid', 'nome', 'codigo_eol', 'tipo_unidade', 'acesso_de_suporte']

    def get_acesso_de_suporte(self, instance):
        user = self.context["user"]
        return UnidadeEmSuporte.objects.filter(unidade=instance, user=user).exists()


class UsuarioSerializer(serializers.ModelSerializer):
    groups = SerializerMethodField()
    unidades = SerializerMethodField()
    visoes = SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "name", "url", "e_servidor", "groups", "unidades", "visoes"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"}
        }

    def get_groups(self, instance):
        """
        Retorna a versão estendida dos grupos do usuário que inclui as informações de visões e descrição.
        """
        visao_consulta = self.context.get('visao_consulta')
        groups_padrao = instance.groups.values_list("id", flat=True)
        groups_extendido = Grupo.objects.filter(id__in=groups_padrao).order_by('id')

        if visao_consulta == 'UE':
            groups_extendido = groups_extendido.filter(visoes__nome='UE')
        elif visao_consulta == 'DRE':
            groups_extendido = groups_extendido.exclude(visoes__nome='SME')

        return GrupoComVisaoSerializer(groups_extendido, many=True).data

    def get_unidades(selfself, instance):
        return UnidadeSerializer(instance.unidades, many=True, context={'user': instance}).data

    def get_visoes(selfself, instance):
        return VisaoSerializer(instance.visoes, many=True).data

class UsuarioRetrieveSerializer(serializers.ModelSerializer):
    visoes = VisaoSerializer(many=True)
    groups = SerializerMethodField()
    unidades = SerializerMethodField()

    def get_groups(self, instance):
        """
        Retorna a versão estendida dos grupos do usuário que inclui as informações de visões e descrição.
        """
        groups_padrao = instance.groups.values_list("id", flat=True)
        groups_extendido = Grupo.objects.filter(id__in=groups_padrao).order_by('id')
        return GrupoComVisaoSerializer(groups_extendido, many=True).data

    def get_unidades(selfself, instance):
        return UnidadeSerializer(instance.unidades, many=True, context={'user': instance}).data

    class Meta:
        model = User
        fields = ["id", "username", "email", "name", "url", "e_servidor", "groups", "unidades", "visoes"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"}
        }


class UsuarioCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "name", "e_servidor", "id"]

    def create(self, validated_data):
        dados_usuario = {
            "login": validated_data["username"],
            "email": validated_data["email"],
            "nome": validated_data["name"],
            "servidor_s_n": "S" if validated_data["e_servidor"] else "N",
        }

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
            "email": validated_data["email"],
            "nome": validated_data["name"],
            "servidor_s_n": "S" if validated_data["e_servidor"] else "N",
        }

        try:
            cria_ou_atualiza_usuario_core_sso(
                dados_usuario=dados_usuario
            )
            logger.info(f'Usuário {validated_data["username"]} criado/atualizado no CoreSSO com sucesso.')

        except Exception as e:
            logger.error(f'Erro ao tentar cria/atualizar usuário {validated_data["username"]} no CoreSSO: {str(e)}')

        return super().update(instance, validated_data)
