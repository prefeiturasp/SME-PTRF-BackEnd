import logging

from amqp import NotFound
from django.core.exceptions import ValidationError
from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.exceptions import ValidationError as DRFValidationError, NotFound

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.receitas.api.serializers import (
    DetalheTipoReceitaParametrizacaoSerializer,
    TipoReceitaListaSerializer
)
from sme_ptrf_apps.core.models import Recurso
from sme_ptrf_apps.receitas.models import DetalheTipoReceita, TipoReceita
from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe,
    PermissaoAPITodosComLeituraOuGravacao
)

logger = logging.getLogger(__name__)


class DetalheTipoReceitaParametrizacaoViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         GenericViewSet):
    lookup_field = 'uuid'
    queryset = DetalheTipoReceita.objects.all().order_by('-nome')
    serializer_class = DetalheTipoReceitaParametrizacaoSerializer
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    pagination_class = CustomPagination

    def get_queryset(self):
        nome = self.request.query_params.get('nome')
        recurso_uuid = self.request.query_params.get('recurso_uuid')

        qs = DetalheTipoReceita.objects.all().order_by('nome')

        if nome:
            qs = qs.filter(nome__icontains=nome)

        if recurso_uuid:
            try:
                recurso = Recurso.objects.get(uuid=recurso_uuid)
                qs = DetalheTipoReceita.filter_by_recurso(qs, recurso)
            except Recurso.DoesNotExist:
                raise NotFound({"mensagem": "Recurso não encontrado."})
            except ValidationError:
                raise DRFValidationError({"mensagem": "UUID de recurso inválido."})
            except Exception:
                raise DRFValidationError({"mensagem": "Erro ao processar a solicitação."})

        return qs


    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.receitas.exists():
            content = {
                'mensagem': (
                    'Essa operação não pode ser realizada. '
                    'Há receitas associadas a esse detalhe de tipo de crédito.'
                )
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)


    @action(detail=False, url_path='tipo_receita_possui_detalhamento', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def tipo_receita_possui_detalhamento(self, tipo_receita):
        recurso = self.request.query_params.get('recurso_uuid')

        qs = TipoReceita.objects.filter(possui_detalhamento=True)

        if recurso:
            try:
                recurso_obj = Recurso.objects.get(uuid=recurso)
                qs = TipoReceita.filter_by_recurso(qs, recurso_obj)
            except Recurso.DoesNotExist:
                raise NotFound({"mensagem": "Recurso não encontrado."})
            except ValidationError:
                raise DRFValidationError({"mensagem": "UUID de recurso inválido."})

        return Response(TipoReceitaListaSerializer(qs, many=True).data, status=status.HTTP_200_OK)
