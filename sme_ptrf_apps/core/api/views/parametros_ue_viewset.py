import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.models.parametros import Parametros


from sme_ptrf_apps.users.permissoes import PermissaoAPITodosComLeituraOuGravacao

logger = logging.getLogger(__name__)


class ParametrosUeViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao]
    queryset = Parametros.objects.all()

    @action(detail=False, methods=['get'], url_path='texto-pagina-valores-reprogramados',
            permission_classes=[IsAuthenticated, PermissaoAPITodosComLeituraOuGravacao])
    def texto_pagina_valores_reprogramados(self, request):
        texto = Parametros.get().texto_pagina_valores_reprogramados_ue

        return Response({'detail': texto}, status=status.HTTP_200_OK)
