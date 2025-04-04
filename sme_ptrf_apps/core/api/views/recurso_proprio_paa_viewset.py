from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from django.db.models import Sum
import django_filters
from waffle.mixins import WaffleFlagMixin

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.core.models import RecursoProprioPaa
from sme_ptrf_apps.core.api.serializers import RecursoProprioPaaCreateSerializer, RecursoProprioPaaListSerializer


class RecursoProprioPaaViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = RecursoProprioPaa.objects.all()
    serializer_class = RecursoProprioPaaListSerializer
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return RecursoProprioPaaListSerializer
        else:
            return RecursoProprioPaaCreateSerializer

    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError
        obj = self.get_object()
        try:
            self.perform_destroy(obj)
        except ProtectedError:
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Essa operação não pode ser realizada. Há dados vinculados a esse Recuro'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='total',
            permission_classes=[IsAuthenticated])
    def total_recursos(self, request, *args, **kwrgs):
        valor_total = RecursoProprioPaa.objects.aggregate(total=Sum('valor'))
        return Response({
            'total': valor_total['total']
        }, status=status.HTTP_200_OK)
