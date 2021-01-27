from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ...models import MotivoAprovacaoRessalva

from ..serializers.motivo_aprovacao_ressalva_serializer import MotivoAprovacaoRessalvaSerializer


class MotivoAprovacaoRessalvaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = MotivoAprovacaoRessalva.objects.all().order_by('motivo')
    serializer_class = MotivoAprovacaoRessalvaSerializer
