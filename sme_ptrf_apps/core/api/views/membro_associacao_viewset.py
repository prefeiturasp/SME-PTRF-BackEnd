from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.api.serializers import MembroAssociacaoCreateSerializer, MembroAssociacaoListSerializer
from sme_ptrf_apps.core.models import MembroAssociacao


class MembroAssociacaoViewSet(mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.DestroyModelMixin,
                              GenericViewSet):

    lookup_field = 'uuid'
    permission_classes = [AllowAny]
    serializer_class = MembroAssociacaoListSerializer
    queryset = MembroAssociacao.objects.all()

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return MembroAssociacaoListSerializer
        else:
            return MembroAssociacaoCreateSerializer
