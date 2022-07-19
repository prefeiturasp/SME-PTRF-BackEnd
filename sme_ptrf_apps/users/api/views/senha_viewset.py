import logging

from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from sme_ptrf_apps.users.api.serializers import (
    EsqueciMinhaSenhaSerializer,
    RedefinirSenhaSerializer,
    RedefinirSenhaSerializerCreator,
)
from sme_ptrf_apps.users.api.serializers.senha_serializer import EmailNaoCadastrado, ProblemaEnvioEmail

logger = logging.getLogger(__name__)

User = get_user_model()


class EsqueciMinhaSenhaViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = EsqueciMinhaSenhaSerializer

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, args, kwargs)
        except EmailNaoCadastrado as err_email:
            return Response({'detail': str(err_email)}, status=status.HTTP_400_BAD_REQUEST)
        except ProblemaEnvioEmail as err_envio:
            return Response({'detail': str(err_envio)}, status=status.HTTP_400_BAD_REQUEST)


class RedefinirSenhaViewSet(viewsets.ModelViewSet):
    lookup_field = 'hash_redefinicao'
    queryset = User.objects.filter(username='987654')
    serializer_class = RedefinirSenhaSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return RedefinirSenhaSerializer
        else:
            return RedefinirSenhaSerializerCreator

    def retrieve(self, request, hash_redefinicao=None):
        RedefinirSenhaSerializer().validate({'hash_redefinicao': hash_redefinicao})
        return Response({'detail': hash_redefinicao}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serialize = RedefinirSenhaSerializerCreator()
        validated_data = serialize.validate(request.data)
        usuario = User.objects.get(hash_redefinicao=validated_data.get('hash_redefinicao'))
        result = serialize.update(usuario, validated_data)
        if isinstance(result, Response):
            logger.error('Erro ao alterar a senha:', result)
            return result
        return Response({'detail': 'Senha redefinida com sucesso'}, status=status.HTTP_200_OK)




