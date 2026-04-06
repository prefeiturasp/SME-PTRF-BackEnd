import logging

from waffle.mixins import WaffleFlagMixin
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from ..serializers.parametro_paa_serializer import ParametroPaaSerializer
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from sme_ptrf_apps.paa.models import ParametroPaa

from sme_ptrf_apps.users.permissoes import PermissaoAPITodosComLeituraOuGravacao

logger = logging.getLogger(__name__)


class ParametrosPaaViewSet(WaffleFlagMixin, GenericViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = ParametroPaa.objects.all()
    pagination_class = CustomPagination
    serializer_class = ParametroPaaSerializer

    @action(detail=False, methods=['get'], url_path='mes-elaboracao-paa')
    def mes_elaboracao_paa(self, request):
        texto = ParametroPaa.get().mes_elaboracao_paa
        return Response({'detail': texto}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='textos-paa-ue',
            permission_classes=[IsAuthenticated, PermissaoAPITodosComLeituraOuGravacao])
    def texto_paa_ue(self, request):
        """Retorna textos específicos da PAA para UE."""
        obj_paa = ParametroPaa.get()
        serializer = self.get_serializer(obj_paa)
        response_data = serializer.data

        logger.info('Textos PAA recuperados para todos os campos')

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='update-textos-paa-ue',
            permission_classes=[IsAuthenticated, PermissaoAPITodosComLeituraOuGravacao])
    def update_textos_paa_ue(self, request):
        """Atualiza textos específicos da PAA para UE."""
        if not request.data:
            logger.warning(f'Tentativa de atualizar textos PAA sem dados pelo usuário {request.user}')
            return Response(
                {
                    'erro': 'falta_de_informacoes',
                    'operacao': 'update_textos_paa_ue',
                    'mensagem': 'Pelo menos um campo deve ser enviado para atualização.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        obj_paa = ParametroPaa.get()
        serializer = self.get_serializer(obj_paa, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            logger.info(f'Textos PAA atualizados com sucesso pelo usuário {request.user}')
            return Response(
                {'detail': 'Textos atualizados com sucesso'},
                status=status.HTTP_200_OK
            )

        logger.error(f'Erro ao atualizar textos PAA: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
