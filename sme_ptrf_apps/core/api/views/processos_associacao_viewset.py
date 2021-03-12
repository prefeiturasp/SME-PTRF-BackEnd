from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.api.serializers import ProcessoAssociacaoCreateSerializer, ProcessoAssociacaoRetrieveSerializer
from sme_ptrf_apps.core.models import ProcessoAssociacao
from sme_ptrf_apps.users.permissoes import PermissaoApiDre


class ProcessosAssociacaoViewSet(mixins.RetrieveModelMixin,
                                 mixins.CreateModelMixin,
                                 mixins.UpdateModelMixin,
                                 mixins.DestroyModelMixin,
                                 GenericViewSet):
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    serializer_class = ProcessoAssociacaoRetrieveSerializer
    queryset = ProcessoAssociacao.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProcessoAssociacaoRetrieveSerializer
        else:
            return ProcessoAssociacaoCreateSerializer
