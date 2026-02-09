from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from waffle.mixins import WaffleFlagMixin

from sme_ptrf_apps.core.models import Recurso
from ..serializers.recurso_serializer import RecursoSerializer
from sme_ptrf_apps.core.services.recursos_service import RecursoService


class RecursoViewSet(WaffleFlagMixin,
                     ModelViewSet):

    lookup_field = 'uuid'
    queryset = Recurso.objects.filter(ativo=True).order_by('nome')
    permission_classes = [IsAuthenticated]
    serializer_class = RecursoSerializer
    waffle_flag = "premio-excelencia"

    @action(detail=False, methods=['get'], url_path='por-unidade')
    def por_unidade(self, request):
        from sme_ptrf_apps.core.models.unidade import Unidade
        uuid_unidade = self.request.query_params.get('uuid_unidade')

        try:
            unidade = Unidade.objects.get(uuid=uuid_unidade)
        except Unidade.DoesNotExist:
            content = {
                'erro': 'DoesNotExist',
                'mensagem': 'Unidade não encontrada'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        recurso_service = RecursoService()
        recursos = recurso_service.disponiveis_para_unidade(unidade)
        serializer = self.get_serializer(recursos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
