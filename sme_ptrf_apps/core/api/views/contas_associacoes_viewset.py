from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django_filters import rest_framework as filters

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample

from sme_ptrf_apps.users.permissoes import PermissaoAPITodosComLeituraOuGravacao
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from ..serializers import ContaAssociacaoCriacaoSerializer, TipoContaSerializer
from ...models import ContaAssociacao, TipoConta


class ContasAssociacoesViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = ContaAssociacao.objects.all()
    serializer_class = ContaAssociacaoCriacaoSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = CustomPagination

    def get_queryset(self):
        associacao_nome = self.request.query_params.get('associacao_nome')
        tipo_conta_uuid = self.request.query_params.get('tipo_conta_uuid')
        status = self.request.query_params.get('status')

        filters = Q()
        if associacao_nome:
            filters &= Q(
                Q(associacao__nome__unaccent__icontains=associacao_nome) |
                Q(associacao__unidade__codigo_eol=associacao_nome) |
                Q(associacao__unidade__nome__unaccent__icontains=associacao_nome)
            )
        if tipo_conta_uuid:
            filters &= Q(tipo_conta__uuid=tipo_conta_uuid)
        if status:
            filters &= Q(status=status)

        return ContaAssociacao.objects.filter(filters)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='associacao_nome', description='Nome da Associação', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='tipo_conta_uuid', description='UUID do tipo de Conta', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='status', description='Status da Conta', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                             enum=[i[0] for i in ContaAssociacao.STATUS_CHOICES]),
        ],
        responses={200: ContaAssociacaoCriacaoSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError
        obj = self.get_object()
        try:
            self.perform_destroy(obj)
        except ProtectedError:
            content = {
                'erro': 'ProtectedError',
                'mensagem': (
                    'Essa operação não pode ser realizada. Há dados vinculados a essa ação da referida Conta Associação'
                )
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        responses={200: 'result'},
        examples=[
            OpenApiExample('Resposta', value={
                "tipos_contas": TipoContaSerializer(TipoConta.objects.all(), many=True).data,
                "status": ContaAssociacao.STATUS_CHOICES
            }),
        ]
    )
    @action(detail=False, methods=['GET'], url_path='filtros',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def tabelas(self, request):
        result = {
            "tipos_contas": TipoContaSerializer(TipoConta.objects.all(), many=True).data,
            "status": ContaAssociacao.STATUS_CHOICES
        }

        return Response(result, status=status.HTTP_200_OK)
