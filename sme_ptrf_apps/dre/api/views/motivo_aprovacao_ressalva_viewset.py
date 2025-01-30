from django.db.models import Q
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ...models import MotivoAprovacaoRessalva

from ..serializers.motivo_aprovacao_ressalva_serializer import MotivoAprovacaoRessalvaSerializer
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination


class MotivoAprovacaoRessalvaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = MotivoAprovacaoRessalva.objects.all().order_by('motivo')
    serializer_class = MotivoAprovacaoRessalvaSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        motivo = self.request.query_params.get('motivo')

        filters = Q()
        if motivo:
            filters &= Q(motivo__icontains=motivo)

        return MotivoAprovacaoRessalva.objects.filter(filters)


    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError
        obj = self.get_object()
        try:
            self.perform_destroy(obj)
        except ProtectedError:
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Essa operação não pode ser realizada. Há dados vinculados a esse motivo de aprovação com ressalva'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)