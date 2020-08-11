from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from ..serializers import UnidadeSerializer
from ...models import Unidade


class UnidadesViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = Unidade.objects.all()
    serializer_class = UnidadeSerializer
