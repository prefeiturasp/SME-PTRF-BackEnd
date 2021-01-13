from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.api.serializers import AcaoAssociacaoCreateSerializer, AcaoAssociacaoRetrieveSerializer
from sme_ptrf_apps.core.models import AcaoAssociacao
from sme_ptrf_apps.users.permissoes import PermissaoAssociacao


class AcaoAssociacaoViewSet(mixins.RetrieveModelMixin,
                            mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.ListModelMixin,
                            GenericViewSet):
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticated & PermissaoAssociacao]
    serializer_class = AcaoAssociacaoRetrieveSerializer
    queryset = AcaoAssociacao.objects.all().order_by('associacao__nome', 'acao__nome')

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return AcaoAssociacaoRetrieveSerializer
        else:
            return AcaoAssociacaoCreateSerializer
