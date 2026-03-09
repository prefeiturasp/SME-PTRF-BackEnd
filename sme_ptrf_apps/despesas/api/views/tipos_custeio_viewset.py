import logging
from django.db.models import Q
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from ..serializers.tipo_custeio_serializer import TipoCusteioSerializer, TipoCusteioFormSerializer
from ...models import TipoCusteio
from sme_ptrf_apps.core.api.serializers import UnidadeLookUpSerializer
from sme_ptrf_apps.users.permissoes import (
    PermissaoAPIApenasSmeComLeituraOuGravacao
)
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.despesas.services.tipo_custeio_vinculo_unidade_service import (
    TipoCusteioVinculoUnidadeService,
    UnidadeNaoEncontradaException,
    ValidacaoVinculoException,
)

logger = logging.getLogger(__name__)


class TiposCusteioViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          GenericViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = TipoCusteio.objects.all().order_by('nome')
    serializer_class = TipoCusteioSerializer

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return TipoCusteioSerializer
        else:
            return TipoCusteioFormSerializer

    def get_queryset(self):
        qs = TipoCusteio.objects.all()

        nome = self.request.query_params.get('nome')
        if nome is not None:
            qs = qs.filter(nome__unaccent__icontains=nome)

        return qs.order_by('nome')

    def _get_service_tipo_custeio_vinculo_unidade(self) -> TipoCusteioVinculoUnidadeService:
        """
        Retorna uma instância do service para o objeto atual.

        Returns:
            Instância configurada do service
        """
        instance = self.get_object()
        return TipoCusteioVinculoUnidadeService(instance)
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='nome', description='Filtrar por nome', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: TipoCusteioSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='dre', description='UUID da DRE', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='tipo_unidade', description='Tipo da Unidade', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='nome_ou_codigo', description='Nome da Unidade ou Código EOL', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: UnidadeLookUpSerializer()},
    )
    @action(detail=True, url_path='unidades-vinculadas',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao])
    def unidades_vinculadas(self, request, *args, **kwargs):
        uuid_dre = self.request.query_params.get('dre')
        nome_ou_codigo = self.request.query_params.get('nome_ou_codigo')
        tipo_unidade = self.request.query_params.get('tipo_unidade')

        instance = self.get_object()
        unidades_qs = instance.unidades.all()

        if uuid_dre:
            unidades_qs = unidades_qs.filter(dre__uuid=uuid_dre)

        if tipo_unidade:
            unidades_qs = unidades_qs.filter(tipo_unidade=tipo_unidade)

        if nome_ou_codigo:
            unidades_qs = unidades_qs.filter(
                Q(codigo_eol=nome_ou_codigo) | Q(nome__unaccent__icontains=nome_ou_codigo))

        serializer = UnidadeLookUpSerializer(unidades_qs, many=True)

        paginator = CustomPagination()
        paginated_unidades = paginator.paginate_queryset(serializer.data, request)

        return paginator.get_paginated_response(paginated_unidades)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='dre', description='UUID da DRE', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='tipo_unidade', description='Tipo da Unidade', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='nome_ou_codigo', description='Nome da Unidade ou Código EOL', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: UnidadeLookUpSerializer()},
    )
    @action(detail=True, url_path='unidades-nao-vinculadas',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao])
    def unidades_nao_vinculadas(self, request, *args, **kwargs):
        from sme_ptrf_apps.core.models.unidade import Unidade
        uuid_dre = self.request.query_params.get('dre')
        nome_ou_codigo = self.request.query_params.get('nome_ou_codigo')
        tipo_unidade = self.request.query_params.get('tipo_unidade')

        instance = self.get_object()

        todas_unidades = Unidade.objects.select_related('dre', 'dre__dre').all()
        unidades_nao_vinculadas = todas_unidades.exclude(uuid__in=instance.unidades.values_list('uuid', flat=True))

        if uuid_dre:
            unidades_nao_vinculadas = unidades_nao_vinculadas.filter(dre__uuid=uuid_dre)

        if tipo_unidade:
            unidades_nao_vinculadas = unidades_nao_vinculadas.filter(tipo_unidade=tipo_unidade)

        if nome_ou_codigo:
            unidades_nao_vinculadas = unidades_nao_vinculadas.filter(
                Q(codigo_eol=nome_ou_codigo) | Q(nome__unaccent__icontains=nome_ou_codigo))

        serializer = UnidadeLookUpSerializer(unidades_nao_vinculadas, many=True)

        paginator = CustomPagination()
        paginated_unidades = paginator.paginate_queryset(serializer.data, request)

        return paginator.get_paginated_response(paginated_unidades)

    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError

        obj = self.get_object()

        try:
            self.perform_destroy(obj)
        except ProtectedError:
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Esse tipo não pode ser excluído pois existem despesas cadastradas com esse tipo.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'], url_path='vincular-unidades',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao])
    def vincular_unidades(self, request, *args, **kwargs):
        from sme_ptrf_apps.core.models.unidade import Unidade

        instance = self.get_object()

        unidade_uuids = request.data.get('unidade_uuids', [])

        if not unidade_uuids:
            return Response({"erro": "Nenhuma unidade informada."}, status=status.HTTP_400_BAD_REQUEST)

        unidades = Unidade.objects.filter(uuid__in=unidade_uuids)

        if not unidades.exists():
            return Response({"erro": "Nenhuma unidade encontrada."}, status=status.HTTP_404_NOT_FOUND)

        if instance.pode_vincular(unidade_uuids):
            instance.unidades.add(*unidades)
        else:
            return Response({"mensagem": "Não é possível vincular o tipo de custeio, pois existem unidades com rateios já criados para este tipo que não foram selecionadas."}, status=status.HTTP_400_BAD_REQUEST)  # noqa

        return Response({"mensagem": "Unidades vinculadas com sucesso!"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path='desvincular-unidades',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao])
    def desvincular_unidades(self, request, *args, **kwargs):
        """Desvincula uma unidade do tipo de despesa de custeio."""

        service = self._get_service_tipo_custeio_vinculo_unidade()
        unidade_uuids = request.data.get('unidade_uuids', [])

        if not unidade_uuids:
            return Response({"erro": "Nenhuma unidade informada."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            resultado = service.desvincular_unidades(unidade_uuids)
            return Response(resultado, status=status.HTTP_200_OK)

        except UnidadeNaoEncontradaException as e:   
            return Response({"mensagem": str(e)}, status=status.HTTP_404_NOT_FOUND)

        except ValidacaoVinculoException as e:         
            return Response({"mensagem": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            msg_erro = "Erro ao desvincular"
            logger.error(f"{msg_erro} {str(e)}", exc_info=True)
            return Response({"mensagem": msg_erro}, status=status.HTTP_400_BAD_REQUEST)   

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'unidade_uuids': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'uuid'}
                    }
                },
                'required': ['unidade_uuids']
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'mensagem': {'type': 'string'},
                    'total_desvinculado': {'type': 'integer'},
                    'unidades_desvinculadas': {'type': 'array', 'items': {'type': 'string'}}
                }
            },
            400: {'description': 'Validação falhou'},
            404: {'description': 'Nenhuma unidade encontrada'}
        }
    )
    @action(detail=True, methods=['POST'], url_path='vincular-todas-unidades',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao])
    def vincular_todas_unidades(self, request, *args, **kwargs):
        """Habilita o Tipo Custeio para todas as unidades."""
        service = self._get_service_tipo_custeio_vinculo_unidade()

        try:
            resultado = service.vincular_todas_unidades()
            return Response(resultado, status=status.HTTP_200_OK)
        except Exception as e:
            msg_erro = "Erro ao vincular todas as unidades."
            logger.error(f"{msg_erro} {str(e)}", exc_info=True)
            return Response({"mensagem": msg_erro}, status=status.HTTP_400_BAD_REQUEST)
