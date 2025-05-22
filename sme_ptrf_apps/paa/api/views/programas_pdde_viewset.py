from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

from django.db.models import Sum
import django_filters

from waffle.mixins import WaffleFlagMixin

from sme_ptrf_apps.paa.models import ProgramaPdde
from sme_ptrf_apps.paa.services import PaaService

from sme_ptrf_apps.paa.api.serializers import ProgramaPddeSerializer, ProgramasPddeSomatorioTotalSerializer
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination

from sme_ptrf_apps.users.permissoes import PermissaoAPIApenasSmeComLeituraOuGravacao


class ProgramaPddeFiltro(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ProgramaPdde
        fields = ['nome', ]


class ProgramaPddeViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao]
    lookup_field = 'uuid'
    queryset = ProgramaPdde.objects.all().order_by('nome')
    serializer_class = ProgramaPddeSerializer
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = ProgramaPddeFiltro

    def validar_campos(self, request):
        nome = request.data.get('nome')
        if not nome:
            raise serializers.ValidationError(
                {"nome": "Nome do Programa PDDE não foi informado."}
            )
        return nome

    def create(self, request):
        """ Método acionado antes do validate do Serializer para
            validação de constraints da Model (ao Criar)"""

        nome = self.validar_campos(request)
        if ProgramaPdde.objects.filter(nome__iexact=nome).first():
            raise serializers.ValidationError(
                {
                    "erro": "Duplicated",
                    "detail": ("Erro ao criar Programa PDDE. Já existe um " +
                               "Programa PDDE cadastrado com este nome.")
                }
            )
        return super().create(request)

    def update(self, request, *args, **kwargs):
        """ Método acionado antes do validate do Serializer
            para validação de constraints da Model (Ao Atualizar)"""

        obj = self.get_object()
        nome = request.data.get('nome')
        if ProgramaPdde.objects.exclude(pk=obj.pk).filter(nome__iexact=nome).first():
            raise serializers.ValidationError(
                {
                    "erro": "Duplicated",
                    "detail": ("Erro ao atualizar Programa PDDE. Já existe um " +
                               "Programa PDDE cadastrado com este nome.")
                }
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.acaopdde_set.count() > 0:
            content = {
                'erro': 'ProtectedError',
                'mensagem': ("Não é possível excluir. " +
                             "Este programa ainda está vinculado há alguma ação.")
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(obj)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='paa_uuid', description='UUID do PAA', required=True,
                             type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
        ],
        responses={200: OpenApiTypes.OBJECT},
        description="Retornam os totais por programa PDDE relacionados a um PAA"
    )
    @action(detail=False, methods=['get'], url_path='totais')
    def somatorio_total_por_programas(self, request):
        paa = request.query_params.get('paa_uuid')
        if not paa:
            raise serializers.ValidationError({
                'erro': 'NotFound',
                'mensagem': "PAA não foi informado."
            })

        response = PaaService.somatorio_totais_por_programa_pdde(paa)
        serializer = ProgramasPddeSomatorioTotalSerializer(response)
        return Response(serializer.data, status=status.HTTP_200_OK)
