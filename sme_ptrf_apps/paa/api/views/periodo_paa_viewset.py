import logging

from waffle.mixins import WaffleFlagMixin

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django.http import Http404

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import (
    PermissaoAPIApenasSmeComLeituraOuGravacao
)
from sme_ptrf_apps.paa.api.serializers.periodo_paa_serializer import PeriodoPaaSerializer
from sme_ptrf_apps.paa.models import PeriodoPaa, Paa

logger = logging.getLogger(__name__)


class PeriodoPaaViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao]
    lookup_field = 'uuid'
    queryset = PeriodoPaa.objects.all().order_by('data_inicial')
    serializer_class = PeriodoPaaSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        qs = self.queryset
        filtro_referencia = self.request.query_params.get('referencia', None)

        if filtro_referencia is not None:
            qs = qs.filter(referencia__unaccent__icontains=filtro_referencia)

        return qs

    def destroy(self, request, *args, **kwargs):    
        try:
            # Obtém o período que será excluído
            periodo = self.get_object()                
            tem_paa_vinculado = Paa.objects.filter(periodo_paa=periodo).exists()
            
            # Verifica se o período está vinculado a algum PAA
            if tem_paa_vinculado:
                return Response(
                    {
                        "mensagem": "Este período de PAA não pode ser excluído porque está sendo utilizada em um Plano Anual de Atividades (PAA)."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Se não estiver vinculado, exclui normalmente
            return super().destroy(request, *args, **kwargs)

        except Http404:
            return Response(
                {
                    "mensagem": "Período não encontrado."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"mensagem": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )