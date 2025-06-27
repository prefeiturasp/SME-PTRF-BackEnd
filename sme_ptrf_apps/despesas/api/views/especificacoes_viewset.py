from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status, mixins, exceptions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CHOICES
from django.db.models import Q
from django_filters import rest_framework as filters

from ..serializers.especificacao_material_servico_serializer import (
    EspecificacaoMaterialServicoLookUpSerializer,
    EspecificacaoMaterialServicoSerializer
)
from ..serializers.tipo_custeio_serializer import TipoCusteioSerializer
from ...models import EspecificacaoMaterialServico, TipoCusteio
from ...tipos_aplicacao_recurso import aplicacoes_recurso_to_json
from ....core.api.utils.pagination import CustomPagination


class EspecificacaoMaterialServicoViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'id'
    queryset = EspecificacaoMaterialServico.objects.all().order_by('descricao')
    serializer_class = EspecificacaoMaterialServicoLookUpSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    ordering_fields = ('descricao',)
    search_fields = ('uuid', 'id', 'descricao')
    filterset_fields = ('aplicacao_recurso', 'tipo_custeio')

    def get_serializer_class(self):
        return EspecificacaoMaterialServicoLookUpSerializer


class ParametrizacaoEspecificacoesMaterialServicoViewSet(mixins.CreateModelMixin,
                                                         mixins.RetrieveModelMixin,
                                                         mixins.ListModelMixin,
                                                         mixins.UpdateModelMixin,
                                                         mixins.DestroyModelMixin,
                                                         viewsets.GenericViewSet):

    lookup_field = 'uuid'
    queryset = EspecificacaoMaterialServico.objects.all().order_by('id')
    permission_classes = [IsAuthenticated]
    serializer_class = EspecificacaoMaterialServicoSerializer
    pagination_class = CustomPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(name='ativa', description='Status da especificação', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, enum=['0', '1']),
            OpenApiParameter(name='descricao', description='Descrição da especificação', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='aplicacao_recurso', description='Custeio ou Capital', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                             enum=[i[0] for i in APLICACAO_CHOICES]),
            OpenApiParameter(name='tipo_custeio', description='UUID do tipo de despesa custeio', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: EspecificacaoMaterialServicoSerializer()},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['GET'], url_path='tabelas', permission_classes=[IsAuthenticated])
    def tabelas(self, request):
        tipos_custeio = TipoCusteio.objects.all().order_by('nome')

        result = {
            "tipos_custeio": TipoCusteioSerializer(tipos_custeio, many=True).data,
            "aplicacao_recursos": aplicacoes_recurso_to_json()
        }

        return Response(result, status=status.HTTP_200_OK)

    def get_queryset(self):
        qs = EspecificacaoMaterialServico.objects.all().order_by('descricao')

        ativa = self.request.query_params.get('ativa')
        if ativa in ['0', '1']:
            ativa = bool(int(ativa))
            qs = qs.filter(ativa=ativa)

        pesquisa = self.request.query_params.get('descricao')
        if pesquisa:
            pesquisa = pesquisa.strip()
            qs = qs.filter(
                Q(descricao__unaccent__icontains=pesquisa) |
                Q(tipo_custeio__nome__unaccent__icontains=pesquisa)
            )

        aplicacao_recurso = self.request.query_params.get('aplicacao_recurso')
        if aplicacao_recurso:
            qs = qs.filter(aplicacao_recurso=aplicacao_recurso)

        tipo_custeio_uuid = self.request.query_params.get('tipo_custeio')
        if tipo_custeio_uuid:
            qs = qs.filter(tipo_custeio__uuid=tipo_custeio_uuid)

        return qs

    def perform_create(self, serializer):
        # História AB#125420
        """
            3.4) O sistema deve validar o campo "Descrição" para não permitir duplicidade de cadastro
            na inclusão e na alteração do registro. Se for verificado que o nome informado no campo Descrição já
            existe para o mesmo tipo de aplicação de recurso e tipo do custeio (quando aplicável) não deve ser
            permitido o cadastro e exibida mensagem abaixo do campo: Esta especificação de material e serviço já existe.
        """
        ja_existe = EspecificacaoMaterialServico.objects.filter(
            descricao__iexact=serializer.validated_data.get('descricao'),
            aplicacao_recurso__iexact=serializer.validated_data.get('aplicacao_recurso'),
            tipo_custeio=serializer.validated_data.get('tipo_custeio')
        ).exists()

        if ja_existe:
            raise exceptions.ValidationError({
                'erro': 'Duplicated',
                'mensagem': 'Esta especificação de material e serviço já existe.'
            })
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        # História AB#125420
        """
            3.1) Pode alterar o tipo de aplicação do recurso, caso não tenha sido utilizado nos cadastros de despesa.
            Exibir mensagem ao usuário informando, caso não seja possível fazer a alteração por uso nas despesas.
        """
        obj = self.get_object()
        tem_rateio_despesas = obj.rateiodespesa_set.exists()

        if tem_rateio_despesas:
            aplicacao_recurso_formulario = serializer.validated_data.get('aplicacao_recurso')
            aplicacao_recurso_atual = obj.aplicacao_recurso

            eh_alteracao_aplicacao_recurso = aplicacao_recurso_formulario != aplicacao_recurso_atual
            if eh_alteracao_aplicacao_recurso:
                raise exceptions.ValidationError({
                    'erro': 'Despesas vinculadas',
                    'mensagem': ('Não é possível alterar a aplicação do recurso, ' +
                                 'pois já foi utilizado em despesas.')
                })

        return super().perform_update(serializer)

    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError

        obj = self.get_object()

        try:
            self.perform_destroy(obj)
        except ProtectedError:
            raise exceptions.ValidationError({
                'erro': 'ProtectedError',
                'mensagem': 'Essa operação não pode ser realizada. Há despesas vinculadas à esta especificação'
            })

        return Response(status=status.HTTP_204_NO_CONTENT)
