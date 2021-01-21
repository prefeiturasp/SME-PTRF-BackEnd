from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from sme_ptrf_apps.core.api.serializers import ArquivoSerializer
from sme_ptrf_apps.core.models import Arquivo


class ArquivoViewSet(ModelViewSet):
    # permission_classes = [IsAuthenticated]
    lookup_field = "uuid"
    queryset = Arquivo.objects.all().order_by('-criado_em')
    serializer_class = ArquivoSerializer
