from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from ..serializers.ambiente_serializer import AmbienteSerializer
from ...models import Ambiente


class AmbientesViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Ambiente.objects.all()
    serializer_class = AmbienteSerializer
