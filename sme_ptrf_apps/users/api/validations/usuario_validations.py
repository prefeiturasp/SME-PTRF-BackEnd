import logging
from django.contrib.auth import get_user_model
from rest_framework import serializers
from sme_ptrf_apps.users.models import Visao
from sme_ptrf_apps.users.services import SmeIntegracaoException
from sme_ptrf_apps.core.models import Unidade

User = get_user_model()


logger = logging.getLogger(__name__)


def senhas_devem_ser_iguais(senha1, senha2):
    if senha1 != senha2:
        raise serializers.ValidationError({'detail': 'Senhas informadas devem ser iguais'})


def emails_devem_ser_iguais(email1, email2):
    if email1 != email2:
        raise serializers.ValidationError({'detail': 'Emails informados devem ser iguais'})


def registro_funcional_deve_existir(registro_funcional):
    user = get_user_model()
    usuario = user.objects.filter(username=registro_funcional).exists()
    if not usuario:
        raise serializers.ValidationError({'detail': 'Registro Funcional não foi encontrado'})


def senha_nao_pode_ser_nulo(senha, campo='Senha'):
    if senha is None or senha == 'string' or len(senha) == 0:
        raise serializers.ValidationError({'detail': 'O Campo {} deve ser preenchido'.format(campo)})


def hash_redefinicao_deve_existir(hash):
    existe = get_user_model().objects.filter(hash_redefinicao=hash).exists()
    if not existe:
        logger.info("Hash não existe")
        raise serializers.ValidationError({'detail': 'Hash de redefinicação não foi encontrado'})


def checa_senha(usuario, senha):
    if not usuario.check_password(senha):
        raise serializers.ValidationError({'detail': 'Senha atual incorreta'})


# user v2

class UnidadesDoUsuarioSerializer(serializers.Serializer): # noqa
    username = serializers.CharField(required=True)
    uuid_unidade = serializers.CharField(required=True)
    visao_base = serializers.CharField(required=True)

    def validate_username(self, value): # noqa
        try:
            usuario = User.objects.get(username=value)
        except User.DoesNotExist: # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o username {value}.")

        return value

    def validate_uuid_unidade(self, value): # noqa
        if value == 'SME':
            return value
        else:
            try:
                unidade = Unidade.objects.get(uuid=value)
            except Unidade.DoesNotExist:  # noqa
                raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {value}.")

            return value

    def validate_visao_base(self, value): # noqa
        if value == 'SME' or value == 'DRE':
            return value
        else:
            raise serializers.ValidationError(f"A visão {value} não é aceita como parametro.")


class HabilitarDesabilitarAcessoSerializer(serializers.Serializer): # noqa
    username = serializers.CharField(required=True)
    uuid_unidade = serializers.CharField(required=True, allow_null=False)
    visao_base = serializers.CharField(required=True)

    def validate_username(self, value): # noqa
        try:
            usuario = User.objects.get(username=value)
        except User.DoesNotExist: # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o username {value}.")

        return value

    def validate_uuid_unidade(self, value): # noqa
        if value == 'SME':
            return value
        else:
            try:
                unidade = Unidade.objects.get(uuid=value)
            except Unidade.DoesNotExist:  # noqa
                raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {value}.")

            return value
        
    def validate_visao_base(self, value): # noqa
        try:
            visao = Visao.objects.get(nome=value)
        except User.DoesNotExist: # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para a visão {value}.")

        return value


class UnidadesDisponiveisInclusaoSerializer(serializers.Serializer): # noqa
    username = serializers.CharField(required=True)
    search = serializers.CharField(required=True, allow_blank=False, allow_null=False)

    def validate_username(self, value): # noqa
        try:
            usuario = User.objects.get(username=value)
        except User.DoesNotExist: # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o username {value}.")

        return value


class IncluirUnidadeSerializer(serializers.Serializer): # noqa
    username = serializers.CharField(required=True)
    uuid_unidade = serializers.UUIDField(required=True, allow_null=False)

    def validate_username(self, value): # noqa
        try:
            usuario = User.objects.get(username=value)
        except User.DoesNotExist: # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o username {value}.")

        return value

    def validate_uuid_unidade(self, value): # noqa
        try:
            unidade = Unidade.objects.get(uuid=value)
        except Unidade.DoesNotExist:  # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {value}.")

        return value
