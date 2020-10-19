from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from sme_ptrf_apps.core.api.serializers import ComentarioAnalisePrestacaoRetrieveSerializer
from sme_ptrf_apps.core.models import ComentarioAnalisePrestacao


class ComentariosAnalisesPrestacoesViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    permission_classes = [AllowAny]
    serializer_class = ComentarioAnalisePrestacaoRetrieveSerializer
    queryset = ComentarioAnalisePrestacao.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('prestacao_conta__uuid',)
