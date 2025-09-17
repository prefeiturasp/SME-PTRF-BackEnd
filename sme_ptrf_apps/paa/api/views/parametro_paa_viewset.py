import logging

from waffle.mixins import WaffleFlagMixin
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from sme_ptrf_apps.paa.models import ParametroPaa

from sme_ptrf_apps.users.permissoes import PermissaoAPITodosComLeituraOuGravacao, PermissaoAPIApenasSmeComGravacao

logger = logging.getLogger(__name__)


class ParametrosPaaViewSet(WaffleFlagMixin, GenericViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = ParametroPaa.objects.all()
    pagination_class = CustomPagination

    @action(detail=False, methods=['get'], url_path='mes-elaboracao-paa')
    def mes_elaboracao_paa(self, request):
        texto = ParametroPaa.get().mes_elaboracao_paa
        return Response({'detail': texto}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='textos-paa-ue',
            permission_classes=[IsAuthenticated, PermissaoAPIApenasSmeComGravacao])
    def texto_paa_ue(self, request):
        obj_paa = ParametroPaa.get()
        
        response_data = {
            'texto_pagina_paa_ue': obj_paa.texto_pagina_paa_ue,
            'introducao_do_paa_ue_1': obj_paa.introducao_do_paa_ue_1,
            'introducao_do_paa_ue_2': obj_paa.introducao_do_paa_ue_2,
            'conclusao_do_paa_ue_1': obj_paa.conclusao_do_paa_ue_1,
            'conclusao_do_paa_ue_2': obj_paa.conclusao_do_paa_ue_2
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['patch'], url_path='update-textos-paa-ue',
            permission_classes=[IsAuthenticated, PermissaoAPITodosComLeituraOuGravacao])
    def update_textos_paa_ue(self, request):
        texto_pagina_paa_ue = request.data.get('texto_pagina_paa_ue', None)
        introducao_do_paa_ue_1 = request.data.get('introducao_do_paa_ue_1', None)
        introducao_do_paa_ue_2 = request.data.get('introducao_do_paa_ue_2', None)
        conclusao_do_paa_ue_1 = request.data.get('conclusao_do_paa_ue_1', None)
        conclusao_do_paa_ue_2 = request.data.get('conclusao_do_paa_ue_2', None)

        campos = [
            texto_pagina_paa_ue,
            introducao_do_paa_ue_1,
            introducao_do_paa_ue_2,
            conclusao_do_paa_ue_1,
            conclusao_do_paa_ue_2
        ]
        
        if all(campo is None for campo in campos):
            response = {
                'erro': 'falta_de_informacoes',
                'operacao': 'update_textos_paa_ue',
                'mensagem': 'Pelo menos um campo deve ser enviado para atualização.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        obj_paa = ParametroPaa.get()
        
        if texto_pagina_paa_ue is not None:
            obj_paa.texto_pagina_paa_ue = texto_pagina_paa_ue
            
        if introducao_do_paa_ue_1 is not None:
            obj_paa.introducao_do_paa_ue_1 = introducao_do_paa_ue_1
            
        if introducao_do_paa_ue_2 is not None:
            obj_paa.introducao_do_paa_ue_2 = introducao_do_paa_ue_2
            
        if conclusao_do_paa_ue_1 is not None:
            obj_paa.conclusao_do_paa_ue_1 = conclusao_do_paa_ue_1
            
        if conclusao_do_paa_ue_2 is not None:
            obj_paa.conclusao_do_paa_ue_2 = conclusao_do_paa_ue_2

        obj_paa.save()

        return Response({'detail': 'Salvo com sucesso'}, status=status.HTTP_200_OK)