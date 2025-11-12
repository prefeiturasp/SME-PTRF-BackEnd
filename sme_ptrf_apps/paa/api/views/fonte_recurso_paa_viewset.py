from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from waffle.mixins import WaffleFlagMixin

from ...models import FonteRecursoPaa
from ..serializers.fonte_recurso_paa_serializer import FonteRecursoPaaSerializer


class FonteRecursoPaaViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = FonteRecursoPaa.objects.all()
    serializer_class = FonteRecursoPaaSerializer
    http_method_names = ['get', 'post', 'patch']
