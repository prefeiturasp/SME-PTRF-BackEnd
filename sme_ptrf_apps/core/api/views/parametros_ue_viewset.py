import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.models.parametros import Parametros


from sme_ptrf_apps.users.permissoes import PermissaoAPITodosComLeituraOuGravacao, PermissaoAPIApenasSmeComGravacao

logger = logging.getLogger(__name__)


class ParametrosUeViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao]
    queryset = Parametros.objects.all()

    @action(detail=False, methods=['get'], url_path='texto-pagina-valores-reprogramados',
            permission_classes=[IsAuthenticated, PermissaoAPITodosComLeituraOuGravacao])
    def texto_pagina_valores_reprogramados(self, request):
        texto = Parametros.get().texto_pagina_valores_reprogramados_ue

        return Response({'detail': texto}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='texto-pagina-paa-ue',
            permission_classes=[IsAuthenticated, PermissaoAPITodosComLeituraOuGravacao])
    def texto_pagina_paa_ue(self, request):
        texto = Parametros.get().texto_pagina_paa_ue

        return Response({'detail': texto}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='update-texto-pagina-paa-ue',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasSmeComGravacao])
    def update_texto_pagina_paa_ue(self, request, uuid=None):

        texto_pagina_paa_ue = request.data.get('texto_pagina_paa_ue', None)

        if texto_pagina_paa_ue is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'update-texto-pagina-paa-ue',
                'mensagem': 'Faltou informar o campo texto de página PAA.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        obj_paa = Parametros.get()
        obj_paa.texto_pagina_paa_ue = texto_pagina_paa_ue
        obj_paa.save()

        return Response({'detail': 'Salvo com sucesso'}, status=status.HTTP_200_OK)
