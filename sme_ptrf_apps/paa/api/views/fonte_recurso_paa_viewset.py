from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema_view

from waffle.mixins import WaffleFlagMixin

from sme_ptrf_apps.paa.api.views.docs.fonte_recurso_paa_docs import DOCS

from ...models import FonteRecursoPaa
from ..serializers.fonte_recurso_paa_serializer import FonteRecursoPaaSerializer


@extend_schema_view(**DOCS)
class FonteRecursoPaaViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = FonteRecursoPaa.objects.all()
    serializer_class = FonteRecursoPaaSerializer
    http_method_names = ['get', 'post', 'patch']
