from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from ...models import MotivoAprovacaoRessalva

from ..serializers.motivo_aprovacao_ressalva_serializer import (
    MotivoAprovacaoRessalvaSerializer,
    MotivoAprovacaoRessalvaParametrizacaoSerializer
)
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination


class MotivoAprovacaoRessalvaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = MotivoAprovacaoRessalva.objects.all().order_by('motivo')
    serializer_class = MotivoAprovacaoRessalvaSerializer


class MotivoAprovacaoRessalvaParametrizacaoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = MotivoAprovacaoRessalva.objects.all().order_by('motivo')
    serializer_class = MotivoAprovacaoRessalvaParametrizacaoSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        motivo = self.request.query_params.get('motivo')

        filters = Q()
        if motivo:
            filters &= Q(motivo__icontains=motivo)

        return MotivoAprovacaoRessalva.objects.filter(filters)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='motivo', description='Descrição do Motivo', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: MotivoAprovacaoRessalvaParametrizacaoSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.prestacaoconta_set.exists():
            content = {
                'mensagem': (
                    'Essa operação não pode ser realizada. '
                    'Há PCs com análise concluída com esse motivo de aprovação de PC com ressalvas.'
                )
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)
