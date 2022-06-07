import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.models.parametros import Parametros


from sme_ptrf_apps.users.permissoes import PermissaoAPIApenasSmeComLeituraOuGravacao

logger = logging.getLogger(__name__)


class ParametrosSmeViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao]
    queryset = Parametros.objects.all()

    @action(detail=False, methods=['get'], url_path='texto-pagina-suporte',
            permission_classes=[IsAuthenticated, PermissaoAPIApenasSmeComLeituraOuGravacao])
    def texto_pagina_suporte(self, request):
        texto = Parametros.get().texto_pagina_suporte_sme

        return Response({'detail': texto}, status=status.HTTP_200_OK)
