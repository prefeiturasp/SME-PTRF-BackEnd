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

        instance = self.get_object()
        unidades_qs = instance.unidades.all()

        if uuid_dre is not None and uuid_dre != "":
            unidades_qs = unidades_qs.filter(dre__uuid=uuid_dre)

        if nome_ou_codigo is not None:
            unidades_qs = unidades_qs.filter(
                Q(codigo_eol=nome_ou_codigo) | Q(nome__unaccent__icontains=nome_ou_codigo) | Q(
                    nome__unaccent__icontains=nome_ou_codigo))

        serializer = UnidadeLookUpSerializer(unidades_qs, many=True)

        paginator = CustomPagination()
        paginated_unidades = paginator.paginate_queryset(serializer.data, request)

        return paginator.get_paginated_response(paginated_unidades)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='dre', description='UUID da DRE', required=False,
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

        instance = self.get_object()

        if (uuid_dre is None or uuid_dre == "") and (nome_ou_codigo is None or nome_ou_codigo == ""):
            unidades_nao_vinculadas = Unidade.objects.none()
        else:
            todas_unidades = Unidade.objects.all()

            unidades_nao_vinculadas = todas_unidades.exclude(uuid__in=instance.unidades.values_list('uuid', flat=True))

            if uuid_dre is not None and uuid_dre != "":
                unidades_nao_vinculadas = unidades_nao_vinculadas.filter(dre__uuid=uuid_dre)

            if nome_ou_codigo is not None:
                unidades_nao_vinculadas = unidades_nao_vinculadas.filter(
                    Q(codigo_eol=nome_ou_codigo) | Q(nome__unaccent__icontains=nome_ou_codigo) | Q(
                        nome__unaccent__icontains=nome_ou_codigo))

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
        from sme_ptrf_apps.core.models.unidade import Unidade

        instance = self.get_object()

        unidade_uuids = request.data.get('unidade_uuids', [])

        if not unidade_uuids:
            return Response({"erro": "Nenhuma unidade informada."}, status=status.HTTP_400_BAD_REQUEST)

        unidades = Unidade.objects.filter(uuid__in=unidade_uuids)

        if not unidades.exists():
            return Response(
                {"erro": "Nenhuma unidade encontrada ou já desvinculada."},
                status=status.HTTP_404_NOT_FOUND)

        if instance.pode_desvincular(unidade_uuids):
            instance.unidades.remove(*unidades)
        else:
            return Response({"mensagem": "A operação de desvinculação não pode ser realizada. Algumas unidades possuem rateios cadastrados que exigem que permaneçam vinculadas a este tipo de custeio."}, status=status.HTTP_400_BAD_REQUEST)  # noqa

        return Response({"mensagem": "Unidades desvinculadas com sucesso!"}, status=status.HTTP_200_OK)
