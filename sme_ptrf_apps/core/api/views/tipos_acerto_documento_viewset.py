from django_filters import rest_framework as filters

from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from ..serializers.tipo_acerto_documento_serializer import TipoAcertoDocumentoSerializer
from ...models import TipoAcertoDocumento
from sme_ptrf_apps.users.permissoes import PermissaoApiUe


class TiposAcertoDocumentoViewSet(mixins.ListModelMixin,
                                  mixins.RetrieveModelMixin,
                                  GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = TipoAcertoDocumento.objects.all()
    serializer_class = TipoAcertoDocumentoSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('tipos_documento_prestacao__uuid',)
