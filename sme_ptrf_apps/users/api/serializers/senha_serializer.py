import logging
from django.contrib.auth import get_user_model
from requests import ConnectTimeout, ReadTimeout
from rest_framework import serializers, status
from rest_framework.response import Response

from sme_ptrf_apps.users.api.validations.usuario_validations import (
    hash_redefinicao_deve_existir,
    registro_funcional_deve_existir,
    senha_nao_pode_ser_nulo,
    senhas_devem_ser_iguais,
)
from sme_ptrf_apps.users.services import SmeIntegracaoService, SmeIntegracaoException
from sme_ptrf_apps.users.tasks import enviar_email_redifinicao_senha

User = get_user_model()

logger = logging.getLogger(__name__)


class EmailNaoCadastrado(Exception):
    pass


class ProblemaEnvioEmail(Exception):
    pass


class EsqueciMinhaSenhaSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        logging.info("Esqueci minha senha")
        instance.hash_redefinicao = instance.create_hash
        instance.save()

        result = SmeIntegracaoService.informacao_usuario_sgp(instance.username)
        if not result['email']:
            raise EmailNaoCadastrado(
                "Você não tem e-mail cadastrado e por isso a redefinição não é possível. Você deve procurar apoio na sua Diretoria Regional de Educação.")

        try:
            enviar_email_redifinicao_senha(email=result['email'].strip(), username=instance.username,
                                           nome=instance.name, hash_definicao=instance.hash_redefinicao)
        except Exception as err:
            logger.info("Erro ao enviar email: %s", str(err))
            raise ProblemaEnvioEmail("Problema ao enviar email.")

        return instance

    class Meta:
        model = User
        fields = ('username', 'email',)


class RedefinirSenhaSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        hash_redefinicao = attrs.get('hash_redefinicao')
        hash_redefinicao_deve_existir(hash_redefinicao)
        return attrs

    class Meta:
        model = User
        fields = ['uuid', 'username']


class RedefinirSenhaSerializerCreator(serializers.ModelSerializer):
    password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        hash_redefinicao = attrs.get('hash_redefinicao')
        hash_redefinicao_deve_existir(hash_redefinicao)
        senha_nao_pode_ser_nulo(attrs.get('password'))
        senha_nao_pode_ser_nulo(attrs.get('password2'))
        senhas_devem_ser_iguais(attrs.get('password'), attrs.get('password2'))
        attrs.pop('password2')
        return attrs

    def update(self, instance, validated_data):
        try:
            result = SmeIntegracaoService.redefine_senha(instance.username, validated_data['password'])
            instance.set_password(validated_data.get('password'))
            instance.hash_redefinicao = ''
            instance.save()
            return Response(result)
        except SmeIntegracaoException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ReadTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        return instance

    class Meta:
        model = User
        fields = ['hash_redefinicao', 'password', 'password2']
