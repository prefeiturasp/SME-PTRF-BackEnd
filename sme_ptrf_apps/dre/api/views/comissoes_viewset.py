from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ...models import Comissao

from ..serializers.comissao_serializer import ComissaoSerializer


class ComissoesViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = Comissao.objects.all()
    serializer_class = ComissaoSerializer
