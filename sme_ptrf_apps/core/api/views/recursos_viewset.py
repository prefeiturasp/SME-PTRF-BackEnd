from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from waffle.mixins import WaffleFlagMixin

from sme_ptrf_apps.core.models import Recurso
from ..serializers.recurso_serializer import RecursoSerializer
from sme_ptrf_apps.core.services.recursos_usuario_service import recursos_disponiveis_usuario


class RecursoViewSet(WaffleFlagMixin,
                     ModelViewSet):

    lookup_field = 'uuid'
    queryset = Recurso.objects.filter(ativo=True).order_by('nome')
    permission_classes = [IsAuthenticated]
    serializer_class = RecursoSerializer
    waffle_flag = "premio-excelencia"

    @action(detail=False, methods=['get'], url_path='disponiveis')
    def recursos_disponiveis(self, request):
        """
        Retorna os recursos disponíveis para o usuário autenticado.

        Para usuários com acesso SME, retorna todos os recursos.
        Para outros usuários, retorna apenas recursos relacionados aos seus períodos iniciais.
        """
        recursos = recursos_disponiveis_usuario(request.user)
        serializer = self.get_serializer(recursos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
