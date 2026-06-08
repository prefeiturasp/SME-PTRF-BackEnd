from django.db.models import Q
from uuid import UUID

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError

from sme_ptrf_apps.core.models.recurso import Recurso
from ...models import Comissao

from ..serializers.comissao_serializer import ComissaoSerializer, ComissaoParametrizacaoSerializer

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiDre,
)


class ComissoesViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    lookup_field = 'uuid'
    queryset = Comissao.objects.all()
    serializer_class = ComissaoSerializer


class ComissoesParametrizacaoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    lookup_field = 'uuid'
    queryset = Comissao.objects.all()
    serializer_class = ComissaoParametrizacaoSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        comissoes_uuid = self.request.query_params.get('comissoes_uuid', "")
        recursos_uuid = self.request.query_params.get('recursos_uuid', "")
        responsavel_analise_pc = self.request.query_params.get('responsavel_analise_pc', False)

        filters = Q()
        if comissoes_uuid:
            try:
                comissoes_uuid = [UUID(id_) for id_ in comissoes_uuid.split(',')]
            except ValueError:
                raise DRFValidationError({
                    "non_field_errors": "Por favor, forneça UUIDs de comissões válidos, separados por vírgula."
                })

            filters &= Q(uuid__in=comissoes_uuid)

        if responsavel_analise_pc:
            filters &= Q(responsavel_analise_pc=True)

        if recursos_uuid:
            try:
                recursos_uuid = [UUID(id_) for id_ in recursos_uuid.split(',')]
            except ValueError:
                raise DRFValidationError({
                    "non_field_errors": "Por favor, forneça UUIDs de recursos válidos, separados por vírgula."
                })

            recursos = Recurso.objects.filter(uuid__in=recursos_uuid).values_list('uuid', flat=True)
            if recursos:
                filters &= Q(recursos__uuid__in=recursos)

        return Comissao.objects.filter(filters).order_by('nome').distinct()


    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.membros.exists():
            content = {
                'mensagem': (
                    'Essa operação não pode ser realizada.'
                    'Há membros associados a esta comissão. Remova os membros antes de excluir a comissão.'
                )
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)
