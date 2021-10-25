from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ...models import MotivoReprovacao

from ..serializers.motivo_reprovacao_serializer import MotivoReprovacaoSerializer


class MotivoReprovacaoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = MotivoReprovacao.objects.all().order_by('motivo')
    serializer_class = MotivoReprovacaoSerializer
