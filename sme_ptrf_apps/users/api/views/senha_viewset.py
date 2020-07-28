from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from sme_ptrf_apps.users.api.serializers import (
    EsqueciMinhaSenhaSerializer,
    RedefinirSenhaSerializer,
    RedefinirSenhaSerializerCreator,
)
from sme_ptrf_apps.users.services import SmeIntegracaoException
User = get_user_model()


class EsqueciMinhaSenhaViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = EsqueciMinhaSenhaSerializer


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
        if isinstance(result, SmeIntegracaoException):
            return Response(result)
        return Response({'detail': 'Senha redefinida com sucesso'}, status=status.HTTP_200_OK)
