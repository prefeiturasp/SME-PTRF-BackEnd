import logging

from django.contrib.auth import get_user_model
from requests import ConnectTimeout, ReadTimeout
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from sme_ptrf_apps.users.api.serializers import (
    AlteraEmailSerializer,
    RedefinirSenhaSerializer,
    UserCreateSerializer,
    UserSerializer,
)
from sme_ptrf_apps.users.models import Grupo
from sme_ptrf_apps.users.services import SmeIntegracaoException, SmeIntegracaoService

User = get_user_model()


logger = logging.getLogger(__name__)


class UserViewSet(ModelViewSet):
    lookup_field = "id"
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return UserSerializer
        else:
            return UserCreateSerializer

    def get_queryset(self, *args, **kwargs):
        qs = self.queryset

        visao = self.request.query_params.get('visao')

        if visao:
            qs = qs.filter(visoes__nome=visao).exclude(id=self.request.user.id).all()

        groups__id = self.request.query_params.get('groups__id')
        if groups__id:
            qs = qs.filter(groups__id=groups__id)

        search = self.request.query_params.get('search')
        if search is not None:
            qs = qs.filter(name__unaccent__icontains=search)

        associacao_uuid = self.request.query_params.get('associacao_uuid')
        if associacao_uuid:
            qs = qs.filter(unidades__associacoes__uuid=associacao_uuid)

        username = self.request.query_params.get('username')
        if username:
            qs = qs.filter(username=username)

        return qs

    @action(detail=False, methods=["GET"])
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=True, url_path='altera-email', methods=['patch'])
    def altera_email(self, request, username):
        data = request.data
        serialize = AlteraEmailSerializer()
        validated_data = serialize.validate(data)
        usuario = User.objects.get(username=username)
        instance = serialize.update(usuario, validated_data)
        if isinstance(instance, Response):
            return instance
        return Response(UserSerializer(instance, context={'request': request}).data, status=status.HTTP_200_OK)

    @action(detail=True, url_path='altera-senha', methods=['patch'])
    def altera_senha(self, request, username):
        data = request.data
        serializer = RedefinirSenhaSerializer()
        validated_data = serializer.validate(data)
        usuario = User.objects.get(username=username)
        instance = serializer.update(usuario, validated_data)
        if isinstance(instance, Response):
            return instance
        return Response(UserSerializer(instance, context={'request': request}).data, status=status.HTTP_200_OK)

    @action(detail=False, url_path="grupos", methods=['get'])
    def grupos(self, request):
        logger.info("Buscando grupos para usuario: %s", request.user)
        usuario = request.user
        visao = request.query_params.get('visao')

        if not visao:
            return Response("Parâmetro visão é obrigatório.", status=status.HTTP_400_BAD_REQUEST)

        try:
            grupos = Grupo.objects.filter(visoes__nome=visao).all()

            return Response([{'id': str(grupo.id), "nome": grupo.name, "descricao": grupo.descricao} for grupo in grupos])
        except Exception as err:
            erro = {
                'erro': 'erro_ao_consultar_grupos',
                'mensagem': str(err)
            }
            logging.info("Erro ao buscar grupos do usuário %s", erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='consultar')
    def consulta_servidor_sgp(self, request):
        username = self.request.query_params.get('username')

        if not username:
            return Response("Parâmetro username obrigatório.", status=status.HTTP_400_BAD_REQUEST)

        try:
            result = SmeIntegracaoService.informacao_usuario_sgp(username)
            return Response(result, status=status.HTTP_200_OK)
        except SmeIntegracaoException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ReadTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
