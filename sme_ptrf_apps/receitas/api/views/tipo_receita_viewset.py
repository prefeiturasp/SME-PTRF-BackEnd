import datetime
import logging

from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.core.api.serializers import TipoContaSerializer
from sme_ptrf_apps.receitas.api.serializers import (
    TipoReceitaListaSerializer,
    TipoReceitaCreateSerializer,
    DetalheTipoReceitaSerializer
)
from sme_ptrf_apps.core.models import TipoConta
from sme_ptrf_apps.receitas.models import TipoReceita, DetalheTipoReceita
from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe,
    PermissaoAPIApenasSmeComLeituraOuGravacao
)

logger = logging.getLogger(__name__)


class TipoReceitaViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         GenericViewSet):
    lookup_field = 'uuid'
    queryset = TipoReceita.objects.all().order_by('-nome')
    serializer_class = TipoReceitaListaSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('nome', 'e_repasse', 'e_rendimento', 'e_devolucao', 'e_estorno', 'aceita_capital', 'aceita_custeio',
                     'aceita_livre', 'e_recursos_proprios', 'tipos_conta__uuid', 'unidades__uuid')
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return TipoReceitaListaSerializer
        else:
            return TipoReceitaCreateSerializer


    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError

        obj = self.get_object()

        try:
            self.perform_destroy(obj)
        except ProtectedError:
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Esse tipo de crédito não pode ser excluído pois existem receitas cadastradas com esse tipo.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='filtros',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao])
    def filtros(self, request, *args, **kwargs):

        tipos = [
            {"field_name": "e_repasse", "name": "Repasse"},
            {"field_name": "e_rendimento", "name": "Rendimento"},
            {"field_name": "e_devolucao", "name": "Devolução"},
            {"field_name": "e_estorno", "name": "Estorno"}
        ]
        aceita = [
            {"field_name": "aceita_capital", "name": "Capital"},
            {"field_name": "aceita_custeio", "name": "Custeio"},
            {"field_name": "aceita_livre", "name": "Livre aplicação"}
        ]
        result = {
            "tipos_contas": TipoContaSerializer(TipoConta.objects.all(), many=True).data,
            "tipos": tipos,
            "aceita": aceita,
            "detalhes": DetalheTipoReceitaSerializer(DetalheTipoReceita.objects.order_by('nome'), many=True).data,
        }

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, url_path='unidades-vinculadas',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao])
    def unidades_vinculadas(self, request, *args, **kwargs):
        from sme_ptrf_apps.core.api.serializers import UnidadeLookUpSerializer
        uuid_dre = self.request.query_params.get('dre')
        nome_ou_codigo = self.request.query_params.get('nome_ou_codigo')

        instance = self.get_object()
        unidades_qs = instance.unidades.all()

        if uuid_dre is not None and uuid_dre != "":
            unidades_qs = unidades_qs.filter(dre__uuid=uuid_dre)
        
        if nome_ou_codigo is not None:
            unidades_qs = unidades_qs.filter(Q(codigo_eol=nome_ou_codigo) | Q(nome__unaccent__icontains=nome_ou_codigo) | Q(
                nome__unaccent__icontains=nome_ou_codigo))
            
        serializer = UnidadeLookUpSerializer(unidades_qs, many=True)

        paginator = CustomPagination()
        paginated_unidades = paginator.paginate_queryset(serializer.data, request)

        return paginator.get_paginated_response(paginated_unidades)
    
    @action(detail=True, url_path='unidades-nao-vinculadas',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao])
    def unidades_nao_vinculadas(self, request, *args, **kwargs):
        from sme_ptrf_apps.core.api.serializers import UnidadeLookUpSerializer
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
                unidades_nao_vinculadas = unidades_nao_vinculadas.filter(Q(codigo_eol=nome_ou_codigo) | Q(nome__unaccent__icontains=nome_ou_codigo) | Q(
                    nome__unaccent__icontains=nome_ou_codigo))


        serializer = UnidadeLookUpSerializer(unidades_nao_vinculadas, many=True)

        paginator = CustomPagination()
        paginated_unidades = paginator.paginate_queryset(serializer.data, request)

        return paginator.get_paginated_response(paginated_unidades)
    
    @action(detail=True, methods=['POST'], url_path='unidade/(?P<unidade_uuid>[^/.]+)/desvincular', 
            permission_classes=[IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao])
    def desvincular_unidade(self, request, unidade_uuid, *args, **kwargs):
        instance = self.get_object()

        unidade = instance.unidades.filter(uuid=unidade_uuid).first()

        if not unidade:
            return Response({"detail": "Unidade não encontrada ou já desvinculada."}, status=status.HTTP_404_NOT_FOUND)
        
        if instance.pode_desvincular_unidades([unidade_uuid]):
            instance.unidades.remove(unidade)
        else:
            return Response({"mensagem": "Não é possível restringir tipo de crédito, pois existem unidades que já possuem crédito criado com esse tipo e não estão selecionadas."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"mensagem": "Unidade desvinculada com sucesso!"}, status=200)

    @action(detail=True, methods=['POST'], url_path='desvincular-em-lote', 
            permission_classes=[IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao])
    def desvincular_em_lote(self, request, *args, **kwargs):
        from sme_ptrf_apps.core.models.unidade import Unidade

        instance = self.get_object()

        unidade_uuids = request.data.get('unidade_uuids', [])

        if not unidade_uuids:
            return Response({"erro": "Nenhuma unidade informada."}, status=status.HTTP_400_BAD_REQUEST)

        unidades = Unidade.objects.filter(uuid__in=unidade_uuids)

        if not unidades.exists():
            return Response({"erro": "Nenhuma unidade encontrada ou já desvinculada."}, status=status.HTTP_404_NOT_FOUND)

        if instance.pode_desvincular_unidades(unidade_uuids):
            instance.unidades.remove(*unidades)
        else:
            return Response({"mensagem": "Não é possível restringir tipo de crédito, pois existem unidades que já possuem crédito criado com esse tipo e não estão selecionadas."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"mensagem": "Unidades desvinculadas com sucesso!"}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'], url_path='unidade/(?P<unidade_uuid>[^/.]+)/vincular', 
            permission_classes=[IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao])
    def vincular_unidade(self, request, unidade_uuid, *args, **kwargs):
        from sme_ptrf_apps.core.models.unidade import Unidade
        
        instance = self.get_object()

        unidade = Unidade.objects.filter(uuid=unidade_uuid).first()
        
        instance.unidades.add(unidade)

        return Response({"mensagem": "Unidade vinculada com sucesso!"}, status=200)
    
    @action(detail=True, methods=['POST'], url_path='vincular-em-lote', 
            permission_classes=[IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao])
    def vincular_em_lote(self, request, *args, **kwargs):
        from sme_ptrf_apps.core.models.unidade import Unidade

        instance = self.get_object()

        unidade_uuids = request.data.get('unidade_uuids', [])

        if not unidade_uuids:
            return Response({"erro": "Nenhuma unidade informada."}, status=status.HTTP_400_BAD_REQUEST)

        unidades = Unidade.objects.filter(uuid__in=unidade_uuids)

        if not unidades.exists():
            return Response({"erro": "Nenhuma unidade encontrada."}, status=status.HTTP_404_NOT_FOUND)

        instance.unidades.add(*unidades)

        return Response({"mensagem": "Unidades vinculadas com sucesso!"}, status=status.HTTP_200_OK)
