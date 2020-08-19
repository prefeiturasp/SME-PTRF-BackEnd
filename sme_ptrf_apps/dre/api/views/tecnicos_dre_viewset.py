from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from ..serializers.tecnico_dre_serializer import TecnicoDreSerializer, TecnicoDreCreateSerializer
from ...models import TecnicoDre


class TecnicosDreViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = TecnicoDre.objects.all()
    serializer_class = TecnicoDreSerializer

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return TecnicoDreSerializer
        else:
            return TecnicoDreCreateSerializer
