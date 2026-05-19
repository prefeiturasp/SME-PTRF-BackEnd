from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from sme_ptrf_apps.core.models.recurso import Recurso
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination

from ...models import MotivoReprovacao

from ..serializers.motivo_reprovacao_serializer import MotivoReprovacaoParametrizacaoSerializer, MotivoReprovacaoSerializer


class MotivoReprovacaoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = MotivoReprovacao.objects.all().order_by('motivo')
    serializer_class = MotivoReprovacaoSerializer

    def get_queryset(self):
        recurso_uuid = self.request.query_params.get('recurso_uuid')

        filters = Q()
        if recurso_uuid:
            recurso = Recurso.objects.filter(uuid=recurso_uuid).first() or None
            if recurso:
                filters &= Q(recurso=recurso)

        return MotivoReprovacao.objects.filter(filters)


class MotivoReprovacaoParametrizacaoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = MotivoReprovacao.objects.all().order_by('motivo')
    serializer_class = MotivoReprovacaoParametrizacaoSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        motivo = self.request.query_params.get('motivo')
        recurso_uuid = self.request.query_params.get('recurso_uuid')

        filters = Q()
        if motivo:
            filters &= Q(motivo__icontains=motivo)

        if recurso_uuid:
            recurso = Recurso.objects.filter(uuid=recurso_uuid).first() or None
            if recurso:
                filters &= Q(recurso__uuid=recurso_uuid)

        return MotivoReprovacao.objects.filter(filters)


    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.prestacaoconta_set.exists():
            content = {
                'mensagem': (
                    'Essa operação não pode ser realizada. '
                    'Há PCs com análise concluída com esse motivo de reprovação de PC.'
                )
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)
