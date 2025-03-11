import datetime
import logging

from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.core.exceptions import ValidationError

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
    PermissaoAPITodosComLeituraOuGravacao,
    PermissaoAPITodosComGravacao
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
            permission_classes=[])#[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
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
    