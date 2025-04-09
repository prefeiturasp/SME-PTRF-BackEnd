from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

import django_filters
from waffle.mixins import WaffleFlagMixin

from ...models import FonteRecursoPaa
from ..serializers import FonteRecursoPaaSerializer


class FonteRecursoPaaViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = FonteRecursoPaa.objects.all()
    serializer_class = FonteRecursoPaaSerializer
    http_method_names = ['get', 'post', 'patch']
