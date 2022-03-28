from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ...models import MotivoEstorno
from ..serializers import MotivoEstornoSerializer


class MotivosEstornoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = MotivoEstorno.objects.all().order_by('motivo')
    serializer_class = MotivoEstornoSerializer

